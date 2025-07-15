all: build

folly:
	cd third_party/folly && ./build/fbcode_builder/getdeps.py install-system-deps --recursive && mkdir _build && cd _build &&  cmake .. && make -j$(nproc) && make install;

build: FORCE
	cd third_party/nccl && make -j src.build NVCC_GENCODE="-gencode=arch=compute_89,code=sm_89"
	cd third_party/nccl/ext-net/example && make
	mkdir -p build
	cd build && cmake  -DCMAKE_CUDA_STANDARD=17  -DENABLE_LOGGING=OFF -DSERVER_VERSION=$(SERVER_VERSION) ..  && make -j

FORCE: ;
