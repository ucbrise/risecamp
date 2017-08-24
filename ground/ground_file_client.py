import ground
import os

gc = GroundClient()

def add_file(file_path):
    stat = os.stat(file_path)

    # get the file size
    size = stat[6]

    # get the file creation time
    ctime = stat[-1]

    sv_id = create_structure()['id']

    node_id = gc.create_node(file_path, file_path)['id']
    gc.create_node_version(node_id, tags)


def create_structure():
    struct = gc.get_structure("dataset")

    if struct == None:
        gc.create_structure("dataset", "dataset")
        return gc.create_structure_version("dataset", {"size": "integer", "ctime": "integer", "path": "string"})
    else:
        return gc.get_structure_latest("dataset")
