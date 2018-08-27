# vim: set filetype=dockerfile:
FROM jupyter/pyspark-notebook:8ccdfc1da8d5

USER $NB_USER

#### ray

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install scipy

RUN pip install https://s3-us-west-2.amazonaws.com/ray-wheels/9ad94e33d611905347522c493ad58fe0237c87a2/ray-0.4.0-cp36-cp36m-manylinux1_x86_64.whl

RUN mkdir -p /home/$NB_USER
COPY tutorial /home/$NB_USER/

USER root
RUN chown -R $NB_USER:users /home/$NB_USER && rmdir /home/$NB_USER/work

#### finalize
COPY ./risecamp_start.sh /opt

WORKDIR /home/$NB_USER
USER $NB_USER
RUN pip install jupyterhub==0.7.2
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh
