FROM ucbjey/risecamp2018-base

USER root

RUN apt-get update && apt-get install -y redis-server

USER $NB_USER

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt

COPY tutorial /home/$NB_USER/
