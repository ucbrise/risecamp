# Double (1.0.2.0/32): Double
# This payload is an 8 byte long IEEE 754 double floating point value encoded in
# little endian. This should only be used if the semantic meaning is obvious in
# the context, otherwise a PID with a more specific semantic meaning should be
# used.
PONumDouble = 16777728
PODFMaskDouble = "1.0.2.0/32"
PODFDouble = (1, 0, 2, 0)
POMaskDouble = 32

# BWMessage (1.0.1.1/32): Packed Bosswave Message
# This object contains an entire signed and encoded bosswave message
PONumBWMessage = 16777473
PODFMaskBWMessage = "1.0.1.1/32"
PODFBWMessage = (1, 0, 1, 1)
POMaskBWMessage = 32

# ChirpFeed (2.0.11.1/32): Chirp Anemometer Feed
# A map containing - vendor: the vendor implementing the algorithm - sensor: the
# anemometer this data is for - algorithm: symbol name of the algorithm
# type/version - tofs: a list of src,dst,val time of flight measurements in
# microseconds - extradata: a list of string extra from the algorithm
PONumChirpFeed = 33557249
PODFMaskChirpFeed = "2.0.11.1/32"
PODFChirpFeed = (2, 0, 11, 1)
POMaskChirpFeed = 32

# L7G1Stats (2.0.10.2/32): L7G v1 stats message
# tbd
PONumL7G1Stats = 33556994
PODFMaskL7G1Stats = "2.0.10.2/32"
PODFL7G1Stats = (2, 0, 10, 2)
POMaskL7G1Stats = 32

# SpawnpointSvcHb (2.0.2.2/32): SpawnPoint Service Heartbeat
# A heartbeat from spawnpoint about a currently running service. It is a msgpack
# dictionary that contains the keys "SpawnpointURI", "Name", "Time", "MemAlloc",
# and "CpuShares".
PONumSpawnpointSvcHb = 33554946
PODFMaskSpawnpointSvcHb = "2.0.2.2/32"
PODFSpawnpointSvcHb = (2, 0, 2, 2)
POMaskSpawnpointSvcHb = 32

# Wavelet (1.0.6.1/32): Wavelet binary
# This object contains a BOSSWAVE Wavelet
PONumWavelet = 16778753
PODFMaskWavelet = "1.0.6.1/32"
PODFWavelet = (1, 0, 6, 1)
POMaskWavelet = 32

# SpawnpointHeartbeat (2.0.2.1/32): SpawnPoint heartbeat
# A heartbeat message from spawnpoint. It is a msgpack dictionary that contains
# the keys "Alias", "Time", "TotalMem", "TotalCpuShares", "AvailableMem", and
# "AvailableCpuShares".
PONumSpawnpointHeartbeat = 33554945
PODFMaskSpawnpointHeartbeat = "2.0.2.1/32"
PODFSpawnpointHeartbeat = (2, 0, 2, 1)
POMaskSpawnpointHeartbeat = 32

# ROPermissionDChain (0.0.0.18/32): Permission DChain
# A permission dchain
PONumROPermissionDChain = 18
PODFMaskROPermissionDChain = "0.0.0.18/32"
PODFROPermissionDChain = (0, 0, 0, 18)
POMaskROPermissionDChain = 32

# GilesTimeseriesResponse (2.0.8.4/32): Giles Timeseries Response
# A dictionary containing timeseries results for a query. Has 2 keys: - Nonce: the
# uint32 number corresponding to the query nonce that generated this timeseries
# response - Data: list of GilesTimeseries (2.0.8.5) objects - Stats: list of
# GilesStatistics (2.0.8.6) objects
PONumGilesTimeseriesResponse = 33556484
PODFMaskGilesTimeseriesResponse = "2.0.8.4/32"
PODFGilesTimeseriesResponse = (2, 0, 8, 4)
POMaskGilesTimeseriesResponse = 32

# ROEntityWKey (0.0.0.50/32): Entity with signing key
# An entity with signing key
PONumROEntityWKey = 50
PODFMaskROEntityWKey = "0.0.0.50/32"
PODFROEntityWKey = (0, 0, 0, 50)
POMaskROEntityWKey = 32

