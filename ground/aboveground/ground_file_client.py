from ground.client import GroundClient
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
    node_id = gc.createNode(file_path, file_path, {})['id']

    # create and return the node version; the empty array is the list of the
    # parent versions of this version (i.e., none)
    node_version = gc.createNodeVersion(node_id, tags=tags, structure_version_id=sv_id)
    return node_version


def create_structure():
    # attempt to retrieve the structure
    struct = gc.getStructure("dataset")

    if struct == None:
        # if it does not exist, create a new structure and structure version
        structure_id = gc.createStructure("dataset", "dataset", {})['id']
        return gc.createStructureVersion(structure_id, {"size": "integer", "ctime": "integer", "path": "string"})['id']
    else:
        # if it already exists, return the most recent version of it
        sv_id = gc.getStructureLatestVersions("dataset")[0]
        return gc.getStructureVersion(sv_id)
