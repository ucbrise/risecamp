import os
import wave3 as wv
import grpc
# from clipper_admin.deployers import rllib as rllib_deployer
from clipper_rllib_deployer import deploy_rllib_model

def auth_deploy_rllib_model(
    clipper_conn,
    model_name,
    version=1,
    input_type="doubles",
    func,
    trainer,
    wave_obj,
    recipient_entity,
    ciphertext
):
    '''Deploy a Python function with a PyTorch model.

    Parameters
    ----------
    clipper_conn : :py:meth:`clipper_admin.ClipperConnection`
        A ``ClipperConnection`` object connected to a running Clipper cluster.
    name : str
        The name to be assigned to both the registered application and deployed model.
    version : str
        The version to assign this model. Versions must be unique on a per-model
        basis, but may be re-used across different models.
    input_type : str
        The input_type to be associated with the registered app and deployed model.
        One of "integers", "floats", "doubles", "bytes", or "strings".
    func : function
        The prediction function. Any state associated with the function will be
        captured via closure capture and pickled with Cloudpickle.
    trainer : RLlib PPO Agent
    wave_obj: wave object
    recipient_entity: parameter for wave decrypt call
    ciphertext: text to be decoded
    '''
    decrypt_response = wave_obj.DecryptMessage(wv.DecryptMessageParams(
        perspective=wv.Perspective(
            entitySecret=wv.EntitySecret(DER=recipientEntity.SecretDER)),
        ciphertext=ciphertext,
        resyncFirst= True))
    if decrypt_response.error.code != 0:
        raise Exception("Incorrect authentication")
    
    rllib_deployer.deploy_rllib_model(
        clipper_conn,
        name=model_name,
        version=1,
        input_type="doubles",
        func=predict_doubles,
        trainer=trainer
    )