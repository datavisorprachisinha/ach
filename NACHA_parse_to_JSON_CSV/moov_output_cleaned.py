import json
import argparse

parser = argparse.ArgumentParser(description="Process some arguments.")

parser.add_argument('-f', '--file', type=str, help='JSON to clean')

args = parser.parse_args()

fname = args.file

with open(fname, 'r') as file:
    data = json.load(file)

print('parsing JSON:', fname)

# moov puts file info inside another JSON --> parse out the og file info and remove added fields

error = data['error']
if error != None:
    print('PARSING ERROR, PARSING WHAT IS AVAILABLE:', error)
    ach = data['File']
else:
    ach = data['file']

ach.pop('id')
ach.pop('validateOpts')

with open(fname, 'w') as file:
    json.dump(ach, file)
