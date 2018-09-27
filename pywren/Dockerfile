FROM ucbjey/risecamp2018-base

# use apt-get as user "root" to install ubuntu packages
USER root
# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN git clone https://github.com/pywren/pywren.git /home/$NB_USER/pywren
RUN pip install -e /home/$NB_USER/pywren
RUN mkdir -p /home/$NB_USER/.aws

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
