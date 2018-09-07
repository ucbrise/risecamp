FROM ucbjey/risecamp2018-base

USER $NB_USER

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python

RUN pip install ray==0.5.2

COPY pong_py_no_git /home/$NB_USER/
