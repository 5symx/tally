cmake_minimum_required(VERSION 3.24)
project(tally LANGUAGES C CXX CUDA)
enable_language(CUDA)

#set(SERVER_VERSION server)
set(SERVER_VERSION "server" CACHE STRING "Server version")
message(STATUS "SERVER_VERSION is set to: ${SERVER_VERSION}")

if (SERVER_VERSION STREQUAL "server_naive")
    add_definitions(-DUSE_NAIVE_CLIENT)
    message(STATUS "client headfile is set to: naive")
endif()

set(CMAKE_CUDA_COMPILER nvcc)
set(CMAKE_CXX_STANDARD 20)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -Wno-deprecated-declarations -Wno-comment -Wno-deprecated -Wno-maybe-uninitialized")

if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "" FORCE)
endif()

option(ENABLE_LOGGING "Enable logging" OFF)
option(ENABLE_PERFORMANCE_LOGGING "Enable performance-related logging" OFF)
option(ENABLE_PROFILING "Enable profiling" OFF)
option(VERIFY_CORRECTNESS "Verify that the results after replacing cublas is correct" OFF)
option(MEASURE_PREEMPTION_LATENCY "Measure latency of preemption in priority scheduler" OFF)

link_directories(/usr/local/cuda/lib)
link_directories(/usr/local/cuda/lib64)
link_directories(/usr/local/cuda/targets/x86_64-linux/lib/stubs)

set(ENV{CUDNN_PATH} /usr/local/cuda/lib)

FIND_PACKAGE(Boost COMPONENTS serialization regex stacktrace_backtrace REQUIRED)
FIND_PACKAGE(folly REQUIRED)
find_package(gflags CONFIG REQUIRED)

add_subdirectory(third_party/spdlog)
add_subdirectory(third_party/iceoryx/iceoryx_meta)
add_subdirectory(third_party/json)
add_subdirectory(third_party/readerwriterqueue)

include(GNUInstallDirs)

find_package(iceoryx_platform REQUIRED)
find_package(iceoryx_posh REQUIRED)
find_package(iceoryx_hoofs REQUIRED)

include(IceoryxPackageHelper)
include(IceoryxPlatform)
include(IceoryxPlatformSettings)

include(FindCUDA/select_compute_arch)
CUDA_DETECT_INSTALLED_GPUS(INSTALLED_GPU_CCS_1)
string(REPLACE " " "" INSTALLED_GPU_CCS_1 ${INSTALLED_GPU_CCS_1})
string(REPLACE "." "" INSTALLED_GPU_CCS_1 ${INSTALLED_GPU_CCS_1})
string(SUBSTRING ${INSTALLED_GPU_CCS_1} 0 2 CUDA_ARCH_LIST)
message(CUDA_ARCH_LIST="${CUDA_ARCH_LIST}")

set(TALLY_CUTLASS_SRC_FILES
    ${PROJECT_SOURCE_DIR}/src/tally/cutlass/cutlass.cu
)

set(TALLY_SRC_FILES
    ${PROJECT_SOURCE_DIR}/src/tally/cache.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/cache_struct.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/cuda_util.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/util.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/signal.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/env.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/transform.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/generated/cuda_api.cpp
)

set(TALLY_SERVER_SRC_FILES
    ${PROJECT_SOURCE_DIR}/src/tally/measurements.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/${SERVER_VERSION}.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/generated/server.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/partial.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/cuda_launch.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/scheduler.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/naive.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/priority.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/profile.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/workload_agnostic.cpp
    ${PROJECT_SOURCE_DIR}/src/tally/scheduler/workload_aware.cpp
)



set(TALLY_CLIENT_SRC_FILES
    ${PROJECT_SOURCE_DIR}/src/tally/client.cpp
)

add_library(nccl_lib SHARED IMPORTED)

set_target_properties(nccl_lib PROPERTIES IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/third_party/nccl/build/lib/libnccl.so)

add_library(tally_cutlass SHARED
    ${TALLY_CUTLASS_SRC_FILES}
)

target_link_libraries(tally_cutlass
    cuda
    cudart
)

target_include_directories(tally_cutlass
    PUBLIC  ${PROJECT_SOURCE_DIR}/include
    PUBLIC  ${PROJECT_SOURCE_DIR}/third_party/cutlass/include
    PUBLIC  ${PROJECT_SOURCE_DIR}/third_party/cutlass/tools/util/include/
)

set_target_properties(tally_cutlass PROPERTIES
    CUDA_ARCHITECTURES ${CUDA_ARCH_LIST}
    CUDA_RUNTIME_LIBRARY Shared
)

add_library(tally STATIC ${TALLY_SRC_FILES})
target_include_directories(tally
    PUBLIC ${PROJECT_SOURCE_DIR}/include
    PUBLIC ${PROJECT_SOURCE_DIR}/third_party/nccl/build/include
    PUBLIC  /usr/local/cuda/include
    PUBLIC ${PROJECT_SOURCE_DIR}/third_party/json/single_include
)

target_link_libraries(tally PUBLIC
    iceoryx_posh::iceoryx_posh
    dl
    spdlog::spdlog $<$<BOOL:${MINGW}>:ws2_32>
)

