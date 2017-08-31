# Instructions

The Clipper exercises expect a couple additional arguments to `docker run`
when running the Jupyter notebook docker container.

## Build

Building the Docker image does not require any special instructions:

```
docker build -t risecamp/clipper .
```

## Run

The container must be run with the following command:

```
docker run -it --network=host -v /var/run/docker.sock:/var/run/docker.sock -p 8888:8888 clipper/risecamp
```

Explanation of additional args:

+ `--network=host` useallows the Jupyter docker container to access the
Clipper docker containers on `localhost`. 
+ `-v /var/run/docker.sock:/var/run/docker.sock` gives the Jupyter docker container
access to the Docker daemon so it can launch sibling Docker containers on the host.

