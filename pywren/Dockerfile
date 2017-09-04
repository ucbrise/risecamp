FROM jupyter/pyspark-notebook

USER root
RUN mkdir -p /opt/pywren
COPY config_encoder.py /opt/pywren/
COPY training.py /opt/pywren/
COPY pywren_start.sh /opt/pywren/
RUN chown $NB_USER /opt/pywren/
RUN chmod a+x /opt/pywren/config_encoder.py
RUN chmod a+x /opt/pywren/pywren_start.sh
RUN chmod a+r /opt/pywren/training.py

USER $NB_USER

COPY *.ipynb /home/$NB_USER/
RUN mkdir /home/$NB_USER/solution
COPY solution/*.ipynb /home/$NB_USER/solution/
RUN cd /opt/pywren && git clone https://github.com/pywren/pywren.git && pip install -e pywren/
ENV PYWREN_LOGLEVEL ERROR
ENV PYTHONPATH="/opt/pywren:${PYTHONPATH}"

CMD cd /opt/pywren/ && bash pywren_start.sh && cd /home/$NB_USER && start-notebook.sh