# ROAccessDOT (0.0.0.32/32): Access DOT
# An access DOT
PONumROAccessDOT = 32
PODFMaskROAccessDOT = "0.0.0.32/32"
PODFROAccessDOT = (0, 0, 0, 32)
POMaskROAccessDOT = 32

# ROOriginVK (0.0.0.49/32): Origin verifying key
# The origin VK of a message that does not contain a PAC
PONumROOriginVK = 49
PODFMaskROOriginVK = "0.0.0.49/32"
PODFROOriginVK = (0, 0, 0, 49)
POMaskROOriginVK = 32

# GilesKeyValueMetadata (2.0.8.3/32): Giles Key Value Metadata
# A dictionary containing metadata results for a single stream. Has 2 keys: -
# UUID: string identifying the stream - Metadata: a map of keys->values of
# metadata
PONumGilesKeyValueMetadata = 33556483
PODFMaskGilesKeyValueMetadata = "2.0.8.3/32"
PODFGilesKeyValueMetadata = (2, 0, 8, 3)
POMaskGilesKeyValueMetadata = 32

# L7G1Raw (2.0.10.1/32): L7G v1 Raw message
# A map containing - srcmac: the MAC address of the sensor - srcip: the IP address
# of the sensor, if available - type: the 16 bit L7G type field - popid: the ID of
# the point of presence that received the packet - poptime: the boot time (in us)
# of the pop when the message was received - brtime: the real time (in ns) at the
# border router when the message was relayed to bosswave - rssi: the RSSI of the
# message at the pop, if available - lqi: the LQI of the message at the pop, if
# available - payload: the raw message
PONumL7G1Raw = 33556993
PODFMaskL7G1Raw = "2.0.10.1/32"
PODFL7G1Raw = (2, 0, 10, 1)
POMaskL7G1Raw = 32

# Binary (0.0.0.0/4): Binary protocols
# This is a superclass for classes that are generally unreadable in their plain
# form and require translation.
PONumBinary = 0
PODFMaskBinary = "0.0.0.0/4"
PODFBinary = (0, 0, 0, 0)
POMaskBinary = 4

# FMDIntentString (64.0.1.1/32): FMD Intent String
# A plain string used as an intent for the follow-me display service.
PONumFMDIntentString = 1073742081
PODFMaskFMDIntentString = "64.0.1.1/32"
PODFFMDIntentString = (64, 0, 1, 1)
POMaskFMDIntentString = 32

# MsgPack (2.0.0.0/8): MsgPack
# This class is for schemas that are represented in MsgPack
PONumMsgPack = 33554432
PODFMaskMsgPack = "2.0.0.0/8"
PODFMsgPack = (2, 0, 0, 0)
POMaskMsgPack = 8

# ROAccessDChain (0.0.0.2/32): Access DChain
# An access dchain
PONumROAccessDChain = 2
PODFMaskROAccessDChain = "0.0.0.2/32"
PODFROAccessDChain = (0, 0, 0, 2)
POMaskROAccessDChain = 32

# HamiltonBase (2.0.4.0/24): Hamilton Messages
# This is the base class for messages used with the Hamilton motes. The only key
# guaranteed is "#" that contains a uint16 representation of the serial of the
# mote the message is destined for or originated from.
PONumHamiltonBase = 33555456
PODFMaskHamiltonBase = "2.0.4.0/24"
PODFHamiltonBase = (2, 0, 4, 0)
POMaskHamiltonBase = 24

# YAML (67.0.0.0/8): YAML
# This class is for schemas that are represented in YAML
PONumYAML = 1124073472
PODFMaskYAML = "67.0.0.0/8"
PODFYAML = (67, 0, 0, 0)
POMaskYAML = 8

# LogDict (2.0.1.0/24): LogDict
# This class is for log messages encoded in msgpack
PONumLogDict = 33554688
PODFMaskLogDict = "2.0.1.0/24"
PODFLogDict = (2, 0, 1, 0)
POMaskLogDict = 24

# RORevocation (0.0.0.80/32): Revocation
# A revocation for an Entity or a DOT
PONumRORevocation = 80
PODFMaskRORevocation = "0.0.0.80/32"
PODFRORevocation = (0, 0, 0, 80)
POMaskRORevocation = 32

