FROM ubuntu:xenial
# escape=\

# Install Ray dependencies

RUN apt-get update \
    && apt-get install -y vim git wget \
    && apt-get install -y cmake pkg-config build-essential autoconf curl libtool libboost-dev \
    libboost-filesystem-dev libboost-system-dev unzip libzmq5 libzmq5-dev zlib1g-dev
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh \
    && wget --quiet 'https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh' -O /tmp/anaconda.sh \
    && /bin/bash /tmp/anaconda.sh -b -p /opt/conda \
    && rm /tmp/anaconda.sh
ENV PATH "/opt/conda/bin:$PATH"
RUN conda install -y libgcc pyzmq
RUN pip install flatbuffers gym[atari] opencv-python smart_open
RUN pip install --upgrade pip cloudpickle
RUN conda install -y -c conda-forge tensorflow

# install Ray
RUN pip install git+https://github.com/ray-project/ray.git\#subdirectory=python

RUN mkdir -p /model && mkdir -p /container

WORKDIR /container

COPY __init__.py rpc.py /container/

ENV CLIPPER_MODEL_PATH=/model

COPY pong_model_container.py pong_py/ /container/

# TODO: Remove this command, it's only for debugging
COPY checkpoint/ /model/checkpoint/

CMD ["python", "/container/pong_model_container.py"]
