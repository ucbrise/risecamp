from aboveground.ground import GroundClient
import os

gc = GroundClient()

def add_file(file_path):
    # get file system information
    stat = os.stat(file_path)

    # get the file size
    size = stat[6]

    # get the file creation time
    ctime = stat[-1]

    # add the relevant information to the tags in Javascript
    tags = {
        'size': {
            'key': 'size',
            'value': size,
            'type': 'integer'
        },
        'ctime': {
            'key': 'ctime',
            'value': ctime,
            'type': 'integer'
        },
        'path': {
            'key': 'path',
            'value': file_path,
            'type': 'string'
        }
    }

    # either retrieve an existing structure or create a new one
    sv_id = create_structure()

    # get the name of the file
    file_path = file_path.split('/')[-1]

    # create a new node
    node_id = gc.create_node(file_path, file_path)['id']

    # create and return the node version; the empty array is the list of the
    # parent versions of this version (i.e., none)
    node_version = gc.create_node_version(node_id, tags, [], structure_id=sv_id)
    return node_version


def create_structure():
    # attempt to retrieve the structure
    struct = gc.get_structure("dataset")

    if struct == None:
        # if it does not exist, create a new structure and structure version
        structure_id = gc.create_structure("dataset", "dataset")['id']
        return gc.create_structure_version({"size": "integer", "ctime": "integer", "path": "string"}, structure_id)['id']
    else:
        # if it already exists, return the most recent version of it
        return gc.get_structure_latest("dataset")[0]
