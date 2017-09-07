# vim: set filetype=dockerfile:
FROM jupyter/pyspark-notebook:786611348de1


#### common
USER root

# add sbt repo
RUN echo "deb http://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823

# install deps
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
  python2.7 postgresql git tmux apt-transport-https ca-certificates curl software-properties-common \
  daemon python-pip graphviz apt-utils net-tools vim git wget cmake pkg-config build-essential libboost-all-dev \
  unzip libzmq5-dev zlib1g-dev

RUN pip2 install --upgrade pip
RUN python2 -m pip install ipython==5.4 ipykernel
RUN pip2 install numpy msgpack-python requests pytz ipywidgets

# add docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
      && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      && apt-get update
RUN apt-get install -y docker-ce
RUN gpasswd -a $NB_USER docker

# add sbt (after docker to get expected GIDs)
RUN apt-get install -y sbt

USER $NB_USER
RUN python2 -m ipykernel install --user

#### clipper
USER $NB_USER
RUN mkdir -p /home/$NB_USER/clipper
WORKDIR /home/$NB_USER/clipper

RUN conda create -n clipper_py2 python=2 jupyter
RUN /bin/bash -c "source activate clipper_py2 && \
        ipython kernel install --user --name clipper_py2 --display-name \"Python 2 for Clipper\""

COPY clipper/setup/ setup/
COPY clipper/img/ img/
COPY clipper/tf_cifar_model/ tf_cifar_model/

ENV DATA cifar/

RUN mkdir -p cifar/ \
      && /bin/bash -c "source activate clipper_py2 && \
        conda install -y -q libgcc numpy pyzmq subprocess32 pandas matplotlib seaborn tensorflow scikit-learn && \
        pip install ray==0.2.0 tensorflow==1.3.0 gym==0.9.2 smart_open"

RUN /bin/bash -c "source activate clipper_py2 && python ./setup/download_cifar.py cifar/ && \
      python ./setup/extract_cifar.py cifar/ 10000 10000"

# TODO: update to pip install clipper==0.2.0 once the Clipper release is pushed
RUN /bin/bash -c "source activate clipper_py2 && \
      pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin"

COPY clipper/clipper_exercises.ipynb \
      clipper/query_cifar.ipynb \
      clipper/__init__.py \
      clipper/cifar_utils.py \
      clipper/get_docker_ip.sh \
      ./


#### ray
USER root
RUN sudo mkdir /tmp1
RUN sudo chmod 777 /tmp1

USER $NB_USER

RUN pip install tensorflow==1.3.0 && \
    pip install gym==0.9.2 && \
    pip install smart_open && \
    pip install opencv-python && \
    pip install scipy

RUN pip install git+https://github.com/robertnishihara/ray.git@87695eb3466cabfe2aa81ef49a9c8dbe392e79e0#subdirectory=python

RUN git clone https://github.com/catapult-project/catapult.git /tmp1/ray/catapult
RUN git -C /tmp1/ray/catapult checkout 33a9271eb3cf5caf925293ec6a4b47c94f1ac968

RUN mkdir -p /home/$NB_USER/ray
COPY ray/ray-test.ipynb /home/$NB_USER/ray/
COPY ray/tutorial /home/$NB_USER/ray/


#### pong
USER $NB_USER
RUN mkdir -p /home/$NB_USER/pong
WORKDIR /home/$NB_USER/pong
COPY pong/rl_exercise01.ipynb pong/rl_exercise02.ipynb pong/rl_exercise03.ipynb pong/rl_exercise04.ipynb pong/start_webserver.sh pong/get_docker_ip.sh ./
COPY pong/pong_py_no_git/ ./pong_py_no_git
COPY pong/javascript-pong/ ./javascript-pong
RUN /bin/bash -c "source activate clipper_py2 && pip install ./pong_py_no_git"


