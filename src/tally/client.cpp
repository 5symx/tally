
#include <cstring>
#include <memory>
#include <vector>

#include <tally/util.h>

#ifdef USE_NAIVE_CLIENT
    #include <tally/client_init.h>
#else
    #include <tally/client.h>
#endif


#include <tally/generated/cuda_api.h>

TallyClient *TallyClient::client;// = nullptr;

cudaError_t LAST_CUDA_ERR = cudaSuccess;
bool REPLACE_CUBLAS = false;


__attribute__((__constructor__)) void init_client()
{
	if (std::getenv("REPLACE_CUBLAS")) {
		REPLACE_CUBLAS = true;
	}

    TallyClient::client = new TallyClient;

    // --- Extracting program name from /proc/self/cmdline ---
    std::ifstream cmdline_file("/proc/self/cmdline", std::ios::binary);
    if (cmdline_file.is_open()) {
        std::string arg;
        std::vector<std::string> args_from_cmdline;

        while (std::getline(cmdline_file, arg, '\0')) {
            args_from_cmdline.push_back(arg);
        }
        cmdline_file.close();

        for (size_t i = 1; i < args_from_cmdline.size(); ++i) {
            if (args_from_cmdline[i] == "-m") {
                if (i + 1 < args_from_cmdline.size()) {
                    // THIS IS THE ARGUMENT YOU WANT: the one after "-m"
                    std::string target_filepath = args_from_cmdline[i+1];
                    std::cout << "Constructor: Found argument after -m: " << target_filepath << std::endl;

                    // Now, pass this argument to your TallyClient for further processing
                    TallyClient::client->setM_ID(target_filepath);

                    // exit(1); // Exits the entire program
                    return; 
                } else {
                    std::cerr << "Constructor Error: '-m' flag found but no argument followed it." << std::endl;
                    exit(1);
                }
            }
        }


    } else {
        std::cerr << "Constructor: Could not open /proc/self/cmdline to get program name." << std::endl;
    }
}
