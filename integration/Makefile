include ../Makefile.inc

DOCKER_TAG ?= vsreekanti/integration-risecamp18

# We use integration network to comminicate with our containers
# We use /tmp directory to store artifact for container building
DOCKER_RUN_FLAGS += --network=integration_network -v /tmp:/tmp
