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
                # remove the quotes needed to protect spaces at the end of
                # names when steam messed up
                line = line[1:-1]
                if (self.LINK in line):
                    couple = line.split(self.LINK)
                    if (len(couple) == 2):
                        self.__mapping[couple[0].lower()] = couple[1].lower()

    def save_mapping(self):
        if ((self.__mapping == None) or (len(self.__mapping) == 0)):
            return

        f = open(self.__mappingfile, 'w')
        for key in sorted(self.__mapping):
            line = '"{0}{1}{2}"'.format(key, self.LINK, self.__mapping[key])
            f.write(line)
            f.write(os.linesep)

    def add_to_mapping(self, left, right):
        if (left not in self.__mapping):
            self.__mapping[left.lower()] = right.lower()
        else:
            print('Impossible to add mapping, {0} is already in the mapper'.
                  format(left))

    def get_mapping(self, left):
        if (left.lower() in self.__mapping):
            return self.__mapping[left.lower()]
        return None

