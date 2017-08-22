FROM continuumio/miniconda

COPY setup/ /home/$NB_USER/setup/
WORKDIR /home/$NB_USER
ENV DATA /home/$NB_USER/cifar


RUN mkdir -p $DATA \
      && conda install numpy \
      && python ./setup/download_cifar.py $DATA \
      && python ./setup/extract_cifar.py $DATA 10000 10000

RUN apt-get update \
      && apt-get install -y libzmq3 libzmq3-dev \
      && conda install -y pyzmq subprocess32

RUN git clone https://github.com/ucbrise/clipper.git --branch risecamp-2017 --single-branch \
      && pip install -e ./clipper/clipper_admin_v2

COPY clipper_exercises.ipynb /home/$NB_USER/


