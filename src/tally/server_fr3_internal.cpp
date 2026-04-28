#include "server_fr3_internal.h"

#include <chrono>
#include <cstdlib>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <tally/log.h>

namespace server_fr3_internal {

struct MallocWindowState {
    int32_t malloc_count = 0;
    int32_t current_window_id = -1;
    std::unordered_map<int32_t, int32_t> current_window_id_by_client;
    std::unordered_map<int32_t, bool> reusable_by_window_id;
    std::unordered_map<int32_t, int32_t> replay_next_window_by_client;
    std::unordered_map<int32_t, uint64_t> memcpy_async_count_by_window_id;
    std::unordered_map<int32_t, uint64_t> memset_async_count_by_window_id;
    std::unordered_map<int32_t, uint64_t> stream_sync_count_by_window_id;
    std::unordered_map<int32_t, std::vector<uint64_t>> profiled_h2d_hashes_by_window_id;
    std::unordered_map<int32_t, uint64_t> profile_h2d_cursor_by_window_id;
    std::unordered_map<uint64_t, uint64_t> replay_h2d_cursor_by_client_window_key;
    std::unordered_map<int32_t, bool> replay_invalid_by_window_id;
    std::unordered_map<uint64_t, size_t> replay_allocation_id_by_client_window_key;
    std::unordered_map<uint64_t, size_t> latest_malloc_size_by_client_window_key;
};

std::mutex malloc_window_state_mutex;
std::unordered_map<int32_t, MallocWindowState> malloc_window_state_by_mapped_id;

uint64_t make_client_window_key(int32_t client_id, int32_t window_id)
{
    return (static_cast<uint64_t>(static_cast<uint32_t>(client_id)) << 32) |
           static_cast<uint32_t>(window_id);
}

size_t make_default_replay_allocation_id(int32_t mapped_id, int32_t window_id)
{
    if (window_id <= 0) {
        return 0;
    }

    return (static_cast<uint64_t>(static_cast<uint32_t>(mapped_id)) << 32) |
           static_cast<uint32_t>(window_id);
}

struct ClientSwitchSliceState {
    int32_t slice_owner_client_id = -1;
    std::chrono::steady_clock::time_point slice_started_at = std::chrono::steady_clock::now();
};

std::mutex client_switch_slice_mutex;
std::unordered_map<int32_t, ClientSwitchSliceState> client_switch_slice_by_mapped_id;

uint64_t client_switch_timeslice_ms()
{
    static const uint64_t kDefaultTimesliceMs = 50;
    static const uint64_t parsed_value = []() -> uint64_t {
        if (const char* env = std::getenv("TALLY_CLIENT_SWITCH_TIMESLICE_MS")) {
            try {
                const auto parsed = std::stoll(env);
                if (parsed > 0) {
                    return static_cast<uint64_t>(parsed);
                }
            } catch (...) {
                // Ignore malformed env values and use default.
            }
        }
        return kDefaultTimesliceMs;
    }();
    return parsed_value;
}

void record_client_switch_for_timeslice(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(client_switch_slice_mutex);
    auto& state = client_switch_slice_by_mapped_id[mapped_id];
    state.slice_owner_client_id = client_id;
    state.slice_started_at = std::chrono::steady_clock::now();
}

void clear_client_switch_for_timeslice(int32_t mapped_id)
{
    std::lock_guard<std::mutex> lock(client_switch_slice_mutex);
    auto& state = client_switch_slice_by_mapped_id[mapped_id];
    state.slice_owner_client_id = -1;
    state.slice_started_at = std::chrono::steady_clock::now();
}

bool should_switch_client_for_timeslice(int32_t mapped_id, int32_t active_client_id, int32_t request_client_id)
{
    if (active_client_id == request_client_id) {
        return false;
    }

    // No active owner means we should always accept the requester.
    if (active_client_id == -1) {
        return true;
    }

    const auto now = std::chrono::steady_clock::now();
    std::lock_guard<std::mutex> lock(client_switch_slice_mutex);
    auto& state = client_switch_slice_by_mapped_id[mapped_id];

    if (state.slice_owner_client_id != active_client_id) {
        state.slice_owner_client_id = active_client_id;
        state.slice_started_at = now;
    }

    const auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now - state.slice_started_at).count();
    if (elapsed_ms < static_cast<int64_t>(client_switch_timeslice_ms())) {
        return false;
    }

