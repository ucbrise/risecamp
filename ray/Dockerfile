FROM jupyter/pyspark-notebook

MAINTAINER Alexey Tumanov <atumanov@gmail.com>

RUN pip install ray==0.2.0 && \
    pip install tensorflow==1.3.0 && \
    pip install gym==0.9.2 && \
    pip install smart_open && \
    pip install opencv-python && \
    pip install scipy

COPY ray-test.ipynb /home/$NB_USER
COPY tutorial/ /home/$NB_USER/tutorial
