#include <cuda.h>
#include <stdio.h>

int main() {
    cuInit(0);

    CUmemAllocationProp prop = {};
    prop.type = CU_MEM_ALLOCATION_TYPE_PINNED;
    prop.location.type = CU_MEM_LOCATION_TYPE_DEVICE;
    prop.location.id = 0;
    //accessDesc.location = prop.location;
    //accessDesc.flags = CU_MEM_ACCESS_FLAGS_PROT_READWRITE;
    size_t aligned_sz;
    CUresult res = cuMemGetAllocationGranularity(&aligned_sz, &prop, CU_MEM_ALLOC_GRANULARITY_MINIMUM);
    //sz = ((size + aligned_sz - 1) / aligned_sz) * aligned_sz;
    if (res != CUDA_SUCCESS) {
        printf("cuMemGetAllocationGranularity failed!\n");
        return -1;
    }
    printf("aligned_sz :  %zu ", aligned_sz);

    CUmemGenericAllocationHandle memHandle;
    CUdeviceptr d_ptr;
    size_t size = 1024 * 1024 * 2;  // Allocate 1MB
    printf("request_sz :  %zu ", size);
    size = ((size + aligned_sz - 1) / aligned_sz) * aligned_sz;
    printf("updated_sz :  %zu\n", size);
    // Initialize CUDA Driver API
    // Create virtual memory allocation
    res = cuMemCreate(&memHandle, size, &prop, 0); //CU_MEM_ALLOC_GRANULARITY_MINIMUM); //RECOMMENDED); 
    if (res != CUDA_SUCCESS) {
        const char* errName;
        const char* errString;
        
        cuGetErrorName(res, &errName);
        cuGetErrorString(res, &errString);

        printf("cuMemCreate failed! Error ID: %d (%s) - %s\n", res, errName, errString);
        return -1;
    }
    if (res != CUDA_SUCCESS) {
        printf("cuMemCreate failed!\n");
        return -1;
    }

    // Reserve virtual address space
    res = cuMemAddressReserve(&d_ptr, size, 0, 0, 0);
    if (res != CUDA_SUCCESS) {
        printf("cuMemAddressReserve failed!\n");
        return -1;
    }

    // Map the allocation to the reserved address space
    res = cuMemMap(d_ptr, size, 0, memHandle, 0);
    if (res != CUDA_SUCCESS) {
        printf("cuMemMap failed!\n");
        return -1;
    }

    // Set access permissions
    CUmemAccessDesc accessDesc;
    accessDesc.location.type = CU_MEM_LOCATION_TYPE_DEVICE;
    accessDesc.location.id = 0;
    accessDesc.flags = CU_MEM_ACCESS_FLAGS_PROT_READWRITE;
    res = cuMemSetAccess(d_ptr, size, &accessDesc, 1);
    if (res != CUDA_SUCCESS) {
        printf("cuMemSetAccess failed!\n");
        return -1;
    }

    printf("Virtual Memory allocated and mapped at: %p\n", (void*)d_ptr);

    // Free memory
    cuMemUnmap(d_ptr, size);
    cuMemRelease(memHandle);
    cuMemAddressFree(d_ptr, size);

    printf("Virtual Memory allocation and deallocation successful!\n");
    return 0;
}


