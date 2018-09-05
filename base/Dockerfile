FROM jupyter/pyspark-notebook:8ccdfc1da8d5

USER root
RUN mkdir -p /usr/local/bin/start-notebook.d
COPY ./risecamp_start.sh /opt
CMD /opt/risecamp_start.sh

USER $NB_USER
WORKDIR /home/$NB_USER
RUN rmdir /home/$NB_USER/work
RUN pip install --upgrade pip
