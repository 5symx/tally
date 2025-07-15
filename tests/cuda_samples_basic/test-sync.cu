#include <stdio.h>
#include <cassert>
#include <stdlib.h>
#include <iostream>
#include <ctime>
#include <fstream>
#include <sys/time.h>
#include <chrono>
#include <cstdlib>

#include "cuda.h"
#include "cuda_runtime.h"


// Function to check CUDA errors
#define CHECK_CUDA_ERROR(err) \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA Error: %s in %s at line %d\n", cudaGetErrorString(err), __FILE__, __LINE__); \
        exit(EXIT_FAILURE); \
    }

__global__ void elementwiseAddition(float* a, float* b, float* c, int size) {
    
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (tid < size) {
        c[tid] = a[tid] + b[tid];
    }
}
__global__ void nullAddition(float* a, float* b, float* c, int size) {
    
}


__host__ void runElementwiseAddition(float* arr_a, float* arr_b, float* arr_c, int size, bool ptb, bool *is_graph)
{
    // Allocate memory on the device (GPU)
    float* deviceA, * deviceB, * deviceC, * deviceD;

    // Define execution configuration
    dim3 block_dim(256);
    dim3 grid_dim((size + block_dim.x - 1) / block_dim.x);

    cudaGraph_t graph;
    cudaGraphExec_t graphExec;
    cudaStream_t copy_stream; // A dedicated stream for graph capture

    
    auto start = std::chrono::high_resolution_clock::now();

    cudaMalloc((void**)&deviceA, size * sizeof(float));
    cudaMalloc((void**)&deviceB, size * sizeof(float));
    cudaMalloc((void**)&deviceC, size * sizeof(float));

    auto d_stream = nullptr;
    // CHECK_CUDA_ERROR(cudaStreamCreateWithFlags(&copy_stream, 0));


	
    // CHECK_CUDA_ERROR(cudaStreamBeginCapture(copy_stream, cudaStreamCaptureModeThreadLocal));
    // cudaMemcpyAsync(deviceA, arr_a, size * sizeof(float), cudaMemcpyHostToDevice,  copy_stream);
    // cudaMemcpyAsync(deviceB, arr_b, size * sizeof(float), cudaMemcpyHostToDevice,  copy_stream);
    // cudaMemcpyAsync(deviceA, arr_a, size * sizeof(float), cudaMemcpyHostToDevice,  copy_stream);

    // CHECK_CUDA_ERROR(cudaStreamEndCapture(copy_stream, &graph));
    // CHECK_CUDA_ERROR(cudaGraphInstantiate(&graphExec, graph, NULL, NULL, 0));
    // CHECK_CUDA_ERROR(cudaGraphLaunch(graphExec, copy_stream));
    // cudaStreamSynchronize(copy_stream);


    // cudaMemcpyAsync(deviceA, arr_a, size * sizeof(float), cudaMemcpyHostToDevice,  0);
    cudaMemcpyAsync(deviceB, arr_b, size * sizeof(float), cudaMemcpyHostToDevice,  0);
    cudaMemcpyAsync(deviceA, arr_a, size * sizeof(float), cudaMemcpyHostToDevice,  0);
    CHECK_CUDA_ERROR(cudaStreamSynchronize(0));

    
    cudaMalloc((void**)&deviceD, size * sizeof(float));
    // cudaDeviceSynchronize();
    elementwiseAddition<<<grid_dim, block_dim, 0,  copy_stream>>>(deviceA, deviceB, deviceC, size);
    cudaStreamSynchronize( copy_stream);

    

    // float* host_c_result;
    // cudaMallocHost((void**)&host_c_result, size * sizeof(float));
    float* host_c_result = new float[size];
    // host_c_result = (float*)malloc(size * sizeof(float));
    cudaMemcpyAsync(host_c_result, deviceC, size * sizeof(float), cudaMemcpyDeviceToHost, copy_stream);
    cudaStreamSynchronize( copy_stream);

    bool success = true;
    for (int i = 0; i < size; ++i) {
        // Compare device result with expected host calculation
        if (host_c_result[i] != (arr_a[i] + arr_b[i])) {
            std::cerr << "Verification failed at index " << i
                    << ": Expected " << (arr_a[i] + arr_b[i])
                    << ", Got " << host_c_result[i] << std::endl;
            success = false;
            // exit(EXIT_FAILURE);
            // Optionally break early if you find an error
            // break;
        }

        if (success) {
            std::cout << "Element-wise addition verification successful!" << std::endl;
        } else {
            std::cerr << "Element-wise addition verification FAILED!" << std::endl;
        }
    }

    // float* host_b_result = new float[size];
    // cudaMemcpyAsync(host_b_result, deviceB, size * sizeof(float), cudaMemcpyDeviceToHost, 0);
    // cudaStreamSynchronize( 0);

    // bool success = true;
    // for (int i = 0; i < size; ++i) {
    //     // Compare device result with expected host calculation
    //     if (host_b_result[i] != (arr_b[i] )) {
    //         std::cerr << "Verification failed at index " << i
    //                 << ": Expected " << (arr_b[i] )
    //                 << ", Got " << host_b_result[i] << std::endl;
    //         success = false;
    //         // exit(EXIT_FAILURE);
    //         // Optionally break early if you find an error
    //         // break;
    //     }

    //     if (success) {
    //         std::cout << "Element-wise addition verification successful!" << std::endl;
    //     } else {
    //         std::cerr << "Element-wise addition verification FAILED!" << std::endl;
    //     }
    // }

    // float* host_a_result = new float[size];
    // cudaMemcpyAsync(host_a_result, deviceA, size * sizeof(float), cudaMemcpyDeviceToHost, 0);
    // cudaStreamSynchronize( 0);

    // success = true;
    // for (int i = 0; i < size; ++i) {
    //     // Compare device result with expected host calculation
    //     if (host_a_result[i] != (arr_a[i] )) {
    //         std::cerr << "Verification failed at index " << i
    //                 << ": Expected " << (arr_a[i] )
    //                 << ", Got " << host_a_result[i] << std::endl;
    //         success = false;
    //         // exit(EXIT_FAILURE);
    //         // Optionally break early if you find an error
    //         // break;
    //     }

    //     if (success) {
    //         std::cout << "Element-wise addition verification successful!" << std::endl;
    //     } else {
    //         std::cerr << "Element-wise addition verification FAILED!" << std::endl;
    //     }
    // }

    



	//cudaDeviceSynchronize();
    
    // cudaDeviceSynchronize();
    //cudaStreamSynchronize(d_stream);

    auto end = std::chrono::high_resolution_clock::now();

    // Calculate the elapsed time
    std::chrono::duration<double, std::milli> elapsed = end - start;

    // Print the elapsed time
    std::cout << "Elapsed time: " << elapsed.count() << " milliseconds." << std::endl;



    

    // --- Cleanup (Important!) ---
    // cudaFree(host_c_result);

    // cudaFree(deviceA);
    // cudaFree(deviceB);
    // cudaFree(deviceC);
}

