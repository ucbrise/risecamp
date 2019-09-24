FROM continuumio/miniconda3

RUN conda update -n base -c defaults conda
RUN conda install -c conda-forge psutil setproctitle
RUN pip install modin[all]

# configure httpd
USER root

