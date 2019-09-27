FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN pip install bokeh==0.13.0
RUN conda update -n base -c defaults conda
RUN conda install -c conda-forge psutil setproctitle
RUN pip install modin[all]
RUN pip install s3fs

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial_notebooks /home/$NB_USER/
