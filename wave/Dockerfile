FROM immesys/risecamp2018-base

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update
RUN apt-get install -y g++ git daemon
RUN cd /tmp && git clone https://github.com/immesys/pywave
COPY support /support
ENV PRE_START_SCRIPT=/support/prestart.sh

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN pip install bokeh==0.13.0
RUN cd /tmp/pywave && pip install .
RUN pip install paho-mqtt

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
