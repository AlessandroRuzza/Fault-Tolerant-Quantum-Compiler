#pragma once

#include <cstddef>
#include <string>

#ifndef FTOQC_HAS_CUDA
#define FTOQC_HAS_CUDA 0
#endif

namespace bench_cuda {

bool is_compiled_with_cuda();

bool init(int n_workers, std::string &error_out);

void shutdown();

// Per-worker marker: launches a tiny kernel on the worker's stream and
// synchronizes. Returns true on success. On failure (driver/runtime
// problem) sets error_out and returns false.
bool run_worker_marker(int worker_id, std::string &error_out);

int active_worker_count();

} // namespace bench_cuda
