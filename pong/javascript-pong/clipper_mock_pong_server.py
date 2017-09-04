from clipper_admin import ClipperConnection, DockerContainerManager
from clipper_admin.deployers import python as py_deployer
import random

cl = ClipperConnection(DockerContainerManager())
cl.stop_all()
cl.start_clipper()

# cl.register_application(name="pong", input_type="doubles", slo_micros=1000000, default_output="1")


def random_predict(xs):
    action = random.randint(0, 2)
    return [str(action) for _ in xs]


py_deployer.create_endpoint(cl, name="pong", input_type="doubles", func=random_predict,
                            default_output="0", slo_micros=100000)