set(tally_client_targets "tally_client" "tally_client_local")

# tally_client_env_vars
set(tally_client_env_vars "ENABLE_LOGGING" "ENABLE_PERFORMANCE_LOGGING", "ENABLE_PROFILING" "VERIFY_CORRECTNESS")

foreach(tally_client_target IN LISTS tally_client_targets)
    add_library(
        ${tally_client_target} SHARED
        ${PROJECT_SOURCE_DIR}/src/tally/preload/tally_client.cpp
        ${PROJECT_SOURCE_DIR}/src/tally/preload/generated/tally_client.cpp
        ${TALLY_SRC_FILES}
        ${TALLY_CLIENT_SRC_FILES}
    )

    # Loop over the strings using foreach
    foreach(env_var ${tally_client_env_vars})
        if(${env_var})
            target_compile_definitions(${tally_client_target} PRIVATE ${env_var}=${env_var})
        endif()
    endforeach()

    target_include_directories(${tally_client_target}
        PUBLIC ${PROJECT_SOURCE_DIR}/include
        PUBLIC ${PROJECT_SOURCE_DIR}/third_party/nccl/build/include
        PUBLIC  /usr/local/cuda/include
        PUBLIC ${PROJECT_SOURCE_DIR}/third_party/json/single_include
    )

    target_link_libraries(${tally_client_target} PUBLIC
        PUBLIC Boost::serialization 
        PUBLIC Boost::regex
        PUBLIC Boost::stacktrace_backtrace
        iceoryx_posh::iceoryx_posh
        spdlog::spdlog $<$<BOOL:${MINGW}>:ws2_32>
    )

    target_compile_definitions(${tally_client_target} PRIVATE IS_CLIENT="TRUE")
endforeach()

target_compile_definitions(tally_client_local PRIVATE RUN_LOCALLY="TRUE")

add_executable(tally_server ${PROJECT_SOURCE_DIR}/src/tally/tally_server.cpp ${TALLY_SERVER_SRC_FILES})

if(ENABLE_LOGGING)
    target_compile_definitions(tally_server PRIVATE ENABLE_LOGGING=${ENABLE_LOGGING})
endif()

if(MEASURE_PREEMPTION_LATENCY)
    target_compile_definitions(tally_server PRIVATE MEASURE_PREEMPTION_LATENCY=${MEASURE_PREEMPTION_LATENCY})
endif()

target_include_directories(tally_server
    PUBLIC ${PROJECT_SOURCE_DIR}/third_party/nccl/build/include
    PUBLIC /usr/local/cuda/include
    PUBLIC ${PROJECT_SOURCE_DIR}/include
    PUBLIC ${PROJECT_SOURCE_DIR}/third_party/json/single_include
    PUBLIC ${FOLLY_INCLUDE_DIR}
)

target_link_libraries(tally_server PUBLIC
    cuda
    cudart
    cublas
    dl
    tally
    cublasLt
    cudnn
    nccl_lib
    curand
    cusparse
    nvidia-ml
    PUBLIC Boost::serialization
    PUBLIC Boost::regex
    spdlog::spdlog $<$<BOOL:${MINGW}>:ws2_32>
    iceoryx_posh::iceoryx_posh
    ${FOLLY_LIBRARIES}
    readerwriterqueue
)

# Add an option to enable/disable this special build. It's off by default.
option(ENABLE_LLAMA_OVERRIDE "Enable building the llama_model_load_from_file override library" ON)

# Only proceed with this section if the user has enabled the option.
if(ENABLE_LLAMA_OVERRIDE)
    message(STATUS "Llama override library build is ENABLED.")

    # Define a variable for the path to the llama.cpp source directory.
    set(LLAMA_CPP_DIR "" CACHE PATH "Path to the root of the llama.cpp source directory")

    # Ensure the user has provided the path.
    if(NOT LLAMA_CPP_DIR OR NOT EXISTS "${LLAMA_CPP_DIR}/include/llama.h")
        message(FATAL_ERROR "When ENABLE_LLAMA_OVERRIDE is ON, you must set LLAMA_CPP_DIR to a valid llama.cpp source directory.")
    endif()
    message(STATUS "Override using llama.cpp source from: ${LLAMA_CPP_DIR}")

    # Define our new shared library target from its source file.
    # Make sure the path to override.cpp is correct.
    add_library(llama_override SHARED ${PROJECT_SOURCE_DIR}/preload/override.cpp)

    # Set properties for the library.
    set_target_properties(llama_override PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "override" # Creates override.so instead of libllama_override.so
    )

    # Add the llama.cpp directory to the include path for this target only.
    target_include_directories(llama_override PRIVATE ${LLAMA_CPP_DIR}/include ${LLAMA_CPP_DIR}/ggml/include)


    target_link_libraries(llama_override PUBLIC dl)

    message(STATUS "The override library will be built as: ${PROJECT_SOURCE_DIR}/build/liboverride.so (or similar)")

endif()

add_subdirectory(scripts)
add_subdirectory(tests)
add_subdirectory(third_party/cudnn-frontend)
