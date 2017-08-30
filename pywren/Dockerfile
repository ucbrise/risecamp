FROM jupyter/pyspark-notebook
COPY pywren-risecamp.ipynb /home/$NB_USER

RUN pip install pywren

COPY config_encoder.py /home/$NB_USER/config_encoder.py
COPY pywren_start.sh /home/$NB_USER/pywren_start.sh


CMD cd /home/$NB_USER && bash pywren_start.sh && start-notebook.sh