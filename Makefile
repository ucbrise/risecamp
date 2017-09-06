DOCKER_TAG ?= risecamp2017

NOTEBOOK_BASE_URL ?= /
NOTEBOOK_AUTH_TOKEN ?= $(shell hexdump -e '"%x"' -n 24 /dev/urandom)

DOCKER_RUN_FLAGS = \
	--rm -p 0.0.0.0:8888:8888 \
	-p 3000:3000 \
	-v /tmp:/tmp \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--shm-size 64000m \
	-e "NOTEBOOK_AUTH_TOKEN=$(NOTEBOOK_AUTH_TOKEN)" \
	-e "NOTEBOOK_BASE_URL=$(NOTEBOOK_BASE_URL)" \
	# --env-file ./pywren-config.env \
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

.PHONY: debug
debug: build
	docker run -it $(DOCKER_RUN_FLAGS) "$(DOCKER_TAG)"

.PHONY: run
run: build
	docker run -it $(DOCKER_RUN_FLAGS) "$(DOCKER_TAG)"