    state.slice_owner_client_id = request_client_id;
    state.slice_started_at = now;
    return true;
}

void wait_for_init_flag(std::map<int32_t, std::atomic<bool>>& flags, int32_t mapped_id,
                        const char* flag_name, const char* waiter_name, int64_t timeout_ms)
{
    auto it = flags.find(mapped_id);
    if (it == flags.end()) {
        TALLY_SPD_WARN(std::string(waiter_name) + " cannot wait for " + flag_name +
            " because mapped_id " + std::to_string(mapped_id) + " is missing");
        return;
    }

    constexpr int64_t kSleepMs = 1;
    constexpr int64_t kLogIntervalMs = 1000;
    int64_t waited_ms = 0;
    while (!it->second.load(std::memory_order_acquire)) {
        if (timeout_ms >= 0 && waited_ms >= timeout_ms) {
            TALLY_SPD_WARN(std::string(waiter_name) + " timed out waiting for " + flag_name +
                " on mapped_id " + std::to_string(mapped_id) +
                " after " + std::to_string(waited_ms) + " ms");
            return;
        }

        if (waited_ms > 0 && (waited_ms % kLogIntervalMs) == 0) {
            TALLY_SPD_LOG_ALWAYS(std::string(waiter_name) + " still waiting for " + flag_name +
                " on mapped_id " + std::to_string(mapped_id) +
                " after " + std::to_string(waited_ms) + " ms");
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(kSleepMs));
        waited_ms += kSleepMs;
    }

    if (waited_ms > 0) {
        TALLY_SPD_LOG_ALWAYS(std::string(waiter_name) + " passed " + flag_name +
            " gate on mapped_id " + std::to_string(mapped_id) +
            " after waiting " + std::to_string(waited_ms) + " ms");
    }
}

bool metadata_marks_window_reusable(int32_t window_id)
{
    static bool parsed = false;
    static bool reusable_all_windows = false;
    static std::unordered_set<int32_t> reusable_window_ids;

    if (!parsed) {
        parsed = true;
        if (const char* env = std::getenv("TALLY_REUSABLE_WINDOWS")) {
            std::string raw(env);

            TALLY_SPD_LOG("TALLY_REUSABLE_WINDOWS is  " + raw);

            if (raw == "all" || raw == "ALL" || raw == "*") {
                reusable_all_windows = true;
            } else {
                std::stringstream ss(raw);
                std::string token;
                while (std::getline(ss, token, ',')) {
                    try {
                        reusable_window_ids.insert(std::stoi(token));
                    } catch (...) {
                        // Ignore malformed tokens and keep other valid window IDs.
                    }
                }
            }
        }
    }

    return reusable_all_windows || reusable_window_ids.find(window_id) != reusable_window_ids.end();
}

int32_t open_malloc_window(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto& state = malloc_window_state_by_mapped_id[mapped_id];

    if (state.current_window_id != -1) {
        TALLY_SPD_LOG("Closing malloc window " + std::to_string(state.current_window_id) +
            " for mapped_id " + std::to_string(mapped_id));
    }

    state.malloc_count += 1;
    state.current_window_id = state.malloc_count;
    state.current_window_id_by_client[client_id] = state.current_window_id;
    state.reusable_by_window_id[state.current_window_id] = false;
    state.replay_invalid_by_window_id[state.current_window_id] = false;
    state.profiled_h2d_hashes_by_window_id[state.current_window_id].clear();
    state.profile_h2d_cursor_by_window_id[state.current_window_id] = 0;
    state.replay_h2d_cursor_by_client_window_key.erase(make_client_window_key(client_id, state.current_window_id));

    TALLY_SPD_LOG("Opening malloc window " + std::to_string(state.current_window_id) +
        " for mapped_id " + std::to_string(mapped_id) + " for client_id " + std::to_string(client_id));

    return state.current_window_id;
}

