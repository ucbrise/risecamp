FROM jupyter/pyspark-notebook

USER root
RUN apt-get update && apt-get install -y daemon python-pip graphviz

RUN ln -sf python2 `which python`
RUN python2 -m pip install ipython==5.4 ipykernel
RUN python2 -m ipykernel install --user
RUN pip2 install --upgrade pip
RUN pip2 install msgpack-python requests pytz ipywidgets
RUN jupyter nbextension enable --py  --sys-prefix widgetsnbextension
RUN chown -R $NB_USER /home/$NB_USER/.local/share/jupyter
RUN mkdir -p /home/$NB_USER/.ipynb_checkpoints
RUN chown -R $NB_USER /home/$NB_USER/.ipynb_checkpoints
RUN chown -R $NB_USER /home/$NB_USER

COPY getentity.py /usr/local/bin/
COPY getaccess /home/$NB_USER
COPY start.sh /usr/local/bin/
COPY ragent /bin/
RUN chmod 0755 /bin/ragent
COPY bw2 /bin/
COPY bw2lint /bin/
COPY rise_entity.ent /etc/
COPY WAVE.ipynb /home/$NB_USER
COPY ExamineNamespace.ipynb /home/$NB_USER

ADD images /home/$NB_USER/images
ADD python /home/$NB_USER/
ENV PYTHONPATH /home/$NB_USER/python
RUN chown -R $NB_USER /home/$NB_USER
RUN rm -f /home/$NB_USER/.bw2bind.log

