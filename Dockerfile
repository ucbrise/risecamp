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

# web3d dependencies
RUN sudo apt-get install apt-transport-https
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update
RUN apt-get install -y --no-install-recommends --allow-unauthenticated yarn

USER $NB_USER

#### ray

RUN pip install tensorflow==1.8.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install scipy

RUN pip install ray==0.5.2

# Install Modin.
RUN git clone https://github.com/modin-project/modin.git && \
    pip install modin

# Install flow
 COPY ./install-sumo.sh /opt
RUN bash /opt/install-sumo.sh
COPY ./install-flow.sh /opt
RUN bash /opt/install-flow.sh
COPY ./install-web3d.sh /opt
RUN bash /opt/install-web3d.sh

RUN mkdir -p /home/$NB_USER
COPY ray /home/$NB_USER/

# Install py_pong (for the pong exercise).
RUN pip install /home/$NB_USER/utilities/pong_py

USER root
RUN chown -R $NB_USER:users /home/$NB_USER && rmdir /home/$NB_USER/work

#### finalize
COPY ./risecamp_start.sh /opt

WORKDIR /home/$NB_USER
USER $NB_USER
RUN pip install jupyterhub==0.7.2
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh
