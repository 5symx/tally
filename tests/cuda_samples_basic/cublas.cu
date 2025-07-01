#include <stdio.h>
#include <cassert>
#include <stdlib.h>
#include <iostream>
#include <ctime>
#include <fstream>
#include <sys/time.h>

#include <cublas_v2.h>
#include "cuda.h"

// #define IDX2C(i,j,ld) (((j)*(ld))+(i))

// int main()
// {
//     cublasHandle_t handle;
//     cublasCreate(&handle);
//     int m = 128;
//     int n = 128;
//     int k = 128;

//     float *h_A, *h_B, *h_C, *h_ref;
//     h_A = (float *) malloc(sizeof(float) * m * k);
//     h_B = (float *) malloc(sizeof(float) * k * n);
//     h_C = (float *) malloc(sizeof(float) * m * n);
//     h_ref = (float *) malloc(sizeof(float) * m * n);

//     for (int j = 0; j < k; j++) {
//         for (int i = 0; i < m; i++) {
//             h_A[IDX2C(i, j, m)] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
//         }
//     }

//     for (int j = 0; j < n; j++) {
//         for (int i = 0; i < k; i++) {
//             h_B[IDX2C(i, j, k)] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
//         }
//     }

//     for (int j = 0; j < k; j++) {
//         for (int i = 0; i < m; i++) {
//             for (int p = 0; p < n; p++) {
//                 h_ref[IDX2C(i, j, m)] += h_A[IDX2C(i, p, m)] * h_B[IDX2C(p, j, k)];
//             }
//         }
//     }

//     // Allocate memory on the device
//     float* d_A, *d_B, *d_C;
//     cudaMalloc((void**)&d_A, sizeof(float) * m * k); // m x k matrix
//     cudaMalloc((void**)&d_B, sizeof(float) * k * n); // k x n matrix
//     cudaMalloc((void**)&d_C, sizeof(float) * m * n); // m x n matrix

//     // Copy input matrices from host to device
//     cudaMemcpy(d_A, h_A, sizeof(float) * m * k, cudaMemcpyHostToDevice);
//     cudaMemcpy(d_B, h_B, sizeof(float) * k * n, cudaMemcpyHostToDevice);

//     const float alpha = 1.0f;
//     const float beta = 0.0f;

//     cublasOperation_t transa = CUBLAS_OP_N; // No transpose for A
//     cublasOperation_t transb = CUBLAS_OP_N; // No transpose for B
//     int lda = m; // Leading dimension of A (A is a m x k matrix)
//     int ldb = k; // Leading dimension of B (B is a k x n matrix)
//     int ldc = m; // Leading dimension of C (C is a m x n matrix)

//     cublasSgemm_v2(handle, transa, transb, m, n, k, &alpha, d_A, lda, d_B, ldb, &beta, d_C, ldc);

//     cudaMemcpy(h_C, d_C, sizeof(float) * m * n, cudaMemcpyDeviceToHost);

//     for (int i = 0; i < m; i++) {
//         for (int j = 0; j < n; j++) {

//             if (abs(h_C[IDX2C(i, j, m)] - h_ref[IDX2C(i, j, m)]) > 0.001) {
//                 std::cout << "Results do not match." << std::endl;
//                 std::cout << "h_C[IDX2C(i, j, m)]: " << h_C[IDX2C(i, j, m)] << std::endl;
//                 std::cout << "h_ref[IDX2C(i, j, m)]: " << h_ref[IDX2C(i, j, m)] << std::endl;
//                 exit(1);
//             }
//         }
//     }

//     cudaFree(d_A);
//     cudaFree(d_B);
//     cudaFree(d_C);
//     cublasDestroy(handle);

//     return 0;
// }

#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <iostream>
#include <vector>
#include <cmath>

// Helper to check CUDA calls
#define CUDA_CHECK(err) \
    if (err != cudaSuccess) { \
        std::cerr << "CUDA error: " << cudaGetErrorString(err) << std::endl; \
        exit(EXIT_FAILURE); \
    }

// Helper to check cuBLAS calls
#define CUBLAS_CHECK(err) \
    if (err != CUBLAS_STATUS_SUCCESS) { \
        std::cerr << "cuBLAS error at line " << __LINE__ << std::endl; \
        exit(EXIT_FAILURE); \
    }

void print_matrix(int rows, int cols, const float* data, int ld) {
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            std::cout << data[i * ld + j] << " ";
        }
        std::cout << "\n";
    }
}

int main() {
    const int m = 2, n = 2, k = 2;
    const int batchCount = 2;
    const float alpha = 1.0f, beta = 0.0f;

    // Host arrays
    std::vector<std::vector<float>> h_A(batchCount, std::vector<float>(m * k));
    std::vector<std::vector<float>> h_B(batchCount, std::vector<float>(k * n));
    std::vector<std::vector<float>> h_C(batchCount, std::vector<float>(m * n));

    // Initialize inputs
    for (int b = 0; b < batchCount; ++b) {
        for (int i = 0; i < m * k; ++i) h_A[b][i] = i + b;
        for (int i = 0; i < k * n; ++i) h_B[b][i] = i - b;
    }

    // Device pointers
    float* d_A[batchCount], *d_B[batchCount], *d_C[batchCount];
    float** d_A_array; float** d_B_array; float** d_C_array;
    CUDA_CHECK(cudaMalloc(&d_A_array, batchCount * sizeof(float*)));
    CUDA_CHECK(cudaMalloc(&d_B_array, batchCount * sizeof(float*)));
    CUDA_CHECK(cudaMalloc(&d_C_array, batchCount * sizeof(float*)));

    for (int b = 0; b < batchCount; ++b) {
        CUDA_CHECK(cudaMalloc(&d_A[b], sizeof(float) * m * k));
        CUDA_CHECK(cudaMalloc(&d_B[b], sizeof(float) * k * n));
        CUDA_CHECK(cudaMalloc(&d_C[b], sizeof(float) * m * n));
        CUDA_CHECK(cudaMemcpy(d_A[b], h_A[b].data(), sizeof(float) * m * k, cudaMemcpyHostToDevice));
        CUDA_CHECK(cudaMemcpy(d_B[b], h_B[b].data(), sizeof(float) * k * n, cudaMemcpyHostToDevice));
    }

    CUDA_CHECK(cudaMemcpy(d_A_array, d_A, sizeof(float*) * batchCount, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_B_array, d_B, sizeof(float*) * batchCount, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_C_array, d_C, sizeof(float*) * batchCount, cudaMemcpyHostToDevice));

    // Create handle and stream
    cublasHandle_t handle;
    cudaStream_t stream;
    CUBLAS_CHECK(cublasCreate(&handle));
    CUDA_CHECK(cudaStreamCreate(&stream));
    CUBLAS_CHECK(cublasSetStream(handle, stream));

    // Perform GEMM
    CUBLAS_CHECK(cublasGemmBatchedEx(
        handle,
        CUBLAS_OP_N, CUBLAS_OP_N,
        m, n, k,
        &alpha,
        (void**)d_A_array, CUDA_R_32F, m,
        (void**)d_B_array, CUDA_R_32F, k,
        &beta,
        (void**)d_C_array, CUDA_R_32F, m,
        batchCount,
        CUDA_R_32F,
        CUBLAS_GEMM_DEFAULT
    ));

    // Step 4: Copy result from device to host
    for (int b = 0; b < batchCount; ++b) {
        CUDA_CHECK(cudaMemcpyAsync(h_C[b].data(), d_C[b], sizeof(float) * m * n,
                                   cudaMemcpyDeviceToHost, stream));
    }

    CUDA_CHECK(cudaStreamSynchronize(stream));

    // Step 5: Print results
    for (int b = 0; b < batchCount; ++b) {
        std::cout << "C[" << b << "]\n";
        print_matrix(m, n, h_C[b].data(), m);
        std::cout << "=====\n";
    }

    // Cleanup
    CUBLAS_CHECK(cublasDestroy(handle));
    CUDA_CHECK(cudaStreamDestroy(stream));
    for (int b = 0; b < batchCount; ++b) {
        CUDA_CHECK(cudaFree(d_A[b]));
        CUDA_CHECK(cudaFree(d_B[b]));
        CUDA_CHECK(cudaFree(d_C[b]));
    }
    CUDA_CHECK(cudaFree(d_A_array));
    CUDA_CHECK(cudaFree(d_B_array));
    CUDA_CHECK(cudaFree(d_C_array));

    return 0;
}