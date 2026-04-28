#ifndef TALLY_CLIENT_H
#define TALLY_CLIENT_H

#include <signal.h>
#include <map>
#include <string>
#include <vector>
#include <chrono>
#include <memory>
#include <functional>
#include <iostream>
#include <cassert>
#include <sstream>
#include <unordered_map>
#include <unistd.h>

#include "iceoryx_dust/posix_wrapper/signal_watcher.hpp"
#include "iceoryx_posh/popo/untyped_client.hpp"
#include "iceoryx_posh/runtime/posh_runtime.hpp"
#include "iox/detail/unique_id.hpp"

#include "tally/msg_struct.h"

#include <dlfcn.h>

extern cudaError_t LAST_CUDA_ERR;
extern bool REPLACE_CUBLAS;

class TallyClient {

public:

    static TallyClient *client;
    int32_t client_id;

    //add3
    int mapped_id;
    std::string m_id_str = "";
    
    bool has_connected = false;

    std::recursive_mutex iox_mtx;

    std::map<const void *, std::string> host_func_to_demangled_kernel_name_map;
    std::map<std::string, std::vector<uint32_t>> _kernel_name_to_args;

    std::unordered_map<const void *, std::vector<uint32_t>> _kernel_addr_to_args;
    std::unordered_map<CUfunction, std::vector<uint32_t>> _jit_kernel_addr_to_args;

    iox::popo::UntypedClient *iox_client;

    TallyClient() :
        client_id(getpid())
    {
        mapped_id = -1;
    }

    ~TallyClient(){}

    static const std::unordered_map<std::string, int>& model_name_to_id_map()
    {
        // Add new models here to assign stable IDs.
        static const std::unordered_map<std::string, int> model_map = {
            {"ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf", 1},
            {"Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", 2},
        };
        return model_map;
    }

    // void setM_ID(const std::string& full_file_path) {
    //     size_t base_pos = full_file_path.find_last_of("/\\");
    //     std::string model_name = (base_pos == std::string::npos) ? full_file_path : full_file_path.substr(base_pos + 1);
    //     m_id_str = model_name;

    //     const auto& model_map = model_name_to_id_map();
    //     auto it = model_map.find(model_name);
    //     if (it != model_map.end()) {
    //         mapped_id = it->second;
    //     } else {
    //         mapped_id = -1;
    //         std::cerr << "Warning: model is not in model_name_to_id_map, using mapped_id=-1. model=" << model_name << std::endl;
    //     }

    //     std::cout << "set client model id to: " << mapped_id << std::endl;
    //     // exit(1);
    // }
    void setM_ID(const std::string& full_file_path) 
    {
        m_id_str = full_file_path;
        mapped_id = -1; // Default to -1

        const auto& model_map = model_name_to_id_map();

        // Loop through the map and check if the key is a substring of the path
        for (const auto& [key, id] : model_map) {
            if (full_file_path.find(key) != std::string::npos) {
                mapped_id = id;
                m_id_str = key; // Update to the "stable" name for cleaner logs
                break; 
            }
        }

        if (mapped_id == -1) {
            std::cerr << "Warning: No known model name found in path: " << full_file_path << std::endl;
        } else {
            std::cout << "Matched Model ID: " << mapped_id << " for path: " << m_id_str << std::endl;
        }
    }

    // void process_args(int argc, char** argv) {
    //     std::cerr << "TallyClient: Processing arguments from __libc_start_main interception." << std::endl;
    //     for (int i = 1; i < argc; ++i) {
    //         std::string arg = argv[i];
    //         if (arg == "-m") {
    //             if (i + 1 < argc) {
    //                 std::string path_mid_arg = argv[++i];
    //                 this->setM_ID(path_mid_arg);
    //                 // Perform your parsing logic here (e.g., extractAndSetM_ID)
    //                 // For simplicity, just store the path for now
    //                 std::cerr << "TallyClient: Found -m with path: " << path_mid_arg << std::endl;
    //             }
    //         }
    //     }
    //     std::cout << "TallyClient: set model id " << mapped_id << std::endl;
    //     exit(1);
    // }


    void connect_to_server()
    {
        if (!has_connected) {
            int32_t priority = std::getenv("PRIORITY") ? std::stoi(std::getenv("PRIORITY")) : 1;

            auto app_name_str_base = std::string("tally-client-app");
            auto app_name_str = app_name_str_base + std::to_string(client_id);

            char APP_NAME[100];
            strcpy(APP_NAME, app_name_str.c_str()); 

            iox::runtime::PoshRuntime::initRuntime(APP_NAME);

            iox::popo::UntypedClient client_handshake({"Tally", "handshake", "event"});

            // Send handshake to server
            client_handshake.loan(sizeof(HandshakeMessgae), alignof(HandshakeMessgae))
                .and_then([&](auto& requestPayload) {

                    auto request = static_cast<HandshakeMessgae*>(requestPayload);
                    request->header.client_id = client_id;
                    request->client_id = client_id;
                    request->mapped_id = mapped_id;
                    request->priority = priority;

                    client_handshake.send(request).or_else(
                        [&](auto& error) { std::cout << "Could not send Request! Error: " << error << std::endl; });
                })
                .or_else([](auto& error) { std::cout << "Could not allocate Request! Error: " << error << std::endl; });

            while (!client_handshake.take().and_then([&](const auto& responsePayload) {

                auto response = static_cast<const HandshakeResponse*>(responsePayload);
                
                bool success = response->success;
                if (!success) {
                    std::cout << "Handshake with tally server failed. Exiting ..." << std::endl;
                    exit(1);
                }

                client_handshake.releaseResponse(responsePayload);

            })) {};

            // auto channel_desc_str = std::string("Tally-Communication") + std::to_string(client_id);
            auto channel_desc_str = std::string("Tally-Main") + std::to_string(mapped_id);
            char channel_desc[100];
            strcpy(channel_desc, channel_desc_str.c_str()); 
            iox_client = new iox::popo::UntypedClient({channel_desc, "tally", "tally"});
        }

        has_connected = true;
    }
};

#endif // TALLY_CLIENT_H
