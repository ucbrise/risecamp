# vim: set filetype=dockerfile:
FROM jupyter/pyspark-notebook:786611348de1

USER $NB_USER

#### ray

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install scipy

RUN pip install ray

RUN mkdir -p /home/$NB_USER/ray
COPY ray/tutorial /home/$NB_USER/ray/

USER root
RUN chown -R $NB_USER:users /home/$NB_USER && rmdir /home/$NB_USER/work

#### finalize
COPY ./risecamp_start.sh /opt

WORKDIR /home/$NB_USER
USER $NB_USER
RUN pip install jupyterhub==0.7.2
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh
