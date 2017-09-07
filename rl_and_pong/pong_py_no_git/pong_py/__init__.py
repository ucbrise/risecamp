from pong_py.pongjsenv import PongJSEnv

from gym.envs.registration import register

register(id='PongJS-v0', entry_point='pong_py:PongJSEnv', kwargs={}, nondeterministic=False)
