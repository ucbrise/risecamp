DOCKER_FLAGS= \
	--rm -p 0.0.0.0:8888:8888 \
	-v /tmp:/tmp \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--shm-size 64000m \
	-e GRANT_SUDO=yes \
	-e "PYWREN_CONFIG_STRING=$(PYWREN_CONFIG_STRING)" \
	#

.PHONY: default
default: debug

.PHONY: build
build:
	docker build --tag risecamp2017 .
	
.PHONY: debug
debug: build
	docker run -it $(DOCKER_FLAGS) risecamp2017

.PHONY: run
run: build
	docker run -it $(DOCKER_FLAGS) risecamp2017
