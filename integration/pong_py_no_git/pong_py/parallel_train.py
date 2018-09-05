import ray
import numpy as np
import gym
import tensorflow as tf
import tensorflow.contrib.slim as slim
import time
import sys
sys.path.insert(0, "/home/ubuntu/pong_py")
from pongjsenv import PongJSEnv

ray.init(num_workers=0)

n_obs = 8              # dimensionality of observations
n_h = 256              # number of hidden layer neurons
#n_actions = 2          # number of available actions
n_actions = 3          # number of available actions
learning_rate = 5e-4   # how rapidly to update parameters
gamma = .99            # reward discount factor


def make_policy(observation_placeholder):
    hidden = slim.fully_connected(observation_placeholder, n_h)
    log_probability = slim.fully_connected(hidden, n_actions, activation_fn=None, weights_initializer=tf.truncated_normal_initializer(0.001))
    return tf.nn.softmax(log_probability)

def discounted_normalized_rewards(r):
    """Take 1D float array of rewards and compute normalized discounted reward."""
    result = np.zeros_like(r)
    running_sum = 0
    for t in reversed(range(0, r.size)):
        running_sum = running_sum * gamma + r[t]
        result[t] = running_sum
    return (result - np.mean(result)) / np.std(result)


@ray.remote
class Env(object):
    def __init__(self):
        self.env = env = PongJSEnv()

        self.input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])
        input_probability = tf.placeholder(dtype=tf.float32, shape=[None, n_actions])
        input_reward = tf.placeholder(dtype=tf.float32, shape=[None,1])

        # The policy network.
        self.action_probability = make_policy(self.input_observation)

        loss = tf.nn.l2_loss(input_probability - self.action_probability)
        optimizer = tf.train.AdamOptimizer(learning_rate)
        self.train_op = optimizer.minimize(loss, grad_loss=input_reward)

        # Create TensorFlow session and initialize variables.
        self.sess = tf.InteractiveSession()
        tf.global_variables_initializer().run()

        self.variables = ray.experimental.TensorFlowVariables(self.action_probability, self.sess)

    def rollout(self):

        observation = self.env.reset()
        observations, rewards, labels = [], [], []
        reward_sum = 0
        reward_sums = []
        episode_number = 0
        num_timesteps = 0

        done = False

        start_time = time.time()

        # Training loop
        while not done:
            # stochastically sample a policy from the network
            probability = self.sess.run(self.action_probability, {self.input_observation: observation[np.newaxis, :]})[0,:]

            action = np.random.choice(n_actions, p = probability)
            label = np.zeros_like(probability) ; label[action] = 1
            observations.append(observation)
            labels.append(label)

            observation, reward, done, info = self.env.step(action)
            reward_sum += reward

            rewards.append(reward)

        return np.vstack(observations), discounted_normalized_rewards(np.vstack(rewards)), np.vstack(labels)

    def load_weights(self, weights):
        self.variables.set_weights(weights)


agents = [Env.remote() for _ in range(4)]

input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])
input_probability = tf.placeholder(dtype=tf.float32, shape=[None, n_actions])
input_reward = tf.placeholder(dtype=tf.float32, shape=[None, 1])

action_probability = make_policy(input_observation)

loss = tf.nn.l2_loss(input_probability - action_probability)
optimizer = tf.train.AdamOptimizer(learning_rate)
train_op = optimizer.minimize(loss, grad_loss=input_reward)

sess = tf.Session()
tf.global_variables_initializer().run(session=sess)
variables = ray.experimental.TensorFlowVariables(loss, sess)

num_timesteps = 0
reward_sums = []

# Barrier for the timing (TODO(pcm): clean this up)
weights = ray.put(variables.get_weights())
ray.get([agent.load_weights.remote(weights) for agent in agents])

start_time = time.time()

for _ in range(100):
    weights = ray.put(variables.get_weights())

    # EXERCISE: Set weights on the remote agents
    [agent.load_weights.remote(weights) for agent in agents]

    # EXERCISE: Call agent.rollout on all the agents, get results, store them in variable "trajectories"
    trajectories = ray.get([agent.rollout.remote() for agent in agents])

    reward_sums.extend([trajectory[0].shape[0] for trajectory in trajectories])
    timesteps = np.sum([trajectory[0].shape[0] for trajectory in trajectories])
    if (num_timesteps + timesteps) // 5000 > num_timesteps // 5000:
        print('time: {:4.1f}, timesteps: {:7.0f}, reward: {:7.3f}'.format(
            time.time() - start_time, num_timesteps + timesteps, np.mean(reward_sums)))
    num_timesteps += timesteps
    results = [np.concatenate(x) for x in zip(*trajectories)]
    sess.run(train_op, {input_observation: results[0], input_reward: results[1], input_probability: results[2]})
