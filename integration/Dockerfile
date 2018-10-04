FROM ucbjey/risecamp2018-base:2b580e66f1f7

USER root
RUN apt-get update
RUN apt-get install -y python-pydot python-pydot-ng graphviz git daemon default-libmysqlclient-dev

# Wave support
RUN cd /tmp && git clone https://github.com/immesys/pywave
COPY wavesupport/prestart.sh /usr/local/bin/start-notebook.d
COPY wavesupport/waved /usr/local/bin
COPY wavesupport/wave.toml /usr/local/bin

USER $NB_USER

# pip install in Python3 for Jupyter
RUN cd /tmp/pywave && pip install .
RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install graphviz && \
    pip install gitpython && \
    pip install tqdm && \
    pip install lz4 && \
    pip install ray==0.5.2 && \
    pip install clipper_admin 

# conda install in python2 for pong env
RUN conda create -n pong_py2 python=2 jupyter
RUN /bin/bash -c "source activate pong_py2 && \
        conda install -y -q libgcc numpy pyzmq subprocess32 pandas matplotlib seaborn tensorflow scikit-learn && \
        pip install tensorflow==1.3.0 gym==0.9.2 smart_open cython mysqlclient"

# Python library support
ENV LIBPATH /home/$NB_USER/libraries

WORKDIR /home/$NB_USER
RUN git clone https://github.com/ucbrise/flor $LIBPATH/flor
RUN git clone https://github.com/ground-context/grit $LIBPATH/grit
RUN git clone https://github.com/ground-context/client $LIBPATH/client
COPY clipper_util $LIBPATH/clipper_util
COPY pong_py_no_git $LIBPATH/pong_py_no_git
RUN cd $LIBPATH/pong_py_no_git && pip install .

ENV PYTHONPATH $PYTHONPATH:$LIBPATH/grit/python:$LIBPATH/client/python:$LIBPATH/flor:$LIBPATH

RUN mkdir /home/$NB_USER/tutorial
COPY tutorial /home/$NB_USER/tutorial
COPY start_webserver.sh /home/$NB_USER/tutorial
COPY pong-js /home/$NB_USER/tutorial/pong-js

USER root
RUN chmod +x /home/$NB_USER/tutorial/start_webserver.sh

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

