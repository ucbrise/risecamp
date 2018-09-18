FROM ucbjey/risecamp2018-base

USER root
RUN apt-get update
RUN apt-get install -y python-pydot python-pydot-ng graphviz

USER $NB_USER

RUN pip install tensorflow==1.7.0 && \
    pip install gym==0.10.5 && \
    pip install opencv-python && \
    pip install graphviz && \
    pip install gitpython && \
    pip install tqdm

RUN pip install ray==0.5.2

RUN touch a

RUN git clone https://github.com/ucbrise/flor
WORKDIR /home/$NB_USER
RUN git clone https://github.com/ground-context/grit
RUN git clone https://github.com/ground-context/client
ENV PYTHONPATH $PYTHONPATH:/home/$NB_USER/grit/python:/home/$NB_USER/client/python:/home/$NB_USER/flor

COPY pong_py_no_git /home/$NB_USER/

USER root
COPY tutorial /home/$NB_USER/
RUN chown $NB_USER /home/$NB_USER
