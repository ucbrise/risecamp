#!/bin/bash

RUN echo "[default]" > /home/$NB_USER/.aws/credentials
RUN echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> /home/$NB_USER/.aws/credentials
RUN echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> /home/$NB_USER/.aws/credentials
RUN cat ~/.aws/credentials
RUN pywren create-config
RUN sed -i s/" bucket:.*"/" bucket: `python -c 'import random; print("".join(random.choice("abcdefghijkl") for i in range(30)))'`"/ /home/$NB_USER/.pywren_config
RUN pywren create-bucket
RUN pywren create-role
RUN pywren deploy-lambda
