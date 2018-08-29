# Example RISECamp Project

This year’s RISECamp tutorials will be in Jupyter notebooks running on
Docker containers. We’ll use Docker Hub to coordinate builds, releases,
and updates, thereby avoiding the merging and coordination problems
encountered last year. Each project will be responsible for pushing
their own builds to a Docker Hub repository and maintaining a `stable`
tag pointing to their latest stable build.

# Getting Started

To create your RISECamp tutorial, please follow the following steps:

1.  Install [Docker](https://www.docker.com/get-started) on your laptop
    and start it.
2.  Clone [this](https://github.com/ucbrise/risecamp) repository and
    `cd` to the `example` directory.
3.  Type `make run`, and navigate to the URL given in the output. It
    should look something like this:

<!-- -->

    ****
    **** Notebook Login URL: http://127.0.0.1:8888/?token=7c1a0fe854ebeac88064b7e01e73420ed8d5be795af1b726
    ****

4.  If everything worked, you should see a Jupyter notebook with some
    interactive plots.
5.  Sign-up for a [Docker Hub](https://hub.docker.com) account and
    create a new “repository”, preferably with a name like
    `risecamp2018-$PROJECT`.
6.  Copy the contents of the `example/` directory to a new `$PROJECT/`
    directory for your project.
7.  Edit the `$PROJECT/Makefile` to set the `DOCKER_TAG` variable to the
    name of the repository created in the previous step.
8.  Edit the `Dockerfile` to install your software, and place your
    tutorials into the `tutorial/` subdirectory.
9.  Type `make run` to run the container.

# Deploying

TODO
