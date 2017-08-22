# Generates PO number and dot form constants for use in Python bindings
# Based on "gen_allocations_go.py" in the immesys/bw2bind repo

import requests
import yaml # pyaml on pip

import sys
import textwrap

ALLOCATIONS_URL = "https://raw.githubusercontent.com/immesys/bw2_pid/master/allocations.yaml"

def parseDottedForm(df):
    tokens = df.split(".")
    if len(tokens) != 4:
        print "Invalid PO Dot Form: " + df
        return None, None

    tokenValues = [int(token) for token in tokens]
    po_num = (tokenValues[0] << 24) + (tokenValues[1] << 16) + (tokenValues[2] << 8) + tokenValues[3]
    po_df = tuple(tokenValues)
    return po_df, po_num

if __name__ == '__main__':
    rq = requests.get(ALLOCATIONS_URL)
    if rq.status_code != 200:
        print "Failed to retrieve Bosswave allocations file from GitHub"
        sys.ext(1)

    allocs = yaml.load(rq.text)

    with open("ponames.py", 'w') as f:
        for key, params in allocs.iteritems():
            key_toks = key.split('/')
            if len(key_toks) != 2:
                print "Invalid PO Allocation: " + key_toks
                continue

            mask = int(key_toks[1])
            po_df, po_num = parseDottedForm(key_toks[0])
            if po_num is None:
                print "Invalid PO Dot Form: " + key_toks[0]
                continue

            short_name = params["short"]
            sym_name = params["sym"]
            description = params["desc"]

            f.write("# {} ({}): {}\n".format(sym_name, key, short_name))
            wrapped_desc = textwrap.wrap(description, 80)
            for line in wrapped_desc:
                f.write("# {}\n".format(line))

            f.write('PONum{} = {}\n'.format(sym_name, po_num))
            f.write('PODFMask{} = "{}"\n'.format(sym_name, key))
            f.write('PODF{} = {}\n'.format(sym_name, po_df))
            f.write('POMask{} = {}\n'.format(sym_name, mask))
            f.write('\n')
