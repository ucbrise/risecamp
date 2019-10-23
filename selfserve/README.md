# RISECamp 2019 Tutorials (Self-Serve)

This directory contains scripts that can be used to run the RISECamp 2019
tutorials at home on your own computer.

## MacOS and Linux

### Ray

For the Ray tutorials, please see the following links:

<ol>
<li>Ray
	<ol type="a">
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/exercises/colab01-03.ipynb" target="_blank">Remote functions</a></li>
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/exercises/colab04-05.ipynb" target="_blank">Remote actors</a></li>
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/exercises/colab06-07.ipynb" target="_blank">In-order task processing</a></li>
	</ol>
</li>
<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/rllib_exercises/rllib_colab.ipynb">RLLib</a></li>

<li>Tune
	<ol type="a">
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/tune_exercises/exercise_1_basics.ipynb" target="_blank">Learning how to use Tune</a></li>
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/tune_exercises/exercise_2_optimize.ipynb" target="_blank">Accelerated Hyperparameter Tuning For PyTorch</a></li>
		<li><a href="https://colab.research.google.com/github/ray-project/tutorial/blob/master/tune_exercises/exercise_3_pbt.ipynb" target="_blank">Population-Based Training</a></li>
	</ol>
</li>
</ol>


### Modin, Autopandas, and MC2
1. Install and start [Docker CE](https://docs.docker.com/install/).
2. Open a terminal and `cd` to this directory.
3. Use the `./runtutorial [name]` script to start the tutorial. Valid tutorials
   are `modin|autopandas|mc2`.
4. Once the container has finished booting, you'll see output like this with
   the URL and password to access the selected tutorial:

		************************************************************
		***
		*** RISE Camp 2019
		***
		*** Tutorial: ray
		*** Login URL: http://127.0.0.1:8080/camp/ray
		*** Password: risecamp2019
		***
		************************************************************

5. Press Control-C when finished to shutdown the tutorial.
