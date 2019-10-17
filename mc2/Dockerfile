FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update && apt-get install -y g++ openssh-client openssh-server dnsutils
RUN pip3 install pandas sklearn awscli pymongo jupyter_contrib_nbextensions ipywidgets
RUN git clone https://github.com/mc2-project/secure-xgboost.git /home/secure-xgboost && cd /home/secure-xgboost && git submodule init && git submodule update
RUN cd /home/secure-xgboost; make; cd python-package; python3 setup.py install
RUN jupyter contrib nbextension install --user; jupyter nbextension enable init_cell/main
RUN git clone -b risecamp2019 https://github.com/mc2-project/dmlc-core.git /home/dmlc-core
RUN aws s3 --no-sign-request --region=us-east-2 sync s3://risecamp2019-mc2/hb /data/hb

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN ssh-keygen -q -t rsa -b 4096 -N '' -f /home/$NB_USER/.ssh/id_rsa

# perform boot-time initialization by adding a startup script
COPY init-world.sh /usr/local/bin/start-notebook.d

# configure httpd
COPY nginx.conf /etc/nginx/sites-enabled/default

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/

USER root
RUN jupyter trust /home/$NB_USER/exercise0.ipynb

USER $NB_USER
EXPOSE 22
EXPOSE 9000-9100

