FROM jupyter/pyspark-notebook

USER root
RUN mkdir -p /pywren-setup
COPY config_encoder.py /pywren-setup/
COPY pywren_start.sh /pywren-setup/
RUN chown $NB_USER /pywren-setup
RUN chmod a+x /pywren-setup/config_encoder.py
RUN chmod a+x /pywren-setup/pywren_start.sh

USER $NB_USER

COPY pywren-risecamp.ipynb /home/$NB_USER
RUN pip install pywren
ENV PYWREN_LOGLEVEL INFO

CMD cd /pywren-setup && bash pywren_start.sh && cd /home/$NB_USER && start-notebook.sh