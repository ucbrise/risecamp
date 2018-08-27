FROM jupyter/pyspark-notebook:8ccdfc1da8d5

USER $NB_USER
RUN pip install --upgrade pip
RUN pip install jupyterhub==0.7.2
COPY ./risecamp_start.sh /opt

WORKDIR /home/$NB_USER
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh

USER $NB_USER
