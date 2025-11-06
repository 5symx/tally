FROM docker.m.daocloud.io/nvidia/cuda:12.2.0-devel-ubuntu20.04

RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        curl \
        git \
        wget \
        libacl1-dev \
        libncurses5-dev \
        pkg-config \
        zlib1g \
        g++-10 \
        sudo \
        libssl-dev \
        vim \
        libfreeimage-dev \
        python3-dev \
        zlib1g-dev \
        tzdata

RUN rm /usr/bin/g++ && \
    rm /usr/bin/gcc && \
    ln -s /usr/bin/g++-10 /usr/bin/g++ && \
    ln -s /usr/bin/gcc-10 /usr/bin/gcc


RUN cd /home && \
    mkdir /opt/cmake && \
    wget https://cmake.org/files/v3.27/cmake-3.27.0-linux-x86_64.sh && \
    sh cmake-3.27.0-linux-x86_64.sh --prefix=/opt/cmake --skip-license && \
    ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake

RUN cd /home && \
    wget https://archives.boost.io/release/1.80.0/source/boost_1_80_0.tar.gz && \
    tar xvf boost_1_80_0.tar.gz && \
    cd boost_1_80_0 && \
    ./bootstrap.sh --prefix=/usr/ && \
    ./b2 install && \
    cd /home && \
    rm boost_1_80_0.tar.gz && \
    rm -rf boost_1_80_0

WORKDIR /home/tally

COPY . .

# RUN mkdir cudnn && \
#     cd cudnn && \
#     wget https://developer.download.nvidia.cn/compute/cudnn/redist/cudnn/linux-x86_64/cudnn-linux-x86_64-8.9.3.28_cuda12-archive.tar.xz && \
#     tar -xvf cudnn-linux-x86_64-8.9.3.28_cuda12-archive.tar.xz && \
#     cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include && \
#     cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64 && \
#     chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# RUN cp /usr/include/cudnn*.h /usr/local/cuda/include && \
#     cp -P /usr/lib/$(uname -m)-linux-gnu/libcudnn* /usr/local/cuda/lib64 && \
#     chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*


RUN cd third_party && \
    cp cudnn-frontend/ /usr/local/cuda/ -r

RUN cd third_party/folly && \
    git checkout 6d79e8b && \
    sudo ./build/fbcode_builder/getdeps.py install-system-deps --recursive && \
    python3 ./build/fbcode_builder/getdeps.py --allow-system-packages build \
        --no-tests --install-prefix /usr/local

RUN cd cudnn && \
    tar -xvf cudnn-linux-x86_64-8.9.3.28_cuda12-archive.tar.xz && \
    cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include && \
    cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64 && \
    chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# RUN mkdir cudnn && \
#     cd cudnn && \
#     wget https://developer.download.nvidia.cn/compute/cudnn/redist/cudnn/linux-x86_64/cudnn-linux-x86_64-8.9.3.28_cuda12-archive.tar.xz && \
#     tar -xvf cudnn-linux-x86_64-8.9.3.28_cuda12-archive.tar.xz && \
#     cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include && \
#     cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64 && \
#     chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

 
RUN cd third_party/nccl && \
    make -j src.build NVCC_GENCODE="-gencode=arch=compute_89,code=sm_89"

RUN ln -sf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so
# RUN cd /home && \
#     git clone https://github.com/facebook/folly && \
#     cd folly && \
#     git checkout 6d79e8b && \
#     sudo ./build/fbcode_builder/getdeps.py install-system-deps --recursive && \
#     python3 ./build/fbcode_builder/getdeps.py --allow-system-packages build \
#         --no-tests --install-prefix /usr/local


# WORKDIR /home/tally
#RUN cd /home/tally && \
#    make folly && \ 
#    make

# RUN cd tally && mkdir -p build && cd build && cmake .. && make -j
