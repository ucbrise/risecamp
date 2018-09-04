# vim: set filetype=dockerfile:
FROM jupyter/pyspark-notebook:786611348de1

USER root

# General dependencies
RUN apt-get update \
    && apt-get install -y vim \
    git \
    wget \
    emacs-nox \
    cmake \
    pkg-config \
    build-essential \
    autoconf \
    curl \
    libtool \
    unzip

# Flow dependencies
RUN apt-get install  -y swig \
    libgtest-dev \
    autoconf \
    pkg-config \
    libgdal-dev \
    libxerces-c-dev \
    libproj-dev \
    libfox-1.6-dev \
    libxml2-dev \
    libxslt1-dev \
    flex \
    bison

USER $NB_USER

#### ray

RUN pip install tensorflow==1.8.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install scipy

RUN pip install ray==0.5.2

# Install flow
 COPY ./install-sumo.sh /opt
RUN bash /opt/install-sumo.sh
COPY ./install-flow.sh /opt
RUN bash /opt/install-flow.sh
COPY ./install-web3d.sh /opt
RUN bash /opt/install-web3d.sh

RUN mkdir -p /home/$NB_USER
COPY ray/tutorial /home/$NB_USER/

USER root
RUN chown -R $NB_USER:users /home/$NB_USER && rmdir /home/$NB_USER/work

#### finalize
COPY ./risecamp_start.sh /opt

WORKDIR /home/$NB_USER
USER $NB_USER
RUN pip install jupyterhub==0.7.2
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh
