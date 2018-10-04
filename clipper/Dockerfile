FROM ucbjey/risecamp2018-base:2b580e66f1f7

USER root

RUN apt-get update && apt-get install -y redis-server

USER $NB_USER

COPY requirement.txt requirement.txt

RUN pip install --upgrade pip setuptools

RUN pip install -r requirement.txt

COPY tutorial /home/$NB_USER/

# configure httpd
USER root
COPY nginx.conf /etc/nginx/sites-enabled/default
