# RISECamp Tutorials

## Quickstart

If you're already familiar with Docker and Jupyter, here's the high-order bits:

  * Derive your Docker image from `jupyter/base-notebook`.
  * Consult the `hello-world` directory for an example.
  * Submit a pull request that adds your tutorial as a subdirectory to this repository.


## Getting Started

### How to run the `hello-world` example:

1. Install Docker: https://docs.docker.com/engine/installation/

2. Build the `hello-world` image:
    ```
    $ docker build hello-world/
    ```

3. You will see output similar to the following. Take note of the Docker image
   ID printed at the end, in this case `21a65a239ed6`.

        $ docker build hello-world/
        Sending build context to Docker daemon  6.656kB
        Step 1/2 : FROM jupyter/pyspark-notebook
         ---> 93262f647bcc
        Step 2/2 : COPY Hello-World.ipynb /home/$NB_USER
         ---> Using cache
         ---> 21a65a239ed6
        Successfully built 21a65a239ed6

4. Use the ID from the previous step to launch the container:
    ```
    $ docker run -it --rm -p 8888:8888 21a65a239ed6
    ```

5. Open the URL output by the container, which looks something like:
    ```
    http://localhost:8888/?token=3e18614852cd453007d747c83757c125e512b770a1df7e70
    ```

6. You'll see a Jupyter instance with a "Hello-World" notebook in it. This
notebook derives from
[`jupyter/pyspark-notebook`](https://github.com/jupyter/docker-stacks/blob/master/pyspark-notebook/Dockerfile),
which derives from `jupyter/base-notebook`.

### Adding a new tutorial:

Create a new subdirectory within this repository, following the examples
provided by the `hello-world` and `pyspark-notebook` containers.

Any background setup required by your project (e.g. libraries, daemons, etc)
should be performed in the Dockerfile. All instructional content should live in
the Jupyter notebook.
