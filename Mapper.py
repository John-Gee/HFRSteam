import os.path
import sys
import difflib

_mappingfile = "mapping.txt"
_link = "<->"
_mapping = dict()

if(os.path.exists(_mappingfile)):
    f = open(_mappingfile, "r")
    for line in iter(f):
        line = line.strip()
        # remove the quotes needed to protect spaces at the end of names when steam messed up
        line = line[1:-1]
        if (_link in line):
            couple = line.split(_link)
            if (len(couple) == 2):
                _mapping[couple[0]] = couple[1]

def save_mapping():
    f = open(_mappingfile, "w")
    for key in sorted(_mapping):
        line = "\"" + key + _link + _mapping[key] + "\""
        f.write(line)
        f.write(os.linesep)

def add_to_mapping(left, right):
    if (left not in _mapping):
        _mapping[left] = right
    else:
        print("Impossible to add mapping, " + left + " is already in the mapper")

def get_mapping(left):
    if (left in _mapping):
        return _mapping[left]
    return None

def get_match(sentance, possibilities):
    return difflib.get_close_matches(sentance, possibilities, 1)