int32_t open_replay_window_for_client(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto& state = malloc_window_state_by_mapped_id[mapped_id];
    auto& replay_next = state.replay_next_window_by_client[client_id];

    if (replay_next <= 0) {
        replay_next = 1;
    }

    if (state.current_window_id != -1) {
        TALLY_SPD_LOG("Closing malloc window " + std::to_string(state.current_window_id) +
            " for mapped_id " + std::to_string(mapped_id) + " (replay)");
    }

    state.current_window_id = replay_next;
    state.current_window_id_by_client[client_id] = state.current_window_id;
    state.replay_h2d_cursor_by_client_window_key[make_client_window_key(client_id, state.current_window_id)] = 0;
    TALLY_SPD_LOG("Opening malloc window " + std::to_string(state.current_window_id) +
        " for mapped_id " + std::to_string(mapped_id) + " (replay)");
    replay_next += 1;

    return state.current_window_id;
}

void reset_replay_window_cursor(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto& state = malloc_window_state_by_mapped_id[mapped_id];
    auto it = state.replay_next_window_by_client.find(client_id);
    if (it == state.replay_next_window_by_client.end() || it->second <= 0) {
        state.replay_next_window_by_client[client_id] = 1;
    }
}

void set_window_reusable(int32_t mapped_id, int32_t window_id, bool reusable)
{
    if (window_id <= 0) {
        return;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto& state = malloc_window_state_by_mapped_id[mapped_id];
    state.reusable_by_window_id[window_id] = reusable;
}

bool is_window_reusable(int32_t mapped_id, int32_t window_id)
{
    if (window_id <= 0) {
        return false;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return false;
    }

    auto reusable_it = state_it->second.reusable_by_window_id.find(window_id);
    if (reusable_it == state_it->second.reusable_by_window_id.end()) {
        return false;
    }

    return reusable_it->second;
}

bool should_bypass_for_current_window(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return false;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return false;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return false;
    }

    auto invalid_it = state_it->second.replay_invalid_by_window_id.find(window_id);
    if (invalid_it != state_it->second.replay_invalid_by_window_id.end() && invalid_it->second) {
        return false;
    }

    auto reusable_it = state_it->second.reusable_by_window_id.find(window_id);
    return reusable_it != state_it->second.reusable_by_window_id.end() && reusable_it->second;
}

void attribute_op_to_current_window(int32_t mapped_id, int32_t client_id, WindowOpType op_type)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return;
    }

    switch (op_type) {
    case WindowOpType::MemcpyAsync:
        state_it->second.memcpy_async_count_by_window_id[window_id] += 1;
        break;
    case WindowOpType::MemsetAsync:
        state_it->second.memset_async_count_by_window_id[window_id] += 1;
        break;
    case WindowOpType::StreamSynchronize:
        state_it->second.stream_sync_count_by_window_id[window_id] += 1;
        break;
    }
}

uint64_t reserve_h2d_index_for_current_window(int32_t mapped_id, int32_t client_id, bool replay_mode)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return 0;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return 0;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return 0;
    }

    if (replay_mode) {
        const uint64_t key = make_client_window_key(client_id, window_id);
        uint64_t& cursor = state_it->second.replay_h2d_cursor_by_client_window_key[key];
        const uint64_t index = cursor;
        cursor += 1;
        return index;
    }

    uint64_t& cursor = state_it->second.profile_h2d_cursor_by_window_id[window_id];
    const uint64_t index = cursor;
    cursor += 1;
    return index;
}

void record_profile_h2d_hash_for_current_window_at_index(int32_t mapped_id, int32_t client_id,
                                                         uint64_t h2d_op_index, uint64_t hash)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return;
    }

    auto& profiled_hashes = state_it->second.profiled_h2d_hashes_by_window_id[window_id];
    if (profiled_hashes.size() <= h2d_op_index) {
        profiled_hashes.resize(static_cast<size_t>(h2d_op_index + 1), 0);
    }
    profiled_hashes[static_cast<size_t>(h2d_op_index)] = hash;
}

