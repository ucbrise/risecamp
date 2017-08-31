from ground import GroundClient
import os

gc = GroundClient()

def add_file(file_path):
    stat = os.stat(file_path)

    # get the file size
    size = stat[6]

    # get the file creation time
    ctime = stat[-1]

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

    sv_id = create_structure()

    file_path = file_path.split('/')[-1]

    node_id = gc.create_node(file_path, file_path)['id']
    node_version = gc.create_node_version(node_id, tags, [], structure_id=sv_id)
    return node_version


def create_structure():
    struct = gc.get_structure("dataset")

    if struct == None:
        structure_id = gc.create_structure("dataset", "dataset")['id']
        return gc.create_structure_version({"size": "integer", "ctime": "integer", "path": "string"}, structure_id)['id']
    else:
        return gc.get_structure_latest("dataset")[0]
