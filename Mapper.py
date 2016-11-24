import os.path
import sys
import difflib

mappingfile = "mapping.txt"
link = "<->"

class Mapper:
    mapping = dict()

    def __init__(self):
        if(os.path.exists(mappingfile)):
            f = open(mappingfile, "r")
            for line in iter(f):
                line = line.strip()
                # remove the quotes needed to protect spaces at the end of names when steam messed up
                line = line[1:-1]
                if (link in line):
                    couple = line.split(link)
                    if (len(couple) == 2):
                        self.mapping[couple[0]] = couple[1]

    def save_mapping(self):
        f = open(mappingfile, "w")
        for key in sorted(self.mapping):
            line = "\"" + key + link + self.mapping[key] + "\""
            f.write(line)
            f.write(os.linesep)

    def add_to_mapping(self, left, right):
        if (left not in self.mapping):
            self.mapping[left] = right
        else:
            print("Impossible to add mapping, " + left + " is already in the mapper")

    def get_mapping(self, left):
        if (left in self.mapping):
            return self.mapping[left]
        return None

    def get_match(self, sentance, possibilities):
        return difflib.get_close_matches(sentance, possibilities, 1)
