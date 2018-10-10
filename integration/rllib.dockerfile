# vim: set filetype=dockerfile:
ARG REGISTRY
ARG CODE_VERSION
ARG RPC_VERSION
FROM ${REGISTRY}/${RPC_VERSION}-rpc:${CODE_VERSION}

RUN apt-get update && apt-get install -y cmake build-essential
RUN apt-get install -y zlib1g-dev

RUN pip install tensorflow ray[rllib]==0.5.2
RUN apt-get install -y libgtk2.0-dev

COPY rllib_container/rllib_container.py rllib_container/container_entry.sh /container/
RUN chmod +x /container/container_entry.sh
RUN chmod +x /container/rllib_container.py

COPY pong_py_no_git /container/pong_py
RUN cd /container/pong_py && pip install .
CMD ["/container/container_entry.sh", "rllib-container", "/container/rllib_container.py"]

