
import paho.mqtt.client as mqtt
import time
import grpc
import wave3 as wv

# The permission set for smart home permissions
# a permission set is a random indentifier, there is nothing special about this
smarthome_pset = bytes("GyAa3XjbDc-S_YoGCW-jXvX5qSmi_BexVDiFE0AdnpbkmA==", "utf8")

class HomeServer:
    def __init__ (self, nickname):
        self.nickname = nickname
        channel = grpc.insecure_channel("localhost:410")
        self.agent = wv.WAVEStub(channel)
        self.ent = self.agent.CreateEntity(wv.CreateEntityParams())
        if self.ent.error.code != 0:
            raise Exception(repr(self.ent.error))
        self.entityPublicDER = self.ent.PublicDER
        self.entitySecretDER = self.ent.SecretDER
        self.perspective =  wv.Perspective(
            entitySecret=wv.EntitySecret(DER=self.ent.SecretDER))
        self.agent.PublishEntity(
            wv.PublishEntityParams(DER=self.ent.PublicDER))

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set("risecamp2018", "risecamp2018")
        self.client.connect("broker.cal-sdb.org", 1883, 60)
        self.client.loop_start()

    def grant_permissions_to(self, enthash):
        # grant the ability to decrypt data that the thermostat publishes
        self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                visibilityURI=[bytes("smarthome","utf8"),bytes("thermostat","utf8")],
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/thermostat",
                )]
            ))
        ))
        # grant the ability to decrypt data that the motion sensor publishes
        self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                visibilityURI=[bytes("smarthome","utf8"),bytes("motion","utf8")],
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/motion",
                )]
            ))
        ))
        # grant the ability to actuate the thermostat and the notifications
        self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                statements=[wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["actuate"],
                    resource="smarthome/thermostat",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["actuate"],
                    resource="smarthome/light",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["actuate"],
                    resource="smarthome/notify",
                )]
            ))
        ))
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.nickname+"/#")

    def namespace(self):
        return self.ent.hash

    def on_message(self, client, userdata, msg):
        proof, payload = unpack_payload(msg.payload)
        if msg.topic == self.nickname+"/smarthome/light":
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["actuate"],
                        resource="smarthome/light",
                    )]
                )
            ))
            if resp.error.code != 0:
                raise Exception(resp.error)
            # TODO integrate with gabe's widget here
            if payload == "on":
                self.light = True
            if payload == "off":
                self.light = False
        elif msg.topic == self.nickname+"/smarthome/thermostat":
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["actuate"],
                        resource="smarthome/thermostat",
                    )]
                )
            ))
            if resp.error.code != 0:
                raise Exception(resp.error)
            # TODO integrate with gabe's widget here
            if payload == "on":
                self.thermostat = True
            if payload == "off":
                self.thermostat = False
        elif msg.topic == self.nickname+"/smarthome/notify":
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["actuate"],
                        resource="smarthome/thermostat",
                    )]
                )
            ))
            if resp.error.code != 0:
                raise Exception(resp.error)
            # TODO integrate with gabe's widget here
            print ("got notification: %s" % payload)


def unpack_payload(payload):
    proof_len=int(payload[:8])
    proof = payload[8:proof_len+8]
    real_payload = payload[proof_len+8:]
    return proof, real_payload

def pack_payload(proof, payload):
    return ("%08d" % (len(proof))) + proof + payload


# Create the home server
hs = HomeServer("michael")

agent = wv.WAVEStub(grpc.insecure_channel("localhost:410"))
entity = agent.CreateEntity(wv.CreateEntityParams())
if entity.error.code != 0:
    raise Exception(entity.error)
agent.PublishEntity(wv.PublishEntityParams(DER=entity.PublicDER))
perspective=wv.Perspective(
    entitySecret=wv.EntitySecret(DER=entity.SecretDER)
)
proof = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
    perspective=perspective,
    namespace=hs.namespace(),
    resyncFirst=True,
    statements=[
        wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["actuate"],
            resource="smarthome/light",
        )
    ]
))
print ("proof resp:",proof)
hs.grant_permissions_to(entity.hash)
proof2 = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
    perspective=perspective,
    namespace=hs.namespace(),
    resyncFirst=True,
    statements=[
        wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["actuate"],
            resource="smarthome/light",
        )
    ]
))
print ("proof resp:",proof2)

time.sleep(30)
