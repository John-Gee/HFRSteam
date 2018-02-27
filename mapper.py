import os.path

import styledprint
import utils

class Mapper:
    def __init__(self, mappingfile):
        if(os.path.exists(mappingfile)):
            self.LINK        = '<->'
            self.mappingfile = mappingfile
            self.mapping     = utils.DictCaseInsensitive()
            f = open(self.mappingfile, 'r', encoding='utf8')
            for line in iter(f):
                line = line.strip()
                # remove the quotes needed to protect spaces
                # at the end of names when steam messed up
                line = line[1:-1]
                if (self.LINK in line):
                    tup = line.split(self.LINK)
                    if (len(tup) <= 1):
                        styledprint.print_info('The line does not '
                                               'contain enough members',
                                               line)
                        continue

                    key   = tup[0]
                    value = tup[1].lower().strip('/');
                    if (key in self.mapping):
                        styledprint.print_info('The key {0} is already in the mapper!'
                                                .format(key))
                        continue
                    if (len(tup) == 2):
                        self.mapping[key] = (value,)
                    elif (len(tup) == 3):
                        self.mapping[key] = (value, tup[2])
                    else:
                        styledprint.print_info('More members in the line than excepted!')


    def save_mapping(self):
        if ((self.mapping == None) or (len(self.mapping) == 0)):
            return

        f = open(self.mappingfile, 'w', encoding='utf8')
        for key in sorted(self.mapping):
            line = '"{0}{1}{2}'.format(key, self.LINK, self.mapping[key][0])
            if (len(self.mapping[key]) == 2):
                line += '{0}{1}'.format(self.LINK, self.mapping[key][1])
            line += '"'
            f.write(line)
            f.write(os.linesep)


    def add_to_mapping(self, left, middle, right=None):
        if (left not in self.mapping):
            if (right):
                self.mapping[left] = (middle.lower(), right)
            else:
                self.mapping[left] = (middle.lower(),)
        else:
            styledprint.print_info('Impossible to add mapping, {0} is already in the mapper'.
                  format(left))


    def remove_from_mapping(self, left):
        try:
            del self.mapping[left]
        except:
            pass


    def get_mapping(self, left):
        if (left in self.mapping):
            return self.mapping[left]
        return None
