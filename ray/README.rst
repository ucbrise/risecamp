Ray Tutorial
============

Exercises
---------

Each file ``exercises/exercise*.ipynb`` is a separate exercise.

Instructions are written in each file. To do each exercise, first run all of
the cells in the Jupyter notebook. Then modify the ones that need to be modified
in order to prevent any exceptions from being raised. Throughout these
exercises, you may find the `Ray documentation`_ helpful.

**Exercise 1:** Define a remote function, and execute multiple remote functions
in parallel.

**Exercise 2:** Execute remote functions in parallel with some dependencies.

**Exercise 3:** Call remote functions from within remote functions.

**Exercise 4:** Use actors to share state between tasks. See the documentation
on `using actors`_.

**Exercise 5:** Pass actor handles to tasks so that multiple tasks can invoke
methods on the same actor.

**Exercise 6:** Use ``ray.wait`` to ignore stragglers. See the
`documentation for wait`_.

**Exercise 7:** Use ``ray.wait`` to process tasks in the order that they finish.
See the `documentation for wait`_.

**Exercise 8:** Use ``ray.put`` to avoid serializing and copying the same
object into shared memory multiple times.

**Exercise 9:** Specify that an actor requires some GPUs. For a complete
example that does something similar, you may want to see the `ResNet example`_.

**Exercise 10:** Specify that a remote function requires certain custom
resources. See the documentation on `custom resources`_.

**Exercise 11:** Extract neural network weights from an actor on one process,
and set them in another actor. You may want to read the documentation on
`using Ray with TensorFlow`_.

**Exercise 12:** Pass object IDs into tasks to construct dependencies between
tasks and perform a tree reduce.

.. _`Anaconda Python distribution`: https://www.continuum.io/downloads
.. _`Ray documentation`: https://ray.readthedocs.io/en/latest/?badge=latest
.. _`documentation for wait`: https://ray.readthedocs.io/en/latest/api.html#ray.wait
.. _`using actors`: https://ray.readthedocs.io/en/latest/actors.html
.. _`using Ray with TensorFlow`: https://ray.readthedocs.io/en/latest/using-ray-with-tensorflow.html
.. _`ResNet example`: https://ray.readthedocs.io/en/latest/example-resnet.html
.. _`custom resources`: https://ray.readthedocs.io/en/latest/resources.html#custom-resources


More In-Depth Examples
----------------------

**Sharded Parameter Server:** This exercise involves implementing a parameter
server as a Ray actor, implementing a simple asynchronous distributed training
algorithm, and sharding the parameter server to improve throughput.

**Speed Up Pandas:** This exercise involves using `Modin`_ to speed up your
pandas workloads.

**MapReduce:** This exercise shows how to implement a toy version of the
MapReduce system on top of Ray.

.. _`Modin`: https://modin.readthedocs.io/en/latest/

RL Exercises
------------

**Exercise 1:** Introduction to Markov Decision Processes.

**Exercise 2:** Derivative free optimization.

**Exercise 3:** Introduction to proximal policy optimization (PPO).

**Exercise 4:** Introduction to asynchronous advantage actor-critic (A3C).

**Exercise 5:** Train a policy to play pong using RLlib. Deploy it using actors,
and play against the trained policy.