int main()
{
    int size = 5;
    bool ptb = false;
    bool is_graph = false;
    

    // Allocate memory on the host (CPU)
    float* arr_a = new float[size];
    float* arr_b = new float[size];
    float* res_gpu = new float[size];
    

    // float* arr_a;
    // float* arr_b;
    // float* res_gpu;
    // cudaMallocHost((void**)&arr_a, size * sizeof(float));
    // cudaMallocHost((void**)&arr_b, size * sizeof(float));
    // cudaMallocHost((void**)&res_gpu, size * sizeof(float));

    std::srand(std::time(nullptr));
    
    // Initialize input arrays
    for (int i = 0; i < size; i++) {
        arr_a[i] = 2;//static_cast<float>(std::rand()) / RAND_MAX;
        arr_b[i] = 5;//static_cast<float>(std::rand()) / RAND_MAX;
    }
    


    runElementwiseAddition(arr_a, arr_b, res_gpu, size, ptb, &is_graph);
    // float* deviceA;
    // cudaMalloc((void**)&deviceA, size * sizeof(float));
    // cudaMemcpyAsync(deviceA, arr_a, size * sizeof(float), cudaMemcpyHostToDevice,  0);
    // cudaStreamSynchronize( 0);


    // float* host_c_result = new float[size];
    // cudaMemcpyAsync(host_c_result, deviceA, size * sizeof(float), cudaMemcpyDeviceToHost, 0);
    // cudaStreamSynchronize( 0);

    // bool success = true;
    // for (int i = 0; i < size; ++i) {
    //     // Compare device result with expected host calculation
    //     if (host_c_result[i] != (arr_a[i] )) {
    //         std::cerr << "Verification failed at index " << i
    //                 << ": Expected " << (arr_a[i] )
    //                 << ", Got " << host_c_result[i] << std::endl;
    //         success = false;
    //         // exit(EXIT_FAILURE);
    //         // Optionally break early if you find an error
    //         // break;
    //     }

    //     if (success) {
    //         std::cout << "Element-wise addition verification successful!" << std::endl;
    //     } else {
    //         std::cerr << "Element-wise addition verification FAILED!" << std::endl;
    //     }
    // }

    // cudaFree(deviceA);

    
    // Cleanup
    delete[] arr_a;
    delete[] arr_b;
    delete[] res_gpu;

    return 0;
}
