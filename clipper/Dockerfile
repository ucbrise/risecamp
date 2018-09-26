FROM ucbjey/risecamp2018-base

USER $NB_USER

RUN pip install numpy scipy scikit-learn && \
		pip install pillow && \
		pip install cloudpickle==0.5.3 && \
		pip install jupyterlab && \
		pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin && \
		pip install torch==0.4.0 torchvision && \
		pip install matplotlib

COPY tutorial /home/$NB_USER/
