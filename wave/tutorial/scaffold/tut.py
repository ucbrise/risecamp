
import paho.mqtt.client as mqtt
import time
import grpc
import json
import base64
import wave3 as wv
import scaffold.widgets as widgets
import pickle
import threading
import traceback
import base64
from IPython.display import display

# The permission set for smart home permissions
# a permission set is a random indentifier, there is nothing special about this
smarthome_pset = bytes("GyAa3XjbDc-S_YoGCW-jXvX5qSmi_BexVDiFE0AdnpbkmA==", "utf8")

def check_I_pasted_correctly():
    global partner_nickname
    global partner_entity_hash
    global partner_home_namespace
    global homeserver
    global entity
    if partner_nickname == "paste the nickname here":
        raise Exception("You forgot to paste your partner's nickname")
    if partner_nickname == my_unique_nickname:
        raise Exception("You pasted your own nickname, not your partner's")
    if partner_entity_hash == entity.hash:
        raise Exception("You pasted your own entity hash, not your partner's")
    if partner_home_namespace == homeserver.namespace:
        raise Exception("You pasted your own namespace, not your partner's")

# some utility functions
def hashToBase64(hash):
    return str(base64.b64encode(hash), "utf8")
def hashFromBase64(b64):
    if b64 == "paste the entity hash here":
        raise Exception("You forgot to paste the entity hash")
    if b64 == "paste the namespace here":
        raise Exception("You forgot to paste the namespace hash")
    return base64.b64decode(b64)

# TODO add proper expiries to all the attestations. Default might be unsuitable
class MQTTWrapper:
    def __init__ (self):
        mqttclient = mqtt.Client()
        mqttclient.username_pw_set("risecamp2018", "risecamp2018")
        mqttclient.connect("broker.cal-sdb.org", 1883, 60)
        mqttclient.loop_start()
        self.client = mqttclient
        self.client.on_message = self.on_message
        self.callbacks = {}
        self.mu = threading.Lock()

    def on_message(self, client, userdata, msg):
        try:
            self.mu.acquire()
            for k in self.callbacks:
                if mqtt.topic_matches_sub(k, msg.topic):
                    self.callbacks[k](msg)
        except:
            traceback.print_exc()
        finally:
            self.mu.release()
            
    def subscribe(self, topic, callback):
        self.mu.acquire()
        self.callbacks[topic] = callback
        self.mu.release()
        self.client.subscribe(topic)

    def publish(self, topic, msg):
        self.client.publish(topic, msg)


