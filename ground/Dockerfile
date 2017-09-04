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


RUN wget https://github.com/ground-context/ground/releases/download/v0.1.2/ground-0.1.2.zip
RUN unzip ground-0.1.2.zip
RUN rm ground-0.1.2.zip
RUN service postgresql start && sudo su -c "createuser ground -d -s" -s /bin/sh postgres  && sudo su -c "createdb ground" -s /bin/sh postgres && sudo su -c "createuser root -d -s" -s /bin/sh postgres && sudo su -c "createuser $NB_USER -d -s" -s /bin/sh postgres
RUN service postgresql start && cd ground-0.1.2/db && python2.7 postgres_setup.py ground ground 

# miscellaneous installs
RUN apt-get install -y python3-pip
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install requests

RUN apt-get install -y python-pip
RUN pip2 install psycopg2
RUN pip2 install requests
RUN pip2 install numpy
RUN pip2 install pandas
RUN pip2 install tweet_preprocessor
RUN pip2 install scipy
RUN pip2 install -U scikit-learn
RUN pip2 install HTMLParser

# install git & tmux
RUN apt-get install -y git 
RUN apt-get install -y tmux

USER $NB_USER

# copy new files in
RUN mkdir /home/$NB_USER/risecamp/
COPY aboveground /home/$NB_USER/risecamp/aboveground
COPY ml/ /home/$NB_USER/risecamp/ml/
COPY images/ /home/$NB_USER/risecamp/images
COPY *.sh /home/$NB_USER/
COPY *.ipynb /home/$NB_USER/risecamp/

RUN git clone https://github.com/ground-context/risecamp /home/$NB_USER/risecamp/repo

USER root
RUN chmod +x /home/$NB_USER/ground_start.sh
RUN chmod +x /home/$NB_USER/ground-0.1.2/bin/ground-postgres
RUN chown -R $NB_USER /home/$NB_USER/risecamp/

CMD cd /home/$NB_USER && ./ground_start.sh