bool verify_replay_h2d_hash_for_current_window_at_index(int32_t mapped_id, int32_t client_id,
                                                        uint64_t h2d_op_index, uint64_t observed_hash,
                                                        uint64_t* expected_hash)
{
    if (expected_hash != nullptr) {
        *expected_hash = 0;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return false;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return false;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return false;
    }

    auto invalid_it = state_it->second.replay_invalid_by_window_id.find(window_id);
    if (invalid_it != state_it->second.replay_invalid_by_window_id.end() && invalid_it->second) {
        return false;
    }

    auto profiled_it = state_it->second.profiled_h2d_hashes_by_window_id.find(window_id);
    if (profiled_it == state_it->second.profiled_h2d_hashes_by_window_id.end()) {
        state_it->second.replay_invalid_by_window_id[window_id] = true;
        return false;
    }

    const auto& profiled_hashes = profiled_it->second;
    if (h2d_op_index >= profiled_hashes.size()) {
        state_it->second.replay_invalid_by_window_id[window_id] = true;
        return false;
    }

    const uint64_t expected = profiled_hashes[static_cast<size_t>(h2d_op_index)];
    if (expected_hash != nullptr) {
        *expected_hash = expected;
    }

    if (observed_hash != expected) {
        state_it->second.replay_invalid_by_window_id[window_id] = true;
        return false;
    }

    return true;
}

int32_t get_current_window_for_client(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return -1;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return -1;
    }

    return current_window_it->second;
}

void set_replay_allocation_id_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id,
                                         size_t allocation_id)
{
    if (window_id <= 0 || allocation_id == static_cast<size_t>(-1)) {
        return;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return;
    }

    state_it->second.replay_allocation_id_by_client_window_key[make_client_window_key(client_id, window_id)] =
        allocation_id;
}

size_t get_replay_allocation_id_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id)
{
    if (window_id <= 0) {
        return 0;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return make_default_replay_allocation_id(mapped_id, window_id);
    }

    const uint64_t key = make_client_window_key(client_id, window_id);
    auto alloc_it = state_it->second.replay_allocation_id_by_client_window_key.find(key);
    if (alloc_it == state_it->second.replay_allocation_id_by_client_window_key.end()) {
        return make_default_replay_allocation_id(mapped_id, window_id);
    }

    return alloc_it->second;
}

void record_latest_malloc_size_for_current_window(int32_t mapped_id, int32_t client_id, size_t malloc_size)
{
    if (malloc_size == 0) {
        return;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return;
    }

    state_it->second.latest_malloc_size_by_client_window_key[make_client_window_key(client_id, window_id)] =
        malloc_size;
}

size_t get_latest_malloc_size_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id)
{
    if (window_id <= 0) {
        return 0;
    }

    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return 0;
    }

    auto it = state_it->second.latest_malloc_size_by_client_window_key.find(
        make_client_window_key(client_id, window_id));
    if (it == state_it->second.latest_malloc_size_by_client_window_key.end()) {
        return 0;
    }

    return it->second;
}

void mark_current_window_replay_invalid(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return;
    }

    state_it->second.replay_invalid_by_window_id[window_id] = true;
}

bool is_current_window_replay_invalid(int32_t mapped_id, int32_t client_id)
{
    std::lock_guard<std::mutex> lock(malloc_window_state_mutex);
    auto state_it = malloc_window_state_by_mapped_id.find(mapped_id);
    if (state_it == malloc_window_state_by_mapped_id.end()) {
        return false;
    }

    auto current_window_it = state_it->second.current_window_id_by_client.find(client_id);
    if (current_window_it == state_it->second.current_window_id_by_client.end()) {
        return false;
    }

    int32_t window_id = current_window_it->second;
    if (window_id <= 0) {
        return false;
    }

    auto invalid_it = state_it->second.replay_invalid_by_window_id.find(window_id);
    if (invalid_it == state_it->second.replay_invalid_by_window_id.end()) {
        return false;
    }

    return invalid_it->second;
}

}  // namespace server_fr3_internal