class HomeServer:
    def __init__ (self, nickname):
        self.nickname = nickname
        channel = grpc.insecure_channel("localhost:410")
        self.agent = wv.WAVEStub(channel)

        self.ent, newlycreated = createOrLoadEntity(self.agent, "homeserver")
        self.entityPublicDER = self.ent.PublicDER
        self.entitySecretDER = self.ent.SecretDER
        self.perspective =  wv.Perspective(
            entitySecret=wv.EntitySecret(DER=self.ent.SecretDER))
        if newlycreated:
            self.agent.PublishEntity(
                wv.PublishEntityParams(DER=self.ent.PublicDER))

        # instantiate and display widgets
        self.light_widget = widgets.Light('light-1')
        self.switch_widget = widgets.Switch('light-1')
        self.thermostat_widget = widgets.Thermostat()
        self.motion_sensor_widget = widgets.MotionSensor()
        self.notificationbox = widgets.Notification()
        self.lightbox = widgets.ipw.VBox([self.light_widget, self.switch_widget], layout=widgets.ipw.Layout(align_items='center', border='solid 2px'))
        self.mybox = widgets.ipw.VBox([
            widgets.ipw.HBox([self.lightbox, self.motion_sensor_widget, self.thermostat_widget], layout=widgets.ipw.Layout(width='100%')),
            self.notificationbox,
        ])
        display(self.mybox)


        # TODO: have read/write topic?
        self.tstat_entity, self.tstat_encrypt_proof, self.tstat_msg_proof = self._make_device_entity('thermostat')
        self.light_entity, self.light_encrypt_proof, self.light_msg_proof = self._make_device_entity('light')
        self.motion_entity, self.motion_encrypt_proof, self.motion_msg_proof = self._make_device_entity('motion')
        self.light_widget.observe(self._publish_light_state, 'state')
        self.thermostat_widget.observe(self._publish_tstat_state)
        self.motion_sensor_widget.observe(self._publish_motion_sensor_state)
        # hook up triggers to report?

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set("risecamp2018", "risecamp2018")
        self.client.connect("broker.cal-sdb.org", 1883, 60)
        self.client.loop_start()

    def notify(self, msg):
        """
        Displays message (adds timestamp) in notification box
        """
        self.notificationbox.addmsg(msg)

    def render(self):
        """
        displays the widgets; shared state with all other renders
        """
        display(self.mybox)


    def _make_device_entity(self, device):
        """
        - makes entity
        - publishes entity
        - namespace grant to device entity read on <hash>/<device>/control
        - namespace grant to device entity write on <hash>/<device>/report
        """
        device_entity, newlyCreated = createOrLoadEntity(self.agent, device)
        if newlyCreated:
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

        if newlyCreated:
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
        encrypted = self.agent.EncryptMessage(
            wv.EncryptMessageParams(
                namespace=self.namespace(),
                resource="smarthome/light/report",
                content=bytes(packed,"utf8")))
        if encrypted.error.code != 0:
            raise Exception(encrypted.error.message)
        self.client.publish("{0}/smarthome/light/report".format(self.nickname), encrypted.ciphertext)
        #self.notify("Light changed (local) to {0}".format('on' if change.new else 'off'))


    def _publish_tstat_state(self, change):
        state = {'state': self.thermostat_widget.state,
                 'hsp': self.thermostat_widget.hsp,
                 'csp': self.thermostat_widget.csp,
                 'temperature': self.thermostat_widget.temp,
                 'occupied': self.thermostat_widget.occupied}
        packed = pack_payload(self.tstat_msg_proof.proofDER, json.dumps(state))
        encrypted = self.agent.EncryptMessage(
            wv.EncryptMessageParams(
                namespace=self.namespace(),
                resource="smarthome/thermostat/report",
                content=bytes(packed,"utf8")))
        if encrypted.error.code != 0:
            raise Exception(encrypted.error.message)
        self.client.publish('{0}/smarthome/thermostat/report'.format(self.nickname), encrypted.ciphertext)

    def _publish_motion_sensor_state(self, change):
        if not change['new']: return
        state = 'triggered'
        packed = pack_payload(self.motion_msg_proof.proofDER, json.dumps(state))
        encrypted = self.agent.EncryptMessage(
            wv.EncryptMessageParams(
                namespace=self.namespace(),
                resource="smarthome/motion/report",
                content=bytes(packed,"utf8")))
        if encrypted.error.code != 0:
            raise Exception(encrypted.error.message)
        self.client.publish('{0}/smarthome/motion/report'.format(self.nickname), encrypted.ciphertext)
        self.notify("Motion sensor triggered!")


    def grant_permissions_to(self, enthash):
        # grant the ability to decrypt data that the thermostat publishes
        resp = self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/thermostat/+",
                )]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)
        # grant the ability to decrypt data that the motion sensor publishes
        resp = self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/motion/+",
                )]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)
        # grant the ability to decrypt data that the light publishes
        resp = self.agent.CreateAttestation(wv.CreateAttestationParams(
            perspective=self.perspective,
            subjectHash=enthash,
            publish=True,
            policy=wv.Policy(rTreePolicy=wv.RTreePolicy(
                namespace=self.ent.hash,
                indirections=5,
                statements=[wv.RTreePolicyStatement(
                    permissionSet=wv.WaveBuiltinPSET,
                    permissions=[wv.WaveBuiltinE2EE],
                    resource="smarthome/light/+",
                )]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)

        # grant the ability to actuate the thermostat and the light and the notifications, and read the thermostat and light
        resp = self.agent.CreateAttestation(wv.CreateAttestationParams(
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
               ),wv.RTreePolicyStatement(
                    permissionSet=smarthome_pset,
                    permissions=["read"],
                    resource="smarthome/motion/report",
                )]
            ))
        ))
        if resp.error.code != 0:
            raise Exception(resp.error.message)
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.nickname+"/#")

    def namespace(self):
        return self.ent.hash

    def on_message(self, client, userdata, msg):
        proof, payload = unpack_payload(msg.payload)
        if len(proof) == 0:
            return

        if msg.topic == self.nickname+"/smarthome/light/control":
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
                print("home server received light control with invalid proof: ",resp.error.message)
                return
            # actuate light state when the light receives a direct message
            ls = json.loads(payload).get('state')
            self.light_widget.state = (ls == 'on' or ls == True)
            #self.notify("Light changed (remote) to {0}".format('on' if self.light_widget.state else 'off'))

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
                print("home server received thermostat control with invalid proof: ",resp.error.message)
                return

            # TODO integrate with gabe's widget here
            tstat_fields = json.loads(payload)
            #print('thermostat command', tstat_fields)
            if tstat_fields.get('hsp'):
                self.thermostat_widget.hsp = tstat_fields.get('hsp')
                self.notify("Thermostat heating setpoint changed to {0}".format(self.thermostat_widget.hsp))
            if tstat_fields.get('csp'):
                self.thermostat_widget.csp = tstat_fields.get('csp')
                self.notify("Thermostat cooling setpoint changed to {0}".format(self.thermostat_widget.csp))
            if tstat_fields.get('temperature'):
                self.thermostat_widget.temp = tstat_fields.get('temp')

        elif msg.topic == self.nickname+"/smarthome/notify":
            resp = self.agent.VerifyProof(wv.VerifyProofParams(
                proofDER=proof,
                requiredRTreePolicy=wv.RTreePolicy(
                    namespace=self.ent.hash,
                    statements=[wv.RTreePolicyStatement(
                        permissionSet=smarthome_pset,
                        permissions=["write"],
                        resource="smarthome/notify",
                    )]
                )
            ))
            if resp.error.code != 0:
                print("home server received notify with invalid proof: ",resp.error.message)
                return
            self.notify(json.loads(payload))
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

