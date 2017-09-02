# FROM continuumio/miniconda

FROM jupyter/base-notebook
USER root
RUN apt-get update && apt-get install -yqq libzmq5 git \
      apt-transport-https ca-certificates curl software-properties-common net-tools \
      && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
      && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      && apt-get update \
      && apt-get install -yqq docker-ce

# Install Ray dependencies
RUN apt-get update \
    && apt-get install -y vim git wget gcc \
    && apt-get install -y cmake pkg-config build-essential autoconf curl libtool libboost-dev \
    libboost-filesystem-dev libboost-system-dev unzip libzmq5-dev zlib1g-dev

RUN gpasswd -a $NB_USER docker

USER $NB_USER

RUN conda create -n py2 python=2 jupyter
RUN /bin/bash -c "source activate py2 && ipython kernel install --user"

WORKDIR /home/$NB_USER

ENV DATA cifar/

RUN mkdir -p $DATA \
      && /bin/bash -c "source activate py2 && conda install -y -q libgcc numpy pyzmq subprocess32 pandas matplotlib seaborn tensorflow \
      && pip install ray==0.2.0 tensorflow==1.3.0 gym==0.9.2 smart_open"

# TODO: update to pip install clipper==0.2.0 once the Clipper release is pushed
RUN /bin/bash -c "source activate py2 && \
      pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin"


COPY rl_exercise06.ipynb get_docker_ip.sh ./
COPY pong_py_no_git/ ./pong_py_no_git

RUN /bin/bash -c "source activate py2 && pip install ./pong_py_no_git"

USER root
RUN chown jovyan:users -R /home/$NB_USER/
USER $NBUSER

# vim: set filetype=dockerfile:
