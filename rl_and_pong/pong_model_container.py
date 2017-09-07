from __future__ import print_function
import numpy as np
import os
import sys
import pong_py
import ray
import json
from datetime import datetime
from ray.rllib.ppo import PPOAgent, DEFAULT_CONFIG
import rpc


class PongPolicyContainer(rpc.ModelContainerBase):
    def __init__(self, path):
        ray.init(num_workers=0)

        @ray.remote
        def f():
            pong_py

        config = DEFAULT_CONFIG.copy()
        config['num_workers'] = 3
        config['num_sgd_iter'] = 20
        config['sgd_batchsize'] = 8196
        config['model']['fcnet_hiddens'] = [32, 32]
        config['gamma'] = 0.99
        config['sgd_stepsize'] = 5e-3
        config['kl_coeff'] = 0.1
        self.agent = PPOAgent('PongJS-v0', config)
        self.agent.restore(path)
        # Run test prediction to load the model
        print("Predicted {} in constructor".format(
            self.agent.compute_action(np.random.random(8))))

    def predict_doubles(self, states):
        start = datetime.now()
        actions = [str(self.agent.compute_action(s)) for s in states]
        end = datetime.now()
        print("Computed action in {} ms".format((end-start).total_seconds() * 1000.0))
        return actions


if __name__ == "__main__":
    print("Starting Pong policy container")
    try:
        model_name = os.environ["CLIPPER_MODEL_NAME"]
    except KeyError:
        print(
            "ERROR: CLIPPER_MODEL_NAME environment variable must be set",
            file=sys.stdout)
        sys.exit(1)
    try:
        model_version = os.environ["CLIPPER_MODEL_VERSION"]
    except KeyError:
        print(
            "ERROR: CLIPPER_MODEL_VERSION environment variable must be set",
            file=sys.stdout)
        sys.exit(1)

    ip = "127.0.0.1"
    if "CLIPPER_IP" in os.environ:
        ip = os.environ["CLIPPER_IP"]
    else:
        print("Connecting to Clipper on localhost")

    port = 7000
    if "CLIPPER_PORT" in os.environ:
        port = int(os.environ["CLIPPER_PORT"])
    else:
        print("Connecting to Clipper with default port: 7000")

    input_type = "doubles"
    model_dir_path = "/model"
    with open(os.path.join(model_dir_path, "metadata.json"), "r") as f:
        checkpoint_file = json.load(f)["checkpoint"]
    model = PongPolicyContainer(os.path.join(model_dir_path, checkpoint_file))
    rpc_service = rpc.RPCService()
    rpc_service.start(model, ip, port, model_name, model_version, input_type)
