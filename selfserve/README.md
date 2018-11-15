# RISECamp 2018 Tutorials (Self-Serve)

This directory contains scripts that can be used to run the RISECamp 2018
tutorials at home on your own computer.

## MacOS and Linux

1. Install and start [Docker CE](https://docs.docker.com/install/).
2. Open a terminal and `cd` to this directory.
3. Use the `runtutorial [name]` script to start the tutorial. Valid tutorials
   are `clipper|flor|integration|opaque|pywren|ray|wave`.
4. Once the container has finished booting, you'll see output like this with
   the URL and password to access the selected tutorial:

			************************************************************
			***
			*** RISE Camp 2018
			***
			*** Tutorial: ray
			*** Login URL: http://127.0.0.1:8080/camp/ray
			*** Password: risecamp2018
			***
			************************************************************

5. Press Control-C when finished to shutdown the tutorial.