#### wave
USER root
RUN conda install -y ipywidgets
RUN python2 -m jupyter nbextension enable --py  --sys-prefix widgetsnbextension
RUN mkdir -p /home/$NB_USER/.ipynb_checkpoints /home/$NB_USER/wave
COPY wave/getentity.py /usr/local/bin/
COPY wave/getaccess /home/$NB_USER/wave
COPY wave/ragent /bin/
COPY wave/wave_start.sh /home/$NB_USER/wave
RUN chmod 0755 /bin/ragent
COPY wave/bw2 /bin/
COPY wave/bw2 /bin/wave
COPY wave/bw2lint /bin/
COPY wave/rise_entity.ent /etc/
COPY wave/WAVE.ipynb /home/$NB_USER/wave
COPY wave/ExamineNamespace.ipynb /home/$NB_USER/wave

ADD wave/images /home/$NB_USER/wave/images
ADD wave/python /home/$NB_USER/wave
ENV PYTHONPATH /home/$NB_USER/wave/python
RUN rm -f /home/$NB_USER/.bw2bind.log


#### pywren
USER root
RUN mkdir -p /home/$NB_USER/pywren
RUN mkdir -p /opt/pywren
COPY pywren/config_encoder.py /opt/pywren/
COPY pywren/training.py /opt/pywren/
COPY pywren/matrix.py /opt/pywren/
COPY pywren/pywren_start.sh /opt/pywren/
RUN chown $NB_USER /opt/pywren
RUN chmod a+x /opt/pywren/config_encoder.py
RUN chmod a+x /opt/pywren/training.py
RUN chmod a+x /opt/pywren/matrix.py
RUN chmod a+x /opt/pywren/pywren_start.sh

USER $NB_USER
COPY pywren/*.ipynb /home/$NB_USER/pywren/
RUN cd /opt/pywren && git clone https://github.com/pywren/pywren.git && pip install -e pywren/
ENV PYWREN_LOGLEVEL ERROR
ENV PYTHONPATH="/opt/pywren:${PYTHONPATH}"


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
RUN apt-get install -y openjdk-8-jdk
RUN wget https://github.com/ground-context/ground/releases/download/v0.1.2/ground-0.1.2.zip
RUN unzip ground-0.1.2.zip
RUN rm ground-0.1.2.zip
RUN service postgresql start && sudo su -c "createuser ground -d -s" -s /bin/sh postgres  && sudo su -c "createdb ground" -s /bin/sh postgres && sudo su -c "createuser root -d -s" -s /bin/sh postgres && sudo su -c "createuser $NB_USER -d -s" -s /bin/sh postgres
RUN service postgresql start && cd ground-0.1.2/db && python2.7 postgres_setup.py ground ground

# miscellaneous installs
RUN apt-get install -y python3-pip python-pip
RUN pip3 install pandas numpy requests
RUN pip2 install psycopg2 requests numpy pandas tweet_preprocessor scipy HTMLParser
RUN pip2 install -U scikit-learn

# copy new files in
COPY ground/aboveground /home/$NB_USER/ground/risecamp/aboveground
COPY ground/ml/ /home/$NB_USER/ground/risecamp/ml/
COPY ground/images/ /home/$NB_USER/ground/risecamp/images
COPY ground/*.sh /home/$NB_USER/ground/
COPY ground/*.ipynb /home/$NB_USER/ground/risecamp/

RUN git clone https://github.com/ground-context/risecamp /home/$NB_USER/risecamp/repo
RUN chmod +x ground-0.1.2/bin/ground-postgres


#### finalize
COPY ./risecamp_start.sh /opt
#COPY ./.jupyter /home/$NB_USER/.jupyter

USER root
RUN chown -R $NB_USER:users /home/$NB_USER
RUN rmdir /home/$NB_USER/work

WORKDIR /home/$NB_USER
USER $NB_USER
RUN pip install jupyterhub==0.7.2
USER root
CMD cd /home/$NB_USER && /opt/risecamp_start.sh
