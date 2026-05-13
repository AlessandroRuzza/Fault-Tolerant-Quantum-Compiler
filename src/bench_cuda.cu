#include "bench_cuda.hpp"

#if FTOQC_HAS_CUDA

#include <cstdio>
#include <mutex>
#include <vector>

#include <cuda_runtime.h>

namespace bench_cuda {

namespace {

struct WorkerSlot {
    cudaStream_t stream = nullptr;
    int *device_buf = nullptr;
    int *host_buf = nullptr;
};

std::mutex g_mutex;
std::vector<WorkerSlot> g_workers;
bool g_initialized = false;

bool set_error(std::string &out, const char *prefix, cudaError_t err) {
    out = std::string(prefix) + ": " + cudaGetErrorString(err);
    return false;
}

__global__ void worker_marker_kernel(int *out, int worker_id, int n) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        // Trivial but real device work: write worker_id with an arithmetic op
        // so the kernel is not optimized away.
        out[idx] = worker_id * 2 + idx;
    }
}

} // namespace

bool is_compiled_with_cuda() {
    return true;
}

bool init(int n_workers, std::string &error_out) {
    std::lock_guard<std::mutex> lock(g_mutex);
    if (g_initialized) {
        error_out = "bench_cuda already initialized";
        return false;
    }
    if (n_workers <= 0) {
        error_out = "n_workers must be > 0";
        return false;
    }

    int device_count = 0;
    cudaError_t err = cudaGetDeviceCount(&device_count);
    if (err != cudaSuccess) {
        return set_error(error_out, "cudaGetDeviceCount", err);
    }
    if (device_count == 0) {
        error_out = "no CUDA-capable device detected";
        return false;
    }

    err = cudaSetDevice(0);
    if (err != cudaSuccess) {
        return set_error(error_out, "cudaSetDevice", err);
    }

    g_workers.assign(static_cast<size_t>(n_workers), WorkerSlot{});
    constexpr int kBufLen = 64;
    for (int i = 0; i < n_workers; ++i) {
        WorkerSlot &slot = g_workers[static_cast<size_t>(i)];
        err = cudaStreamCreate(&slot.stream);
        if (err != cudaSuccess) {
            shutdown();
            return set_error(error_out, "cudaStreamCreate", err);
        }
        err = cudaMalloc(reinterpret_cast<void **>(&slot.device_buf),
                         sizeof(int) * kBufLen);
        if (err != cudaSuccess) {
            shutdown();
            return set_error(error_out, "cudaMalloc", err);
        }
        err = cudaMallocHost(reinterpret_cast<void **>(&slot.host_buf),
                             sizeof(int) * kBufLen);
        if (err != cudaSuccess) {
            shutdown();
            return set_error(error_out, "cudaMallocHost", err);
        }
    }

    g_initialized = true;
    return true;
}

void shutdown() {
    std::lock_guard<std::mutex> lock(g_mutex);
    for (WorkerSlot &slot : g_workers) {
        if (slot.device_buf != nullptr) {
            cudaFree(slot.device_buf);
            slot.device_buf = nullptr;
        }
        if (slot.host_buf != nullptr) {
            cudaFreeHost(slot.host_buf);
            slot.host_buf = nullptr;
        }
        if (slot.stream != nullptr) {
            cudaStreamDestroy(slot.stream);
            slot.stream = nullptr;
        }
    }
    g_workers.clear();
    g_initialized = false;
}

bool run_worker_marker(int worker_id, std::string &error_out) {
    cudaStream_t stream = nullptr;
    int *device_buf = nullptr;
    int *host_buf = nullptr;
    {
        std::lock_guard<std::mutex> lock(g_mutex);
        if (!g_initialized) {
            error_out = "bench_cuda not initialized";
            return false;
        }
        if (worker_id < 0 || worker_id >= static_cast<int>(g_workers.size())) {
            error_out = "worker_id out of range";
            return false;
        }
        WorkerSlot &slot = g_workers[static_cast<size_t>(worker_id)];
        stream = slot.stream;
        device_buf = slot.device_buf;
        host_buf = slot.host_buf;
    }

    constexpr int kBufLen = 64;
    constexpr int kBlockSize = 32;
    const int grid = (kBufLen + kBlockSize - 1) / kBlockSize;
    worker_marker_kernel<<<grid, kBlockSize, 0, stream>>>(device_buf,
                                                          worker_id, kBufLen);
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        return set_error(error_out, "worker_marker_kernel launch", err);
    }
    err = cudaMemcpyAsync(host_buf, device_buf, sizeof(int) * kBufLen,
                          cudaMemcpyDeviceToHost, stream);
    if (err != cudaSuccess) {
        return set_error(error_out, "cudaMemcpyAsync", err);
    }
    err = cudaStreamSynchronize(stream);
    if (err != cudaSuccess) {
        return set_error(error_out, "cudaStreamSynchronize", err);
    }
    return true;
}

int active_worker_count() {
    std::lock_guard<std::mutex> lock(g_mutex);
    return g_initialized ? static_cast<int>(g_workers.size()) : 0;
}

} // namespace bench_cuda

#endif // FTOQC_HAS_CUDA
