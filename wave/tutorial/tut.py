
import paho.mqtt.client as mqtt
import time
import grpc
import json
import base64
import wave3 as wv
import widgets
from IPython.display import display

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

        # instantiate and display widgets
        self.light_widget = widgets.Light('light-1')
        self.switch_widget = widgets.Switch('light-1')
        self.thermostat_widget = widgets.Thermostat()
        display(self.light_widget)
        display(self.switch_widget)
        display(self.thermostat_widget)

        # TODO: have read/write topic?
        self.tstat_entity, self.tstat_encrypt_proof, self.tstat_msg_proof = self._make_device_entity('thermostat')
        self.light_entity, self.light_encrypt_proof, self.light_msg_proof = self._make_device_entity('light')
        self.light_widget.observe(self._publish_light_state, 'state')
        self.thermostat_widget.observe(self._publish_tstat_state)
        # hook up triggers to report?

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set("risecamp2018", "risecamp2018")
        self.client.connect("broker.cal-sdb.org", 1883, 60)
        self.client.loop_start()

    def _make_device_entity(self, device):
        """
        - makes entity
        - publishes entity
        - namespace grant to device entity read on <hash>/<device>/control
        - namespace grant to device entity write on <hash>/<device>/report
        """
        device_entity = self.agent.CreateEntity(wv.CreateEntityParams())
        if device_entity.error.code != 0:
            raise Exception(device_entity.error)
        self.agent.PublishEntity(wv.PublishEntityParams(DER=device_entity.PublicDER))
        device_perspective=wv.Perspective(
            entitySecret=wv.EntitySecret(DER=device_entity.SecretDER)
        )

        # grant permission to encrypt on device URIs, read/write on report/control respectively

        encrypt_policy = wv.Policy(rTreePolicy=wv.RTreePolicy(
            namespace=self.ent.hash,
            indirections=5,
            # TODO: need this?
            # visibilityURI=[bytes("smarthome","utf8"),bytes(device,"utf8")],
            statements=[
                wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/{0}/+".format(device),
                )
            ]
        ))

        msg_policy = wv.Policy(rTreePolicy=wv.RTreePolicy(
            namespace=self.ent.hash,
            indirections=5,
            statements=[
                  wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["read"],
                    resource="smarthome/{0}/control".format(device),
                ),
                wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["write"],
                    resource="smarthome/{0}/report".format(device),
                )
            ]
        ))

        r = self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=device_entity.hash,
            publish=True,
            policy=msg_policy
        ))
        #print(r)
        #print('msg policy attested')

        r = self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=device_entity.hash,
            publish=True,
            policy=encrypt_policy,
        ))
        #print(r)
        #print('encrypt policy attested')
        #print(encrypt_policy)

        encrypt_proof = self.agent.BuildRTreeProof(wv.BuildRTreeProofParams(
            perspective=device_perspective,
            namespace=encrypt_policy.rTreePolicy.namespace,
            resyncFirst=True,
            statements=encrypt_policy.rTreePolicy.statements,
        ))
        if encrypt_proof.error.code != 0:
            raise Exception(encrypt_proof.error)

        msg_proof = self.agent.BuildRTreeProof(wv.BuildRTreeProofParams(
            perspective=device_perspective,
            namespace=msg_policy.rTreePolicy.namespace,
            resyncFirst=True,
            statements=msg_policy.rTreePolicy.statements,
        ))
        if msg_proof.error.code != 0:
            raise Exception(msg_proof.error)
        return device_entity, encrypt_proof, msg_proof



    def _publish_light_state(self, change):
        packed = pack_payload(self.light_msg_proof.proofDER, json.dumps({'state': 'on' if change.new else 'off'}))
        self.client.publish("{0}/smarthome/light/report".format(self.nickname), packed)

    def _publish_tstat_state(self, change):
        state = {'state': self.thermostat_widget.state,
                 'hsp': self.thermostat_widget.hsp,
                 'csp': self.thermostat_widget.csp,
                 'temperature': self.thermostat.temp}
        packed = pack_payload(self.tstat_msg_proof.proofDER, json.dumps(state))
        self.client.publish('{0}/smarthome/thermostat/report'.format(self.nickname), packed)

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
                    resource="smarthome/thermostat/+",
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
                    resource="smarthome/motion/+",
                )]
            ))
        ))

        # grant the ability to decrypt data that the light publishes
        self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                visibilityURI=[bytes("smarthome","utf8"),bytes("light","utf8")],
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/light/+",
                )]
            ))
        ))

        # grant the ability to actuate the thermostat and the light and the notifications, and read the thermostat and light
        self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                statements=[wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["write"],
                    resource="smarthome/thermostat/control",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["write"],
                    resource="smarthome/light/control",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["write"],
                    resource="smarthome/notify",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["read"],
                    resource="smarthome/thermostat/report",
                ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["read"],
                    resource="smarthome/light/report",
                ),
                ]
            ))
        ))
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.nickname+"/#")

    def namespace(self):
        return self.ent.hash

    def on_message(self, client, userdata, msg):
        proof, payload = unpack_payload(msg.payload)
        if len(proof) == 0:
            return
        print (msg.topic)

        if msg.topic == self.nickname+"/smarthome/light/control":
            print ("got light command\n")
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["write"],
                        resource="smarthome/light/control",
                    )]
                )
            ))
            if resp.error.code != 0:
                raise Exception(resp.error)
            # actuate light state when the light receives a direct message
            self.light_widget.state = json.loads(payload).get('state') == 'on'

        elif msg.topic == self.nickname+"/smarthome/thermostat/control":
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["write"],
                        resource="smarthome/thermostat/control",
                    )]
                )
            ))
            if resp.error.code != 0:
                raise Exception(resp.error)

            # TODO integrate with gabe's widget here
            tstat_fields = json.loads(payload)
            print('thermostat command', tstat_fields)
            if tstat_fields.get('hsp'):
                self.thermostat_widget.hsp = tstat_fields.get('hsp')
            if tstat_fields.get('csp'):
                self.thermostat_widget.csp = tstat_fields.get('csp')
            if tstat_fields.get('temperature'):
                self.thermostat_widget.temp = tstat_fields.get('temp')

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
        else:
            print("topic", msg.topic, "payload", payload)


