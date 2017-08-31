import base64 
import sys

def encode_config(filename):
    file = open(filename, 'rb')
    data = file.read()
    config_string = base64.b64encode(data)
    print(config_string)


def decode_config(config_string, filename):
    data = base64.b64decode(config_string) 
    file = open(filename, 'wb')
    file.write(data)
    print("decode is done.")

if sys.argv[1] == "encode":
    encode_config(sys.argv[2])
elif sys.argv[1] == "decode":
    decode_config(sys.argv[2], sys.argv[3])
else:
    print("python config_encoder.py encode/decode filename/string")