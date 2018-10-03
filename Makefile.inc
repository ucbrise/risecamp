# vim: filetype=make

CURPROJ ?= $(shell basename $(CURDIR))

CONTAINER_AUTH_TOKEN := $(shell hexdump -e '"%x"' -n 24 /dev/urandom)
CONTAINER_BASE_URL := "camp/$(CURPROJ)"

DOCKER_RUN_FLAGS = \
	--rm \
	--name "risecamp_$(CURPROJ)" \
	-p 8080:8080 \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--shm-size 64000m \
	-e "CONTAINER_AUTH_TOKEN=$(CONTAINER_AUTH_TOKEN)" \
	-e "CONTAINER_BASE_URL=$(CONTAINER_BASE_URL)" \
	#

DOCKER_BUILD_FLAGS = \
	--tag "$(DOCKER_TAG)" \
	#

.PHONY: default
default: debug

.PHONY: build
build:
	docker build $(DOCKER_BUILD_FLAGS) .

.PHONY: clean-build
clean-build:
	docker build --no-cache --pull $(DOCKER_BUILD_FLAGS) .

.PHONY: run
run: build
	docker run -it --user=root $(DOCKER_RUN_FLAGS) "$(DOCKER_TAG)"
