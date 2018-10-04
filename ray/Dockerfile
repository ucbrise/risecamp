FROM ucbjey/risecamp2018-base:2b580e66f1f7

USER $NB_USER

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install keras lz4

RUN pip install --upgrade git+git://github.com/hyperopt/hyperopt.git
RUN pip install -U https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-0.5.3-cp36-cp36m-manylinux1_x86_64.whl

COPY tutorial /home/$NB_USER/ 

RUN pip install /home/$NB_USER/rllib_exercises/serving/pong_py --user

# configure httpd
USER root
COPY nginx.conf /etc/nginx/sites-enabled/default
