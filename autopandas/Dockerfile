FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update
RUN apt-get install -y g++ git

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN conda install python=3.7 anaconda=custom
RUN git clone  --single-branch --branch risecamp https://github.com/rbavishi/atlas.git
RUN cd atlas && git pull origin risecamp && pip install -e . 

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
