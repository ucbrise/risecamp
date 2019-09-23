FROM ucbjey/risecamp2018-base:latest

USER root

RUN curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
 && chmod +x /usr/local/bin/docker-compose

USER $NB_USER

COPY requirement.txt requirement.txt

RUN git clone https://github.com/harbor-ml/modelzoo.git

RUN pip install --upgrade pip setuptools

RUN pip install -r requirement.txt

COPY tutorial /home/$NB_USER/

COPY modelzoo /home/$NB_USER/
