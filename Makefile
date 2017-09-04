.PHONY: default
default: run

.PHONY: build
build:
	docker build --tag risecamp2017 .
	
.PHONY: run
run: build
	docker run --rm -p 8888:8888 -v /var/run/docker.sock:/var/run/docker.sock --shm-size 2048m risecamp2017