# JSON (65.0.0.0/8): JSON
# This class is for schemas that are represented in JSON
PONumJSON = 1090519040
PODFMaskJSON = "65.0.0.0/8"
PODFJSON = (65, 0, 0, 0)
POMaskJSON = 8

# InterfaceDescriptor (2.0.6.1/32): InterfaceDescriptor
# This object is used to describe an interface. It contains "uri",
# "iface","svc","namespace" "prefix" and "metadata" keys.
PONumInterfaceDescriptor = 33555969
PODFMaskInterfaceDescriptor = "2.0.6.1/32"
PODFInterfaceDescriptor = (2, 0, 6, 1)
POMaskInterfaceDescriptor = 32

# GilesKeyValueQuery (2.0.8.1/32): Giles Key Value Query
# Expresses a query to a Giles instance. Expects 2 keys: - Query: A Giles query
# string following syntax at
# https://gtfierro.github.io/giles2/interface/#querylang - Nonce: a unique uint32
# number for identifying the results of this query
PONumGilesKeyValueQuery = 33556481
PODFMaskGilesKeyValueQuery = "2.0.8.1/32"
PODFGilesKeyValueQuery = (2, 0, 8, 1)
POMaskGilesKeyValueQuery = 32

# GilesMetadataResponse (2.0.8.2/32): Giles Metadata Response
# Dictionary containing metadata results for a query. Has 2 keys: - Nonce: the
# uint32 number corresponding to the query nonce that generated this metadata
# response - Data: list of GilesKeyValueMetadata (2.0.8.3) objects
PONumGilesMetadataResponse = 33556482
PODFMaskGilesMetadataResponse = "2.0.8.2/32"
PODFGilesMetadataResponse = (2, 0, 8, 2)
POMaskGilesMetadataResponse = 32

# ROEntity (0.0.0.48/32): Entity
# An entity
PONumROEntity = 48
PODFMaskROEntity = "0.0.0.48/32"
PODFROEntity = (0, 0, 0, 48)
POMaskROEntity = 32

# HSBLightMessage (2.0.5.1/32): HSBLight Message
# This object may contain "hue", "saturation", "brightness" fields with a float
# from 0 to 1. It may also contain an "state" key with a boolean. Omitting fields
# leaves them at their previous state.
PONumHSBLightMessage = 33555713
PODFMaskHSBLightMessage = "2.0.5.1/32"
PODFHSBLightMessage = (2, 0, 5, 1)
POMaskHSBLightMessage = 32

# HamiltonOR (2.0.11.3/32): Hamilton Orientation
# A map containing - time: nanoseconds since the epoch - other stuff TODO
PONumHamiltonOR = 33557251
PODFMaskHamiltonOR = "2.0.11.3/32"
PODFHamiltonOR = (2, 0, 11, 3)
POMaskHamiltonOR = 32

# SMetadata (2.0.3.1/32): Simple Metadata entry
# This contains a simple "val" string and "ts" int64 metadata entry. The key is
# determined by the URI. Other information MAY be present in the msgpacked object.
# The timestamp is used for merging metadata entries.
PONumSMetadata = 33555201
PODFMaskSMetadata = "2.0.3.1/32"
PODFSMetadata = (2, 0, 3, 1)
POMaskSMetadata = 32

# VenstarControl (2.0.12.2/32): VenstarControl
# Consult the documentation
PONumVenstarControl = 33557506
PODFMaskVenstarControl = "2.0.12.2/32"
PODFVenstarControl = (2, 0, 12, 2)
POMaskVenstarControl = 32

# Blob (1.0.0.0/8): Blob
# This is a class for schemas that do not use a public encoding format. In general
# it should be avoided. Schemas below this should include the key "readme" with a
# url to a description of the schema that is sufficiently detailed to allow for a
# developer to reverse engineer the protocol if required.
PONumBlob = 16777216
PODFMaskBlob = "1.0.0.0/8"
PODFBlob = (1, 0, 0, 0)
POMaskBlob = 8

# TimeseriesReading (2.0.9.16/28): Timeseries Reading
# Map with at least these keys: - UUID: string UUID uniquely identifying this
# timeseries - Time: int64 timestamp, UTC nanoseconds - Value: float64 value
PONumTimeseriesReading = 33556752
PODFMaskTimeseriesReading = "2.0.9.16/28"
PODFTimeseriesReading = (2, 0, 9, 16)
POMaskTimeseriesReading = 28

