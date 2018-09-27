FROM ucbjey/risecamp2018-base

# use apt-get as user "root" to install ubuntu packages
USER root

# use "$NB_USER" when installing python packages
USER $NB_USER
RUN git clone https://github.com/pywren/pywren.git /home/$NB_USER/pywren
RUN pip install -e /home/$NB_USER/pywren
RUN mkdir -p /home/$NB_USER/.aws
COPY credentials /home/$NB_USER/.aws/credentials
RUN pywren create-config
RUN sed -i s/" bucket:.*"/" bucket: `python -c 'import random; print("".join(random.choice("abcdefghijkl") for i in range(30)))'`"/ /home/$NB_USER/.pywren_config
RUN pywren create-role
RUN pywren create-bucket
RUN pywren deploy-lambda

# copy the tutorial into the container.
# do this last so that your container builds are as fast as possible
# when updating the content in tutorial/
COPY tutorial /home/$NB_USER/
