partner_occupied = False

def partner_motion_cb(msg):
    global partner_occupied
    # we need to first decrypt the message
    resp = wave.DecryptMessage(wv.DecryptMessageParams(
        perspective= perspective,
        ciphertext= msg.payload,
        resyncFirst= True))
    if resp.error.code != 0:
        print ("dropping motion message:", resp.error.message)
        return
    # then break it up into proof + body
    proof, body = decomposeMessage(resp.content)
    
    # now validate the proof
    resp = wave.VerifyProof(wv.VerifyProofParams(
        proofDER=proof,
        requiredRTreePolicy=wv.RTreePolicy(
            # this is from our partner's namespace
            namespace=partner_home_namespace,
            statements=[wv.RTreePolicyStatement(
                permissionSet=smarthome_pset,
                permissions=["write"],
                resource="smarthome/motion/report",
            )]
        )
    ))
    if resp.error.code != 0:
        print ("dropping motion message: ", resp.error.message)
        return
    
    if not partner_occupied:
        mqtt.publish(my_unique_nickname+"/smarthome/notify",
             composeMessage(msgproof, "a package was delivered to your partner!"))
        
# This one is done for you
def partner_occupancy_cb(msg):
    global partner_occupied
    # the message we are getting here is our OWN light state
    # we need to first decrypt the message
    resp = wave.DecryptMessage(wv.DecryptMessageParams(
        perspective= perspective,
        ciphertext= msg.payload,
        resyncFirst= True))
    if resp.error.code != 0:
        print ("dropping motion message:", resp.error.message)
        return
    # then break it up into proof + body
    proof, body = decomposeMessage(resp.content)
    
    # now validate the proof
    resp = wave.VerifyProof(wv.VerifyProofParams(
        proofDER=proof,
        requiredRTreePolicy=wv.RTreePolicy(
            namespace=partner_home_namespace,
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
    
    partner_occupied = body["occupied"]
    
mqtt.subscribe(partner_nickname+"/smarthome/thermostat/report", partner_occupancy_cb)
mqtt.subscribe(partner_nickname+"/smarthome/motion/report", partner_motion_cb)