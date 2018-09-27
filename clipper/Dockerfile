FROM ucbjey/risecamp2018-base

USER root

RUN apt-get remove docker && \
		apt-get install docker-ce && \
		curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
		chmod +x /usr/local/bin/docker-compose

USER $NB_USER

RUN	pip install numpy scipy scikit-learn && \
		pip install pillow && \
		pip install cloudpickle==0.5.3 && \
		pip install jupyterlab && \
		pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin && \
		pip install torch==0.4.0 torchvision && \
		pip install matplotlib

COPY tutorial /home/$NB_USER/
