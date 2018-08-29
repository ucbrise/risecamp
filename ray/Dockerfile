FROM ucbjey/risecamp2018-base:stable

USER $NB_USER

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python

RUN pip install https://s3-us-west-2.amazonaws.com/ray-wheels/9ad94e33d611905347522c493ad58fe0237c87a2/ray-0.4.0-cp36-cp36m-manylinux1_x86_64.whl

COPY tutorial /home/$NB_USER/ 
