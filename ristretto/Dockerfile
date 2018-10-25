FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get install -y g++
RUN apt-get install libproj-dev -y
RUN apt-get install libgeos-dev -y

# use "$NB_USER" when installing python packages
USER $NB_USER
#RUN pip install bokeh==0.13.0
RUN pip install git+https://github.com/erichson/ristretto
RUN pip install tqdm
RUN pip install h5py
RUN pip install cmocean
RUN pip install netCDF4
RUN pip install git+https://github.com/matplotlib/basemap

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/



