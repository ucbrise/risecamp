FROM ucbjey/risecamp2018-base

# use apt-get as user "root" to install ubuntu packages
USER root

# install graphviz and pydot
RUN apt-get update
RUN apt-get install -y python-pydot python-pydot-ng graphviz

USER $NB_USER

# download and set up Flor
RUN git clone https://github.com/ucbrise/flor
WORKDIR flor
RUN pip3 install -r requirements.txt
RUN pip3 install graphviz

# download and install grit
WORKDIR /home/$NB_USER
RUN git clone https://github.com/ground-context/grit
RUN git clone https://github.com/ground-context/client
ENV PYTHONPATH $PYTHONPATH:/home/$NB_USER/grit/python:/home/$NB_USER/client/python:/home/$NB_USER/flor

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

USER root
# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
RUN chown $NB_USER /home/$NB_USER
