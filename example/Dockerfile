FROM ucbjey/risecamp2018-base

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get install -y g++

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN pip install bokeh==0.13.0

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
