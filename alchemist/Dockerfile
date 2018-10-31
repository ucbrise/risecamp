FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root

# Spark dependencies
ENV APACHE_SPARK_VERSION 2.3.1
ENV HADOOP_VERSION 2.7

RUN apt-get -y update && \
    apt-get install --no-install-recommends -y openjdk-8-jre-headless ca-certificates-java && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
        wget https://www-us.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
        echo "DC3A97F3D99791D363E4F70A622B84D6E313BD852F6FDBC777D31EAB44CBC112CEEAA20F7BF835492FB654F48AE57E9969F93D3B0E6EC92076D1C5E1B40B4696 *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha512sum -c - && \
        tar xzf spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /usr/local --owner root --group root --no-same-owner && \
        rm spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN cd /usr/local && ln -s spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark


# Spark config
ENV SPARK_HOME /usr/local/spark
ENV PYTHONPATH $SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip
ENV SPARK_OPTS --driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info

# Apache Toree kernel
RUN pip install --no-cache-dir \
    https://dist.apache.org/repos/dist/dev/incubator/toree/0.3.0-incubating-rc1/toree-pip/toree-0.3.0.tar.gz \
    && \
    jupyter toree install --sys-prefix && \
    rm -rf /home/$NB_USER/.local && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Spylon-kernel
RUN conda install --quiet --yes 'spylon-kernel=0.4*' && \
    conda clean -tipsy && \
    python -m spylon_kernel install --sys-prefix && \
    rm -rf /home/$NB_USER/.local && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN add-apt-repository universe && \
    apt-get update && \
    apt-get -y install mpich

RUN apt-get -y install libasio-dev

RUN apt-get -y install libspdlog-dev

RUN apt-get -y install build-essential

RUN apt-get -y install gfortran-6

RUN apt-get -y install cmake

RUN apt-get -y install cmake-curses-gui

RUN apt-get -y install libopenblas-dev liblapack-dev libmetis-dev libparmetis-dev vim screen aptitude

RUN apt-get -y install libproj-dev

RUN apt-get -y install libgeos-dev

# Elemental config
ENV ALCHEMIST_PATH /usr/local/Alchemist
ENV ACIPython_PATH /usr/local/ACIPython
ENV ELEMENTAL_PATH /usr/local/elemental
ENV ARPACK_PATH /usr/local/arpack
ENV EIGEN_PATH /usr/local/eigen
ENV OPENBLAS_NUM_THREADS 1

# Install Elemental
RUN cd /root && \
    git clone git://github.com/elemental/Elemental.git && \
    cd Elemental && \
    git checkout 0.87 && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DEL_DISABLE_PARMETIS=1 -DCMAKE_INSTALL_PREFIX=${ELEMENTAL_PATH} .. && \
    nice make -j8  && \
    make install  && \
    cd ../.. && \
    rm -rf Elemental

# Install arpack
RUN cd /root && \
    git clone https://github.com/opencollab/arpack-ng && \
    cd arpack-ng && \
    git checkout 3.5.0 && \
    mkdir build && \
    cd build && \
    cmake -DMPI=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=${ARPACK_PATH} .. && \
    nice make -j8 && \
    make install && \
    cd ../.. && \
    rm -rf arrack-ng

# Install arpackpp
RUN cd /root && \
    git clone https://github.com/m-reuter/arpackpp && \
    cd arpackpp && \
    git checkout 88085d99c7cd64f71830dde3855d73673a5e872b && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=${ARPACK_PATH} .. && \
    make install && \
    cd ../.. && \
    rm -rf arpackpp

# Install Eigen
RUN cd /root && \
    curl -L http://bitbucket.org/eigen/eigen/get/3.3.4.tar.bz2 | tar xvfj - && \
    cd eigen-eigen-5a0156e40feb && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=${EIGEN_PATH} .. && \
    nice make -j8 && \
    make install && \
    cd ../.. && \
    rm -rf eigen-eigen-5a0156e40feb

ENV SPDLOG_PATH /usr/local/spdlog

RUN cd /root && \
    git clone https://github.com/gabime/spdlog.git && \
    cd spdlog && \
    git checkout 4fba14c79f356ae48d6141c561bf9fd7ba33fabd && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=${SPDLOG_PATH} .. && \
    make install -j8 && \
    cd ../.. && \
    rm -rf spdlog

# Install Alchemist
RUN cd /usr/local && \
    git clone https://github.com/project-alchemist/Alchemist && \
    cd Alchemist

# Install ACIPython
RUN cd /usr/local && \
    git clone https://github.com/project-alchemist/ACIPython

# Python stuff
RUN pip install git+https://github.com/erichson/ristretto
RUN pip install tqdm
RUN pip install h5py
RUN pip install cmocean
RUN pip install netCDF4
RUN pip install git+https://github.com/matplotlib/basemap

# use "$NB_USER" when installing python packages
USER $NB_USER

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