def unpack_payload(payload):
    if len(payload) < 100:
        return b"", ""
    proof_len=int(payload[:8])
    proof = payload[8:proof_len+8]
    bproof = base64.b64decode(proof)
    real_payload = payload[proof_len+8:]
    return bproof, str(real_payload,"utf8")

def pack_payload(proof, payload):
    b64 = str(base64.b64encode(proof),"utf8")
    rv = ("%08d" % (len(b64))) + b64 + payload
    return rv

check_error(pb.Error)

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
            resource="smarthome/light/control",
        )
    ]
))
# should have no permissions
print ("first attempt without permissions:")
print (proof.error)

hs.grant_permissions_to(entity.hash)
proof2 = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
    perspective=perspective,
    namespace=hs.namespace(),
    resyncFirst=True,
    statements=[
        wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["write"],
            resource="smarthome/light/control",
        ),
      wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["read"],
            resource="smarthome/light/report",
        )
    ]
))
if proof2.error.code != 0:
    raise Exception(proof2.error)

# actuate the light directly with proof3

proof3 = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
    perspective=perspective,
    namespace=hs.namespace(),
    resyncFirst=True,
    statements=[
        wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["write"],
            resource="smarthome/thermostat/control",
        ),
        wv.RTreePolicyStatement(
            permissionSet=smarthome_pset,
            permissions=["read"],
            resource="smarthome/thermostat/report",
        )
    ]
))
if proof3.error.code != 0:
    raise Exception(proof3.error)

client = mqtt.Client()
client.username_pw_set("risecamp2018", "risecamp2018")
client.connect("broker.cal-sdb.org", 1883, 60)
client.loop_start()

time.sleep(3)
packed = pack_payload(proof2.proofDER, json.dumps({'state': 'on'}))
client.publish("michael/smarthome/light/control", packed)

packed = pack_payload(proof3.proofDER,json.dumps({'hsp': 70, 'csp': 78}))
client.publish("michael/smarthome/thermostat/control", packed)


#subscribe to utility, decryption fails, apply for permissions, decryption succeeeds

# create entity convenience
# check error function
# utility functions for publish
# utility function unpack (decrypt)

#time.sleep(30)