def composeMessage(proof, data):
    return pack_payload(proof.proofDER, json.dumps(data))

def decomposeMessage(data):
    proof, payload = unpack_payload(data)
    return proof, json.loads(payload)

def publishMessage(topic, proof, data):
    packed = pack_payload(proof.proofDER, json.dumps(data))
    mqttclient.publish(topic, packed)

def checkError(pbobj):
    if pbobj.error.code != 0:
        print("Error: ", pbobj.error.message)
        return True
    return False

# def encryptMessage(namespace, uri, msg):
#     """
#     Encrypt a message under a specific URI
#     """
#     resp = agent.EncryptMessage(wv.EncryptMessageParams(namespace=namespace, resource=uri))
#     if resp.error.code != 0:
#         raise Exception(resp.error.message)
#     return resp.ciphertext

# def decryptMessage(perspective, msg):
#     """
#     Try decrypt a message. Returns None if the decryption fails
#     """
#     resp = agent.DecryptMessage(
#         wv.DecryptMessageParams(perspective=perspective, content=msg, resyncFirst=True))
#     if checkError(resp):
#         return None
#     return resp.content

def Initialize(nickname):
    """
    Set up the home server with the user's nickname,
    and open a WAVE and MQTT client
    """
    if nickname == "john-smith":
        raise Exception("you must change your nickname to something unique")
    global t_homeserver
    t_homeserver = HomeServer(nickname)
    global t_wave
    t_wave = wv.WAVEStub(grpc.insecure_channel("localhost:410"))
    mqttclient = MQTTWrapper()
    return t_wave, t_homeserver, mqttclient

