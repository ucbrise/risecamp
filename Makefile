.PHONY: default
default: run

.PHONY: build
build:
	docker build --tag risecamp2017 .
	
.PHONY: run
run: build
	docker run --rm -p 0.0.0.0:8888:8888 -v /tmp:/tmp -v /var/run/docker.sock:/var/run/docker.sock --shm-size 64000m -e GRANT_SUDO=yes risecamp2017
