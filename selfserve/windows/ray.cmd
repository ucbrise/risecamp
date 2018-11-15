docker pull "ucbrise/risecamp2018-ray:latest"
@echo ************************************************************
@echo ***
@echo *** RISE Camp 2018
@echo ***
@echo *** Tutorial: ray
@echo *** Login URL: http://127.0.0.1:8080/camp/ray
@echo *** Password: risecamp2018
@echo ***
@echo ************************************************************
@echo
docker run --rm --detach --name risecamp_ray --user root -p 127.0.0.1:8080:8080 -v /var/run/docker.sock:/var/run/docker.sock --memory 16g --shm-size 16g -e "NOTEBOOK_FLAGS= --NotebookApp.password='sha1:3ec466c1b38d:6b4670be0553e483ca5ddde58bb4765c8ab40c10' --NotebookApp.allow_origin='*'" -e "CONTAINER_BASE_URL=camp/ray" -p 127.0.0.1:3000:3000 -p 127.0.0.1:6006:6006 -p 127.0.0.1:8889:8889 "ucbrise/risecamp2018-ray:latest"
