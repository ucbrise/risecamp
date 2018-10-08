def light_controller_cb(msg):
    # the message we are getting here is our OWN light state
    # we need to first decrypt the message
    resp = wave.DecryptMessage(wv.DecryptMessageParams(
        perspective= perspective,
        ciphertext= msg.payload,
        resyncFirst= True))
    if resp.error.code != 0:
        print ("dropping light state message:", resp.error.message)
        return
    # then break it up into proof + body
    proof, body = decomposeMessage(resp.content)
    
    # now validate the proof
    resp = wave.VerifyProof(wv.VerifyProofParams(
        proofDER=proof,
        requiredRTreePolicy=wv.RTreePolicy(
            namespace= homeserver.namespace(), #SOLUTION: our namespace
            statements=[wv.RTreePolicyStatement(
                permissionSet=smarthome_pset,
                permissions=["write"],
                resource="smarthome/light/report",
            )]
        )
    ))
    if resp.error.code != 0:
        print ("dropping message: ", resp.error.message)
        return
        
    # the proof is valid!
    light_state = body["state"] # "on" or "off"
    # SOLUTION:
    mqtt.publish(partner_nickname+"/smarthome/light/control", 
         composeMessage(partnerlightproof, {"state":light_state})) 
    
mqtt.subscribe(my_unique_nickname+"/smarthome/light/report", light_controller_cb)