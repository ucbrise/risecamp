FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update && apt-get install -y g++ && apt-get -y install openssh-client
RUN git clone https://github.com/mc2-project/risecamp-data.git /data

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN pip3 install xgboost && pip3 install pandas && pip3 install sklearn
RUN git clone https://github.com/mc2-project/dmlc-core.git /home/$NB_USER/dmlc-core
RUN ssh-keygen -q -t rsa -b 4096 -N '' -f /home/$NB_USER/.ssh/id_rsa

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
