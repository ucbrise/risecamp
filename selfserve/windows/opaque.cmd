docker pull "ucbrise/risecamp2018-opaque:latest"
@echo ************************************************************
@echo ***
@echo *** RISE Camp 2018
@echo ***
@echo *** Tutorial: opaque
@echo *** Login URL: http://127.0.0.1:8080/camp/opaque
@echo *** Password: risecamp2018
@echo ***
@echo ************************************************************
@echo
docker run --rm --detach --name risecamp_opaque --user root -p 127.0.0.1:8080:8080 -v /var/run/docker.sock:/var/run/docker.sock --memory 16g --shm-size 16g -e "NOTEBOOK_FLAGS= --NotebookApp.password='sha1:3ec466c1b38d:6b4670be0553e483ca5ddde58bb4765c8ab40c10' --NotebookApp.allow_origin='*'" -e "CONTAINER_BASE_URL=camp/opaque" "ucbrise/risecamp2018-opaque:latest"
