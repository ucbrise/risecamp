FROM ucbjey/risecamp2018-base:2b580e66f1f7

# use apt-get as user "root" to install ubuntu packages
USER root
RUN apt-get update && apt-get install -y g++ openssh-client openssh-server dnsutils tcpdump tshark
RUN pip3 install pandas sklearn awscli pymongo
RUN git clone https://github.com/mc2-project/dmlc-core.git /home/dmlc-core
RUN git clone https://github.com/mc2-project/secure-xgboost.git /home/secure-xgboost && cd /home/secure-xgboost && git submodule init && git submodule update
RUN cd /home/secure-xgboost; make; cd python-package; python3 setup.py install
RUN aws s3 --no-sign-request --region=us-east-2 sync s3://risecamp2019-mc2/insurance /data/insurance
RUN groupadd tcpdump; addgroup $NB_USER tcpdump; chown root.tcpdump /usr/sbin/tcpdump; chmod 0750 /usr/sbin/tcpdump; setcap "CAP_NET_RAW+eip" /usr/sbin/tcpdump

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
RUN mkdir /home/$NB_USER/shared_data
EXPOSE 22
