FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update
RUN apt-get install -y g++

USER root

RUN apt-get -y update && \
    apt-get install --no-install-recommends -y \
      curl \
      openjdk-8-jdk-headless \
      ca-certificates-java && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L -o /usr/local/bin/coursier https://git.io/vgvpD && \
    chmod +x /usr/local/bin/coursier

RUN apt-get update && apt-get -yq dist-upgrade \
    && apt-get install -yq --no-install-recommends \
    build-essential ocaml ocamlbuild automake autoconf libtool wget python libssl-dev cmake gdb

USER $NB_USER

ENV SCALA_VERSION 2.11.12
ENV ALMOND_VERSION 0.1.7

RUN coursier bootstrap \
      -i user -I user:sh.almond:scala-kernel-api_$SCALA_VERSION:$ALMOND_VERSION \
      sh.almond:scala-kernel_$SCALA_VERSION:$ALMOND_VERSION \
      -o almond && \
    ./almond --help && \
    ./almond --install && \
    rm almond

RUN git clone https://github.com/intel/linux-sgx.git -b sgx_2.3 && \
    cd linux-sgx && \
    ./download_prebuilt.sh && \
    make --quiet sdk_install_pkg

USER root
RUN echo $'no\n/usr/local' | ${HOME}/linux-sgx/linux/installer/bin/sgx_linux_x64_sdk_*.bin
USER $NB_USER

RUN rm -r linux-sgx

ENV SGX_SDK="/usr/local/sgxsdk"
ENV PATH="${PATH}:$SGX_SDK/bin:$SGX_SDK/bin/x64"
ENV PKG_CONFIG_PATH="${PKG_CONFIG_PATH}:$SGX_SDK/pkgconfig"

ENV SPARKSGX_DATA_DIR="${HOME}/opaque/data"
ENV PRIVATE_KEY_PATH="${HOME}/opaque/private_key.pem"

# Setting LD_LIBRARY_PATH seems not to work, so we instead just link each
# library into /usr/lib and run ldconfig. See
# https://stackoverflow.com/questions/51670836/saving-dockerfile-env-variables-for-future-use
USER root
RUN find $SGX_SDK/sdk_libs -name '*.so' -exec ln -s {} /usr/lib/ \; && ldconfig
USER $NB_USER
# ENV LD_LIBRARY_PATH="${SGX_SDK}/sdk_libs"

RUN /bin/bash -c '\
    git clone https://github.com/ankurdave/opaque.git -b risecamp2018 && \
    cd opaque && \
    openssl ecparam -name prime256v1 -genkey -noout -out private_key.pem && \
    ./build/sbt publish-local'

# Prefetch Spark SQL 2.0.2 for Opaque tutorial
RUN coursier fetch org.apache.spark:spark-sql_2.11:2.0.2

# Generate Opaque test data for Opaque tutorial
RUN cd opaque && ./build/sbt synthTestData

# perform boot-time initialization by adding a startup script
# COPY init-world.sh /usr/local/bin/start-notebook.d

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/

# configure httpd
USER root
COPY nginx.conf /etc/nginx/sites-enabled/default