# ROPermissionDOT (0.0.0.33/32): Permission DOT
# A permission DOT
PONumROPermissionDOT = 33
PODFMaskROPermissionDOT = "0.0.0.33/32"
PODFROPermissionDOT = (0, 0, 0, 33)
POMaskROPermissionDOT = 32

# BWRoutingObject (0.0.0.0/24): Bosswave Routing Object
# This class and schema block is reserved for bosswave routing objects represented
# using the full PID.
PONumBWRoutingObject = 0
PODFMaskBWRoutingObject = "0.0.0.0/24"
PODFBWRoutingObject = (0, 0, 0, 0)
POMaskBWRoutingObject = 24

# BW2Chat_ChatMessage (2.0.7.2/32): BW2Chat_ChatMessage
# A textual message to be sent to all members of a chatroom. This is a dictionary
# with three keys: 'Room', the name of the room to publish to (this is actually
# implicit in the publishing), 'From', the alias you are using for the chatroom,
# and 'Message', the actual string to be displayed to all users in the room.
PONumBW2Chat_ChatMessage = 33556226
PODFMaskBW2Chat_ChatMessage = "2.0.7.2/32"
PODFBW2Chat_ChatMessage = (2, 0, 7, 2)
POMaskBW2Chat_ChatMessage = 32

# BW2Chat_CreateRoomMessage (2.0.7.1/32): BW2Chat_CreateRoomMessage
# A dictionary with a single key "Name" indicating the room to be created. This
# will likely be deprecated.
PONumBW2Chat_CreateRoomMessage = 33556225
PODFMaskBW2Chat_CreateRoomMessage = "2.0.7.1/32"
PODFBW2Chat_CreateRoomMessage = (2, 0, 7, 1)
POMaskBW2Chat_CreateRoomMessage = 32

# CapnP (3.0.0.0/8): Captain Proto
# This class is for captain proto interfaces. Schemas below this should include
# the key "schema" with a url to their .capnp file
PONumCapnP = 50331648
PODFMaskCapnP = "3.0.0.0/8"
PODFCapnP = (3, 0, 0, 0)
POMaskCapnP = 8

# ROAccessDChainHash (0.0.0.1/32): Access DChain hash
# An access dchain hash
PONumROAccessDChainHash = 1
PODFMaskROAccessDChainHash = "0.0.0.1/32"
PODFROAccessDChainHash = (0, 0, 0, 1)
POMaskROAccessDChainHash = 32

# ROPermissionDChainHash (0.0.0.17/32): Permission DChain hash
# A permission dchain hash
PONumROPermissionDChainHash = 17
PODFMaskROPermissionDChainHash = "0.0.0.17/32"
PODFROPermissionDChainHash = (0, 0, 0, 17)
POMaskROPermissionDChainHash = 32

# AccountBalance (64.0.1.2/32): Account balance
# A comma seperated representation of an account and its balance as
# addr,decimal,human_readable. For example
# 0x49b1d037c33fdaad75d2532cd373fb5db87cc94c,57203431159181996982272,57203.4311
# Ether  . Be careful in that the decimal representation will frequently be bigger
# than an int64.
PONumAccountBalance = 1073742082
PODFMaskAccountBalance = "64.0.1.2/32"
PODFAccountBalance = (64, 0, 1, 2)
POMaskAccountBalance = 32

# SpawnpointConfig (67.0.2.0/32): SpawnPoint config
# A configuration file for SpawnPoint (github.com/immesys/spawnpoint)
PONumSpawnpointConfig = 1124073984
PODFMaskSpawnpointConfig = "67.0.2.0/32"
PODFSpawnpointConfig = (67, 0, 2, 0)
POMaskSpawnpointConfig = 32

# HamiltonOT (2.0.11.2/32): Hamilton OT
# A map containing - time: nanoseconds since the epoch - other stuff TODO
PONumHamiltonOT = 33557250
PODFMaskHamiltonOT = "2.0.11.2/32"
PODFHamiltonOT = (2, 0, 11, 2)
POMaskHamiltonOT = 32

