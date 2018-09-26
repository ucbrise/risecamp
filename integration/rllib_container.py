from __future__ import print_function
import rpc
import os
import sys
import json

import numpy as np
import cloudpickle
import importlib
import ray
import json
from datetime import datetime
from ray.rllib.agents import ppo
from ray.tune.registry import register_env
import pong_py


IMPORT_ERROR_RETURN_CODE = 3


def load_predict_func(file_path):
    if sys.version_info < (3, 0):
        with open(file_path, 'r') as serialized_func_file:
            return cloudpickle.load(serialized_func_file)
    else:
        with open(file_path, 'rb') as serialized_func_file:
            return cloudpickle.load(serialized_func_file)


class RLlibContainer(rpc.ModelContainerBase):
    def __init__(self, path, input_type):
        ray.init()

        # @ray.remote
        # def f():
        #     pong_py

        # config = ppo.DEFAULT_CONFIG.copy()
        # config['num_workers'] = 3
        # config['num_sgd_iter'] = 20
        # config['sgd_batchsize'] = 8196
        # config['model']['fcnet_hiddens'] = [32, 32]
        # config['gamma'] = 0.99
        # config['sgd_stepsize'] = 5e-3
        # config['kl_coeff'] = 0.1
        # self.agent = ppo.PPOAgent('PongJS-v0', config)

        def env_creator(env_config):
            return pong_py.PongJSEnv()

        register_env("my_env", env_creator)
        # ray.init()
        trainer = ppo.PPOAgent(env="my_env", config={
            "env_config": {},  # config to pass to env creator
        })
        self.agent = trainer

        ckpt_dir = os.path.join(path, 'checkpoint')
        meta_data = json.load(open(os.path.join(ckpt_dir, 'metadata.json')))['checkpoint']
        self.agent.restore(os.path.join(ckpt_dir, meta_data))

        self.input_type = rpc.string_to_input_type(input_type)
        modules_folder_path = "{dir}/modules/".format(dir=path)
        sys.path.append(os.path.abspath(modules_folder_path))
        predict_fname = "func.pkl"
        predict_path = "{dir}/{predict_fname}".format(
            dir=path, predict_fname=predict_fname)
        self.predict_func = load_predict_func(predict_path)
        # Run test prediction to load the model
#         print("Predicted {} in constructor".format(
#             self.agent.compute_action(np.random.random(7))))

    def predict_ints(self, inputs):
        preds = self.predict_func(self.agent, inputs)
        return [str(p) for p in preds]

    def predict_floats(self, inputs):
        preds = self.predict_func(self.agent, inputs)
        return [str(p) for p in preds]

    def predict_doubles(self, inputs):
        preds = self.predict_func(self.agent, inputs)
        return [str(p) for p in preds]

    def predict_bytes(self, inputs):
        preds = self.predict_func(self.agent, inputs)
        return [str(p) for p in preds]

    def predict_strings(self, inputs):
        preds = self.predict_func(self.agent, inputs)
        return [str(p) for p in preds]


if __name__ == "__main__":
    print("Starting RLlib container")
    rpc_service = rpc.RPCService()
    try:
        model = RLlibContainer(rpc_service.get_model_path(),
                               rpc_service.get_input_type())
        sys.stdout.flush()
        sys.stderr.flush()
    except ImportError:
        sys.exit(IMPORT_ERROR_RETURN_CODE)
    rpc_service.start(model)
