# FROM continuumio/miniconda

FROM jupyter/base-notebook
USER root
RUN apt-get update && apt-get install -yqq libzmq5 git \
      apt-transport-https ca-certificates curl software-properties-common \
      && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
      && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      && apt-get update \
      && apt-get install -yqq docker-ce

RUN gpasswd -a $NB_USER docker

USER $NB_USER

RUN conda create -n py2 python=2 jupyter
RUN /bin/bash -c "source activate py2 && ipython kernel install --user"

WORKDIR /home/$NB_USER

COPY setup/ setup/
COPY img/ img/
COPY tf_cifar_model/ tf_cifar_model/ 

ENV DATA cifar/

RUN mkdir -p $DATA \
      && /bin/bash -c "source activate py2 && conda install -y -q numpy pyzmq subprocess32 pandas matplotlib seaborn tensorflow"

RUN /bin/bash -c "source activate py2 && python ./setup/download_cifar.py $DATA \
      && python ./setup/extract_cifar.py $DATA 10000 10000"


# TODO: update to pip install clipper==0.2.0 once the Clipper release is pushed
RUN /bin/bash -c "source activate py2 && \
      pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin"


COPY clipper_exercises.ipynb query_cifar.ipynb __init__.py cifar_utils.py \
      ./

USER root
RUN chown jovyan:users -R /home/$NB_USER/
USER $NBUSER

# vim: set filetype=dockerfile:
#
