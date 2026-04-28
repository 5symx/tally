#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <map>

namespace server_fr3_internal {

enum class WindowOpType {
    MemcpyAsync,
    MemsetAsync,
    StreamSynchronize,
};

uint64_t client_switch_timeslice_ms();
void record_client_switch_for_timeslice(int32_t mapped_id, int32_t client_id);
void clear_client_switch_for_timeslice(int32_t mapped_id);
bool should_switch_client_for_timeslice(int32_t mapped_id, int32_t active_client_id, int32_t request_client_id);

void wait_for_init_flag(std::map<int32_t, std::atomic<bool>>& flags, int32_t mapped_id,
                        const char* flag_name, const char* waiter_name, int64_t timeout_ms = 60000);

bool metadata_marks_window_reusable(int32_t window_id);
int32_t open_malloc_window(int32_t mapped_id, int32_t client_id);
int32_t open_replay_window_for_client(int32_t mapped_id, int32_t client_id);
void reset_replay_window_cursor(int32_t mapped_id, int32_t client_id);
void set_window_reusable(int32_t mapped_id, int32_t window_id, bool reusable);
bool is_window_reusable(int32_t mapped_id, int32_t window_id);
bool should_bypass_for_current_window(int32_t mapped_id, int32_t client_id);
void attribute_op_to_current_window(int32_t mapped_id, int32_t client_id, WindowOpType op_type);
uint64_t reserve_h2d_index_for_current_window(int32_t mapped_id, int32_t client_id, bool replay_mode);
void record_profile_h2d_hash_for_current_window_at_index(int32_t mapped_id, int32_t client_id,
                                                         uint64_t h2d_op_index, uint64_t hash);
bool verify_replay_h2d_hash_for_current_window_at_index(int32_t mapped_id, int32_t client_id,
                                                        uint64_t h2d_op_index, uint64_t observed_hash,
                                                        uint64_t* expected_hash);
int32_t get_current_window_for_client(int32_t mapped_id, int32_t client_id);
void set_replay_allocation_id_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id,
                                         size_t allocation_id);
size_t get_replay_allocation_id_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id);
void record_latest_malloc_size_for_current_window(int32_t mapped_id, int32_t client_id, size_t malloc_size);
size_t get_latest_malloc_size_for_window(int32_t mapped_id, int32_t client_id, int32_t window_id);
void mark_current_window_replay_invalid(int32_t mapped_id, int32_t client_id);
bool is_current_window_replay_invalid(int32_t mapped_id, int32_t client_id);

}  // namespace server_fr3_internal
