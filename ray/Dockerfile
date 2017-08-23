FROM jupyter/pyspark-notebook

MAINTAINER Alexey Tumanov <atumanov@gmail.com>

RUN pip install ray && \
    pip install tensorflow==1.3.0 && \
    pip install gym==0.9.2

COPY ray-test.ipynb /home/$NB_USER
COPY tutorial/ /home/$NB_USER/tutorial
