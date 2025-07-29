#define _GNU_SOURCE // Must be defined before any includes to get RTLD_NEXT
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h> // Needed for getenv()
#include "llama.h" // You MUST include the original llama.h

// Use extern "C" to prevent C++ name mangling. This is essential!
extern "C" {

// Define a function pointer type that matches the original function's signature
typedef llama_model* (*original_load_func_t)(const char*, llama_model_params);

struct llama_model* llama_model_load_from_file(
        const char* path_model,
        struct llama_model_params params) {

    printf("\n--- INTERCEPTED call to llama_model_load_from_file ---\n");
    printf("--- Custom logic is now running! ---\n");
    printf("--- Model path provided: %s ---\n\n", path_model);

    // --- YOUR CUSTOM LOGIC GOES HERE ---
    // For example, you could modify the parameters before passing them on.
    // Let's say we want to force GPU offloading for this model.
    // params.n_gpu_layers = 99; // Example modification
    // printf("--- Modified params: Set n_gpu_layers to %d ---\n", params.n_gpu_layers);


    // Find the original function in the next library in the search order
    original_load_func_t original_func = (original_load_func_t)dlsym(RTLD_NEXT, "llama_model_load_from_file");

    if (original_func == NULL) {
        fprintf(stderr, "Error in dlsym: could not find original llama_model_load_from_file: %s\n", dlerror());
        return NULL; // Or handle the error appropriately
    }

    printf("--- Now calling the ORIGINAL llama_model_load_from_file... ---\n");
    
    // --- CONTROL LOGIC ---
    // Check if the environment variable flag is set.
    const char* use_custom_flag = getenv("USE_CUSTOM_LLAMA_LOAD");

    if (use_custom_flag != NULL) {
        // The flag is set, so run our custom/override version.
        printf("\n--- INTERCEPTED: Running CUSTOM llama_model_load_from_file ---\n");
        printf("--- Model path provided: %s ---\n", path_model);

        // --- YOUR CUSTOM LOGIC GOES HERE ---
        // For example, modify parameters:
        // params.n_gpu_layers = 99;
        // printf("--- Modified params: Set n_gpu_layers to %d ---\n", params.n_gpu_layers);

        printf("--- Now calling the ORIGINAL function via pointer... ---\n");
        
        // Call the original function THROUGH THE POINTER
        struct llama_model* model = original_func(path_model, params);
        
        printf("--- Returned from original function. Model loaded successfully. ---\n\n");
        return NULL;

    } else {
        // The flag is NOT set, so behave as if we are not here.
        // Immediately call the original function and return its result.
        printf("\n--- INTERCEPTED: Flag not set. Passing call directly to original function. ---\n\n");

        
        
        // Call the original function THROUGH THE POINTER
        return NULL; //original_func(path_model, params);
    }
}

} // extern "C"