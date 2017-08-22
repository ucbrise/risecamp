FROM jupyter/pyspark-notebook

MAINTAINER Alexey Tumanov <atumanov@gmail.com>

RUN pip install ray && \
    pip install tensorflow && \
    pip install gym

COPY ray-test.ipynb /home/$NB_USER
COPY tutorial/ /home/$NB_USER/tutorial