def createOrLoadEntity(agent, name):
    """
    Check if we have already created an entity (maybe we reset the notebook kernel)
    and load it. Otherwise create a new entity and persist it to disk
    """
    try:
        f = open("/tmp/entity-"+name, "rb")
        entf = pickle.load(f)
        f.close()
        ent = wv.CreateEntityResponse(PublicDER=entf["pub"], SecretDER=entf["sec"], hash=entf["hash"])
        return ent, False
    except IOError:
        ent = agent.CreateEntity(wv.CreateEntityParams())
        if ent.error.code != 0:
            raise Exception(repr(ent.error))
        entf = {"pub":ent.PublicDER, "sec":ent.SecretDER, "hash":ent.hash}
        f = open("/tmp/entity-"+name, "wb")
        pickle.dump(entf, f)
        f.close()
        resp = agent.PublishEntity(wv.PublishEntityParams(DER=ent.PublicDER))
        if resp.error.code != 0:
            raise Exception(resp.error.message)
        return ent, True

# Create the home server

# entity = agent.CreateEntity(wv.CreateEntityParams())
# if entity.error.code != 0:
#     raise Exception(entity.error)
# agent.PublishEntity(wv.PublishEntityParams(DER=entity.PublicDER))
# perspective=wv.Perspective(
#     entitySecret=wv.EntitySecret(DER=entity.SecretDER)
# )
# proof = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
#     perspective=perspective,
#     namespace=hs.namespace(),
#     resyncFirst=True,
#     statements=[
#         wv.RTreePolicyStatement(
#             permissionSet=smarthome_pset,
#             permissions=["actuate"],
#             resource="smarthome/light/control",
#         )
#     ]
# ))
# # should have no permissions
# print ("first attempt without permissions:")
# print (proof.error)

# hs.grant_permissions_to(entity.hash)
# proof2 = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
#     perspective=perspective,
#     namespace=hs.namespace(),
#     resyncFirst=True,
#     statements=[
#         wv.RTreePolicyStatement(
#             permissionSet=smarthome_pset,
#             permissions=["write"],
#             resource="smarthome/light/control",
#         ),
#       wv.RTreePolicyStatement(
#             permissionSet=smarthome_pset,
#             permissions=["read"],
#             resource="smarthome/light/report",
#         )
#     ]
# ))
# if proof2.error.code != 0:
#     raise Exception(proof2.error)

# actuate the light directly with proof3

# proof3 = agent.BuildRTreeProof(wv.BuildRTreeProofParams(
#     perspective=perspective,
#     namespace=hs.namespace(),
#     resyncFirst=True,
#     statements=[
#         wv.RTreePolicyStatement(
#             permissionSet=smarthome_pset,
#             permissions=["write"],
#             resource="smarthome/thermostat/control",
#         ),
#         wv.RTreePolicyStatement(
#             permissionSet=smarthome_pset,
#             permissions=["read"],
#             resource="smarthome/thermostat/report",
#         )
#     ]
# ))
# if proof3.error.code != 0:
#     raise Exception(proof3.error)



# time.sleep(3)
# packed = pack_payload(proof2.proofDER, json.dumps({'state': 'on'}))
# client.publish("michael/smarthome/light/control", packed)

# packed = pack_payload(proof3.proofDER,json.dumps({'hsp': 70, 'csp': 78}))
# client.publish("michael/smarthome/thermostat/control", packed)


#subscribe to utility, decryption fails, apply for permissions, decryption succeeeds

# create entity convenience
# check error function
# utility functions for publish
# utility function unpack (decrypt)

#time.sleep(30)
