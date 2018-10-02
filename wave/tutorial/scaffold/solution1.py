# SOLUTION:
def thermostat_cb(msg):
    # first decrypt the message
    resp = wave.DecryptMessage(wv.DecryptMessageParams(
        perspective= perspective,
        ciphertext= msg.payload,
        resyncFirst= True))
    if resp.error.code != 0:
        print ("dropping thermostat message:", resp.error.message)
        return
    # then break it up into proof + body
    proof, body = decomposeMessage(resp.content)
    
    # now validate the proof
    resp = wave.VerifyProof(wv.VerifyProofParams(
        proofDER=proof,
        requiredRTreePolicy=wv.RTreePolicy(
            namespace=homeserver.namespace(),
            statements=[wv.RTreePolicyStatement(
                permissionSet=smarthome_pset,
                permissions=["write"],
                resource="smarthome/thermostat/report",
            )]
        )
    ))
    if resp.error.code != 0:
        print ("dropping message: ", resp.error.message)
        return
        
    # the proof is valid!
    house_occupied = body["occupied"] # True or False
    
    # SOLUTION:
    mqtt.publish(my_unique_nickname+"/smarthome/light/control",
        composeMessage(lightproof, {"state":"on" if house_occupied else "off"}))
    
    
mqtt.subscribe(my_unique_nickname+"/smarthome/thermostat/report", thermostat_cb)