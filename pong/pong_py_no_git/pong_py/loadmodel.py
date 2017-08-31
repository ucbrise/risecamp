# python ray/python/ray/rllib/train.py --alg=PolicyGradient --config='{"model": {"fcnet_hiddens": [32, 32]}}'

import os
import time

import numpy as np
import tensorflow as tf

import ray
from ray.rllib.common import Algorithm, TrainingResult
from ray.rllib.policy_gradient.agent import Agent, RemoteAgent
from ray.rllib.policy_gradient.env import (
    NoPreprocessor, AtariRamPreprocessor, AtariPixelPreprocessor)
from ray.rllib.policy_gradient.rollout import collect_samples
from ray.rllib.policy_gradient.utils import shuffle


DEFAULT_CONFIG = {
    # Discount factor of the MDP
    "gamma": 0.995,
    # Number of steps after which the rollout gets cut
    "horizon": 2000,
    # GAE(lambda) parameter
    "lambda": 1.0,
    # Initial coefficient for KL divergence
    "kl_coeff": 0.2,
    # Number of SGD iterations in each outer loop
    "num_sgd_iter": 30,
    # Stepsize of SGD
    "sgd_stepsize": 5e-5,
    # TODO(pcm): Expose the choice between gpus and cpus
    # as a command line argument.
    "devices": ["/cpu:%d" % i for i in range(4)],
    "tf_session_args": {
        "device_count": {"CPU": 4},
        "log_device_placement": False,
        "allow_soft_placement": True,
    },
    # Batch size for policy evaluations for rollouts
    "rollout_batchsize": 1,
    # Total SGD batch size across all devices for SGD
    "sgd_batchsize": 128,
    # Coefficient of the entropy regularizer
    "entropy_coeff": 0.0,
    # PPO clip parameter
    "clip_param": 0.3,
    # Target value for KL divergence
    "kl_target": 0.01,
    "model": {"free_logstd": False},
    # Number of timesteps collected in each outer loop
    "timesteps_per_batch": 40000,
    # Each tasks performs rollouts until at least this
    # number of steps is obtained
    "min_steps_per_task": 1000,
    # Number of actors used to collect the rollouts
    "num_agents": 5,
    # Dump TensorFlow timeline after this many SGD minibatches
    "full_trace_nth_sgd_batch": -1,
    # Whether to profile data loading
    "full_trace_data_load": False,
    # If this is True, the TensorFlow debugger is invoked if an Inf or NaN
    # is detected
    "use_tf_debugger": False,
    # If True, we write checkpoints and tensorflow logging
    "write_logs": True,
    # Name of the model checkpoint file
    "model_checkpoint_file": "iteration-%s.ckpt"}


config = DEFAULT_CONFIG
config["model"]["fcnet_hiddens"] = [32, 32]

#dirname = "/tmp/ray/HIHIHI_PolicyGradient_2017-08-19_23-11-54x6m9b1il"
dirname = "/tmp/ray/HIHIHI_PolicyGradient_2017-08-20_02-53-02vwr5ax_v"
#dirname = "tmp_checkpoints/"

model = Agent("HIHIHI", 1, NoPreprocessor(), config, dirname, False)

saver = tf.train.Saver(max_to_keep=None)
saver.restore(model.sess, tf.train.latest_checkpoint(dirname))





##################


from pongjsenv import PongJSEnv
import matplotlib as mpl
import time
# mpl.use("MacOSX")

import matplotlib.pyplot as plt

game = PongJSEnv()
terminated = False
ns = game.reset()
animation = True

x = []
y = []

if animation:
    plt.ion()
    plt.figure()
    plt.show()
    plt.pause(0.5)
step = 0

while not terminated:
    step += 1
    #ns, r, terminated, _ = game.step(0)

    action = model.common_policy.compute_actions(ns[np.newaxis, :])[0][0]
    #probability = model.sess.run(model.action_probability, {self.input_observation: observation[np.newaxis, :]})[0,:]
    #action = np.random.choice(n_actions, p = probability)

    ns, r, terminated, _ = game.step(action)

    ###### CHEAT #######
    #game.left_pad.set_position(game.left_pad.x, ns[1])
    ####################

    ns = ns * 500
    if animation:
        x.append(ns[2])
        y.append(ns[3])
        print(ns[0], ns[1])

        plt.plot([game.right_pad.x, game.left_pad.x],
                [game.right_pad.y, game.left_pad.y], 'o')
        if step % 5 == 0:
            for line in plt.axes().lines:
                line.remove()
            plt.plot(x, y, c='black')
            plt.draw()
            plt.pause(0.1)

print("XXX", step)
