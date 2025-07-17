
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

TallyClient *TallyClient::client;

cudaError_t LAST_CUDA_ERR = cudaSuccess;
bool REPLACE_CUBLAS = false;

__attribute__((__constructor__)) void init_client()
{
	if (std::getenv("REPLACE_CUBLAS")) {
		REPLACE_CUBLAS = true;
	}

    TallyClient::client = new TallyClient;
}
