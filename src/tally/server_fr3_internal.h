#pragma once

#include <atomic>
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
                        const char* flag_name, const char* waiter_name);

bool metadata_marks_window_reusable(int32_t window_id);
int32_t open_malloc_window(int32_t mapped_id, int32_t client_id);
int32_t open_replay_window_for_client(int32_t mapped_id, int32_t client_id);
void reset_replay_window_cursor(int32_t mapped_id, int32_t client_id);
void set_window_reusable(int32_t mapped_id, int32_t window_id, bool reusable);
bool is_window_reusable(int32_t mapped_id, int32_t window_id);
bool should_bypass_for_current_window(int32_t mapped_id, int32_t client_id);
void attribute_op_to_current_window(int32_t mapped_id, int32_t client_id, WindowOpType op_type);

}  // namespace server_fr3_internal
