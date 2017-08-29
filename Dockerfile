# vim: set filetype=dockerfile:
FROM jupyter/pyspark-notebook


#### common
USER root

# add sbt repo
RUN echo "deb http://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823

# install deps
RUN apt-get update && apt-get install -y \
  python2.7 postgresql git tmux apt-transport-https ca-certificates curl software-properties-common \
  libzmq5 daemon python-pip graphviz
RUN pip2 install --upgrade pip

# add docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
      && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      && apt-get update
RUN apt-get install -y docker-ce
RUN gpasswd -a $NB_USER docker

# add sbt (after docker to get expected GIDs)
RUN apt-get install -y sbt


#### clipper
USER $NB_USER

RUN conda create -n py2 python=2 jupyter
RUN /bin/bash -c "source activate py2 && ipython kernel install --user"

RUN mkdir -p /home/$NB_USER/clipper
WORKDIR /home/$NB_USER/clipper
COPY clipper/setup/ setup/
COPY clipper/img/ img/
COPY clipper/tf_cifar_model/ tf_cifar_model/

ENV DATA cifar/

RUN mkdir -p $DATA \
      && /bin/bash -c "source activate py2 && conda install -y -q numpy pyzmq subprocess32 pandas matplotlib seaborn tensorflow"

RUN /bin/bash -c "source activate py2 && python ./setup/download_cifar.py $DATA \
      && python ./setup/extract_cifar.py $DATA 10000 10000"


RUN git clone https://github.com/ucbrise/clipper.git --branch risecamp-2017 --single-branch \
      && /bin/bash -c "source activate py2 && pip install -e ./clipper/clipper_admin_v2"


COPY \
  clipper/clipper_exercises.ipynb \
  clipper/query_cifar.ipynb \
  clipper/__init__.py \
  clipper/cifar_utils.py \
  ./

USER root
RUN chown jovyan:users -R /home/$NB_USER/clipper


#### ground
USER root

RUN mkdir -p /home/$NB_USER/ground
WORKDIR /home/$NB_USER/ground

RUN conda install -y GitPython

# install and set up postgres
RUN sed 's/peer/trust/g' /etc/postgresql/9.5/main/pg_hba.conf > test.out
RUN sed 's/md5/trust/g' test.out > test2.out
RUN mv test2.out /etc/postgresql/9.5/main/pg_hba.conf
RUN rm test.out

# install ground
RUN git clone https://github.com/ground-context/ground
RUN wget https://github.com/ground-context/ground/releases/download/v0.1.1/ground-0.1.1.zip
RUN unzip ground-0.1.1.zip
RUN rm ground-0.1.1.zip
RUN service postgresql start && sudo su -c "createuser ground -d -s" -s /bin/sh postgres  && sudo su -c "createdb ground" -s /bin/sh postgres
RUN service postgresql start && cd ground/resources/scripts/postgres && python2.7 postgres_setup.py ground ground

# copy new files in
RUN mkdir -p /home/$NB_USER/ground/
COPY ground/*.py /home/$NB_USER/ground/
COPY ground/config.ini /home/$NB_USER/ground/
COPY ground/*.sh /home/$NB_USER/ground
COPY ground/Ground.ipynb /home/$NB_USER/ground/

RUN chmod +x /home/$NB_USER/ground/ground_start.sh


#### ray
USER $NB_USER

RUN pip install ray && \
    pip install tensorflow==1.3.0 && \
    pip install gym==0.9.2

RUN mkdir -p /home/$NB_USER/ray
COPY ray/ray-test.ipynb /home/$NB_USER/ray/
COPY ray/tutorial /home/$NB_USER/ray/


#### wave
USER root
RUN pip2 install msgpack-python requests pytz ipywidgets
RUN jupyter nbextension enable --py  --sys-prefix widgetsnbextension
RUN mkdir -p /home/$NB_USER/.ipynb_checkpoints /home/$NB_USER/wave
COPY wave/getentity.py /usr/local/bin/
COPY wave/getaccess /home/$NB_USER
# FIXME: rename to start-wave.sh?
COPY wave/start.sh /usr/local/bin/
COPY wave/ragent /bin/
RUN chmod 0755 /bin/ragent
COPY wave/bw2 /bin/
COPY wave/bw2lint /bin/
COPY wave/rise_entity.ent /etc/
COPY wave/WAVE.ipynb /home/$NB_USER/wave
COPY wave/ExamineNamespace.ipynb /home/$NB_USER/wave

ADD wave/images /home/$NB_USER/wave/images
ADD wave/python /home/$NB_USER/wave
ENV PYTHONPATH /home/$NB_USER/wave/python
RUN rm -f /home/$NB_USER/.bw2bind.log
RUN chown -R $NB_USER:users /home/$NB_USER/wave


#### pywren
USER $NB_USER
RUN mkdir -p /home/$NB_USER/pywren
COPY pywren/pywren-risecamp.ipynb /home/$NB_USER/pywren


#### finalize
COPY ./risecamp_start.sh /opt
CMD cd /home/$NB_USER && /opt/risecamp_start.sh

USER root
RUN chown -R $NB_USER:users /home/$NB_USER
