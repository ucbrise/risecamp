FROM jupyter/pyspark-notebook

MAINTAINER Vikram Sreekanti <vsreekanti@gmail.com> version: 0.1

USER root

RUN apt-get update

# install java 8
RUN apt-get upgrade -y && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:webupd8team/java -y && \
    apt-get update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    apt-get install -y oracle-java8-installer && \
    apt-get clean

# install sbt
RUN echo "deb http://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823 
RUN apt-get update
RUN apt-get install -y sbt

# install python2
RUN apt-get install -y python2.7
RUN conda install -y GitPython

# install and set up postgres
RUN apt-get install -y postgresql
RUN sed 's/peer/trust/g' /etc/postgresql/9.5/main/pg_hba.conf > test.out
RUN sed 's/md5/trust/g' test.out > test2.out
RUN mv test2.out /etc/postgresql/9.5/main/pg_hba.conf 
RUN rm test.out

# install git
RUN apt-get install -y git
RUN git clone https://github.com/ground-context/ground
# TODO: change this once you cut a new release
RUN cd ground && sbt dist && cp modules/postgres/target/universal/ground-postgres-0.1.2-SNAPSHOT.zip /home/$NB_USER/ground-0.1.2.zip
RUN unzip ground-0.1.2.zip
RUN mv ground-postgres-0.1.2-SNAPSHOT ground-0.1.2
RUN rm ground-0.1.2.zip
RUN service postgresql start && sudo su -c "createuser ground -d -s" -s /bin/sh postgres  && sudo su -c "createdb ground" -s /bin/sh postgres && sudo su -c "createuser root -d -s" -s /bin/sh postgres && sudo su -c "createuser $NB_USER -d -s" -s /bin/sh postgres
RUN service postgresql start && cd ground/resources/scripts/postgres && python2.7 postgres_setup.py ground ground 

# install tmux
RUN apt-get install -y tmux

# miscellaneous installs
RUN apt-get install -y python3-pip
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install numpy

USER $NB_USER

# copy new files in
RUN mkdir /home/$NB_USER/risecamp/
COPY aboveground /home/$NB_USER/risecamp/aboveground
COPY ml/ /home/$NB_USER/risecamp/ml/
COPY *.sh /home/$NB_USER/
COPY *.ipynb /home/$NB_USER/risecamp/

RUN git clone https://github.com/ground-context/risecamp /home/$NB_USER/risecamp/repo

USER root
RUN chmod +x /home/$NB_USER/ground_start.sh

CMD cd /home/$NB_USER && ./ground_start.sh