# BW2Chat_LeaveRoom (2.0.7.4/32): BW2Chat_LeaveRoom
# Notify users in the chatroom that you have left. Dictionary with a single key
# "Alias" that has a value of your nickname
PONumBW2Chat_LeaveRoom = 33556228
PODFMaskBW2Chat_LeaveRoom = "2.0.7.4/32"
PODFBW2Chat_LeaveRoom = (2, 0, 7, 4)
POMaskBW2Chat_LeaveRoom = 32

# GilesTimeseries (2.0.8.5/32): Giles Timeseries
# A dictionary containing timeseries results for a single stream. has 3 keys: -
# UUID: string identifying the stream - Times: list of uint64 timestamps - Values:
# list of float64 values Times and Values will line up, e.g. index i of Times
# corresponds to index i of values
PONumGilesTimeseries = 33556485
PODFMaskGilesTimeseries = "2.0.8.5/32"
PODFGilesTimeseries = (2, 0, 8, 5)
POMaskGilesTimeseries = 32

# GilesArchiveRequest (2.0.8.0/32): Giles Archive Request
# A MsgPack dictionary with the following keys: - URI (optional): the URI to
# subscribe to for data - PO (required): which PO object type to extract from
# messages on the URI - UUID (optional): the UUID to use, else it is consistently
# autogenerated. - Value (required): ObjectBuilder expression for how to extract
# the value - Time (optional): ObjectBuilder expression for how to extract any
# timestamp - TimeParse (optional): How to parse that timestamp - MetadataURI
# (optional): a base URI to scan for metadata (expands to uri/!meta/+) -
# MetadataBlock (optional): URI containing a key-value structure of metadata -
# MetadataExpr (optional): ObjectBuilder expression to search for a key-value
# structure in the current message for metadata ObjectBuilder expressions are
# documented at: https://github.com/gtfierro/giles2/tree/master/objectbuilder
PONumGilesArchiveRequest = 33556480
PODFMaskGilesArchiveRequest = "2.0.8.0/32"
PODFGilesArchiveRequest = (2, 0, 8, 0)
POMaskGilesArchiveRequest = 32

# ROExpiry (0.0.0.64/32): Expiry
# Sets an expiry for the message
PONumROExpiry = 64
PODFMaskROExpiry = "0.0.0.64/32"
PODFROExpiry = (0, 0, 0, 64)
POMaskROExpiry = 32

# Giles_Messages (2.0.8.0/24): Giles Messages
# Messages for communicating with a Giles archiver
PONumGiles_Messages = 33556480
PODFMaskGiles_Messages = "2.0.8.0/24"
PODFGiles_Messages = (2, 0, 8, 0)
POMaskGiles_Messages = 24

# BinaryActuation (1.0.1.0/32): Binary actuation
# This payload object is one byte long, 0x00 for off, 0x01 for on.
PONumBinaryActuation = 16777472
PODFMaskBinaryActuation = "1.0.1.0/32"
PODFBinaryActuation = (1, 0, 1, 0)
POMaskBinaryActuation = 32

# RODRVK (0.0.0.51/32): Designated router verifying key
# a 32 byte designated router verifying key
PONumRODRVK = 51
PODFMaskRODRVK = "0.0.0.51/32"
PODFRODRVK = (0, 0, 0, 51)
POMaskRODRVK = 32

# BW2ChatMessages (2.0.7.0/24): BW2ChatMessages
# These are MsgPack dictionaries sent for the BW2Chat program
# (https://github.com/gtfierro/bw2chat)
PONumBW2ChatMessages = 33556224
PODFMaskBW2ChatMessages = "2.0.7.0/24"
PODFBW2ChatMessages = (2, 0, 7, 0)
POMaskBW2ChatMessages = 24

# VenstarInfo (2.0.12.1/32): VenstarInfo
# Consult the venstar API documentation at
# http://developer.venstar.com/restcalls.html
PONumVenstarInfo = 33557505
PODFMaskVenstarInfo = "2.0.12.1/32"
PODFVenstarInfo = (2, 0, 12, 1)
POMaskVenstarInfo = 32

# UniqueObjectStream (2.0.9.0/24): Unique Object Stream
# An object that is part of a (possibly ordered) stream, identified by UUID. It
# must contain at least a UUID key uniquely identifying the collection
PONumUniqueObjectStream = 33556736
PODFMaskUniqueObjectStream = "2.0.9.0/24"
PODFUniqueObjectStream = (2, 0, 9, 0)
POMaskUniqueObjectStream = 24

# SpawnpointLog (2.0.2.0/32): Spawnpoint stdout
# This contains stdout data from a spawnpoint container. It is a msgpacked
# dictionary that contains a "service" key, a "time" key (unix nano timestamp) and
# a "contents" key and a "spalias" key.
PONumSpawnpointLog = 33554944
PODFMaskSpawnpointLog = "2.0.2.0/32"
PODFSpawnpointLog = (2, 0, 2, 0)
POMaskSpawnpointLog = 32

# BW2Chat_JoinRoom (2.0.7.3/32): BW2Chat_JoinRoom
# Notify users in the chatroom that you have joined. Dictionary with a single key
# "Alias" that has a value of your nickname
PONumBW2Chat_JoinRoom = 33556227
PODFMaskBW2Chat_JoinRoom = "2.0.7.3/32"
PODFBW2Chat_JoinRoom = (2, 0, 7, 3)
POMaskBW2Chat_JoinRoom = 32

# XML (66.0.0.0/8): XML
# This class is for schemas that are represented in XML
PONumXML = 1107296256
PODFMaskXML = "66.0.0.0/8"
PODFXML = (66, 0, 0, 0)
POMaskXML = 8

# HamiltonTelemetry (2.0.4.64/26): Hamilton Telemetry
# This object contains a "#" field for the serial number, as well as possibly
# containing an "A" field with a list of X, Y, and Z accelerometer values. A "T"
# field containing the temperature as an integer in degrees C multiplied by 10000,
# and an "L" field containing the illumination in Lux.
PONumHamiltonTelemetry = 33555520
PODFMaskHamiltonTelemetry = "2.0.4.64/26"
PODFHamiltonTelemetry = (2, 0, 4, 64)
POMaskHamiltonTelemetry = 26

# Text (64.0.0.0/4): Human readable text
# This is a superclass for classes that are moderately understandable if they are
# read directly in their binary form. Generally these are protocols that were
# designed specifically to be human readable.
PONumText = 1073741824
PODFMaskText = "64.0.0.0/4"
PODFText = (64, 0, 0, 0)
POMaskText = 4

# GilesStatistics (2.0.8.6/32): Giles Statistics
# A dictionary containing timeseries results for a single stream. has 3 keys: -
# UUID: string identifying the stream - Times: list of uint64 timestamps - Count:
# list of uint64 values - Min: list of float64 values - Mean: list of float64
# values - Max: list of float64 values All fields will line up, e.g. index i of
# Times corresponds to index i of Count
PONumGilesStatistics = 33556486
PODFMaskGilesStatistics = "2.0.8.6/32"
PODFGilesStatistics = (2, 0, 8, 6)
POMaskGilesStatistics = 32

# TSTaggedMP (2.0.3.0/24): TSTaggedMP
# This superclass describes "ts"->int64 tagged msgpack objects. The timestamp is
# used for merging entries and determining which is later and should be the final
# value.
PONumTSTaggedMP = 33555200
PODFMaskTSTaggedMP = "2.0.3.0/24"
PODFTSTaggedMP = (2, 0, 3, 0)
POMaskTSTaggedMP = 24

# String (64.0.1.0/32): String
# A plain string with no rigid semantic meaning. This can be thought of as a print
# statement. Anything that has semantic meaning like a process log should use a
# different schema.
PONumString = 1073742080
PODFMaskString = "64.0.1.0/32"
PODFString = (64, 0, 1, 0)
POMaskString = 32

# GilesQueryError (2.0.8.9/32): Giles Query Error
# A dictionary containing an error returned by a query. Has 3 keys: - Query: the
# string query that was sent - Nonce: the nonce in the query request - Error:
# string of the returned error
PONumGilesQueryError = 33556489
PODFMaskGilesQueryError = "2.0.8.9/32"
PODFGilesQueryError = (2, 0, 8, 9)
POMaskGilesQueryError = 32

