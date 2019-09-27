FROM ucbjey/risecamp2018-base:latest

USER root

RUN apt-get update && apt-get install -y redis-server
RUN curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
 && chmod +x /usr/local/bin/docker-compose

USER $NB_USER

COPY requirement.txt requirement.txt

RUN pip install --upgrade pip setuptools

RUN pip install -r requirement.txt

COPY tutorial /home/$NB_USER/

# configure httpd
USER root
COPY clipper-init.sh /usr/local/bin/start-notebook.d
COPY nginx.conf /home/clipper.nginx.conf
