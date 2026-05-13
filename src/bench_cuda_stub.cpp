// Stub used when CUDA is not enabled at build time. Symbols defined here
// match those in src/bench_cuda.cu so that main.cpp can call into the API
// unconditionally and degrade gracefully at runtime.

#include "bench_cuda.hpp"

#if !FTOQC_HAS_CUDA

namespace bench_cuda {

bool is_compiled_with_cuda() {
    return false;
}

bool init(int /*n_workers*/, std::string &error_out) {
    error_out = "CUDA support was not compiled into this binary";
    return false;
}

void shutdown() {}

bool run_worker_marker(int /*worker_id*/, std::string &error_out) {
    error_out = "CUDA support was not compiled into this binary";
    return false;
}

int active_worker_count() {
    return 0;
}

} // namespace bench_cuda

#endif
