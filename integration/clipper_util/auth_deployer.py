import os
import wave3 as wv
import grpc
import cloudpickle
from clipper_admin.deployers import python as py_deployer
from .clipper_rllib_deployer import deploy_rllib_model
from ray.rllib.agents import ppo
import tarfile
import io
import shutil

def auth_deploy_rllib_model(
    clipper_conn,
    model_name,
    func,
    wave_obj,
    recipient_entity,
    ciphertext,
    checkpoint_file,
    version=1,
    input_type="doubles",
    klass=ppo.PPOAgent,
    ppo_env="pong_env"
):
    '''Deploy a Python function with a RLlib model.

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
    wave_obj: wave object
    recipient_entity: parameter for wave decrypt call
    ciphertext: text to be decoded
    '''
    decrypt_response = wave_obj.DecryptMessage(wv.DecryptMessageParams(
        perspective=wv.Perspective(
            entitySecret=wv.EntitySecret(DER=recipient_entity.SecretDER)),
        ciphertext=ciphertext,
        resyncFirst= True))
    if decrypt_response.error.code != 0:
        raise Exception("Incorrect authentication")

    decrypt_path = "/tmp/model_dir/"
    decryptedmodel = io.BytesIO(decrypt_response.content)

    with tarfile.open(fileobj=decryptedmodel, mode="r:gz") as tar:
        tar.extractall(path=decrypt_path)
        decrypt_path += tar.getnames()[0]

    deploy_rllib_model(
        clipper_conn,
        name=model_name,
        version=version,
        input_type=input_type,
        func=func,
        model_dir=decrypt_path,
        checkpoint_file=checkpoint_file
    )

    shutil.rmtree(decrypt_path)

def auth_deploy_python_model(
    clipper_conn,
    model_name,
    wave_obj,
    recipient_entity,
    ciphertext,
    version=1,
    input_type="doubles"
):
    '''Deploy a Python function with a python model.

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
    wave_obj: wave object
    recipient_entity: parameter for wave decrypt call
    ciphertext: text to be decoded
    '''
    decrypt_response = wave_obj.DecryptMessage(wv.DecryptMessageParams(
        perspective=wv.Perspective(
            entitySecret=wv.EntitySecret(DER=recipient_entity.SecretDER)),
        ciphertext=ciphertext,
        resyncFirst= True))
    if decrypt_response.error.code != 0:
        raise Exception("Incorrect authentication")

    model = cloudpickle.loads(decrypt_response.content)

    # temporarily put the predict method here...
    def predict(inputs):
        # model.predict returns a list of predictions
        preds = model.predict(inputs)
        return [str(p) for p in preds]

    py_deployer.deploy_python_closure(clipper_conn,
                                 name=model_name,
                                 version=version,
                                 input_type=input_type,
                                 func=predict,
                                 pkgs_to_install=["numpy","scipy", "pandas", "sklearn"])

