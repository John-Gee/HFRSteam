import os.path


class Mapper:
    LINK          = '<->'
    __mappingfile = ''
    __mapping     = {}

    def __init__(self, mappingfile):
        if(os.path.exists(mappingfile)):
            self.__mappingfile = mappingfile
            self.__mapping     = dict()
            f = open(self.__mappingfile, 'r')
            for line in iter(f):
                line = line.strip()
                # remove the quotes needed to protect spaces
                # at the end of names when steam messed up
                line = line[1:-1]
                if (self.LINK in line):
                    tup = line.split(self.LINK)
                    if (len(tup) == 2):
                        self.__mapping[tup[0].lower()] = (tup[1].lower(),)
                    elif (len(tup) == 3):
                        self.__mapping[tup[0].lower()] = (tup[1].lower(),
                                                          tup[2].lower())
                    else:
                        print('More members in the line than excepted!')

    def save_mapping(self):
        if ((self.__mapping == None) or (len(self.__mapping) == 0)):
            return

        f = open(self.__mappingfile, 'w')
        for key in sorted(self.__mapping):
            line = '"{0}{1}{2}'.format(key, self.LINK, self.__mapping[key][0])
            if (len(self.__mapping[key]) == 2):
                line += '{0}{1}'.format(self.LINK, self.__mapping[key][1])
            line += '"'
            f.write(line)
            f.write(os.linesep)

    def add_to_mapping(self, left, middle, right=None):
        if (left not in self.__mapping):
            if (right):
                self.__mapping[left.lower()] = (middle.lower(), right.lower())
            else:
                self.__mapping[left.lower()] = (middle.lower())
        else:
            print('Impossible to add mapping, {0} is already in the mapper'.
                  format(left))

    def get_mapping(self, left):
        if (left.lower() in self.__mapping):
            return self.__mapping[left.lower()]
        return None

