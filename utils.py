import inspect
import os
import requests


class DictCaseInsensitive(requests.structures.CaseInsensitiveDict):
    pass


class ComparableClass():
    def compare(self, other):
        for key in self.__dict__:
            if(isinstance(self.__dict__[key], ComparableClass)):
                self.__dict__[key].compare(other.__dict__[key])
            elif (self.__dict__[key] != other.__dict__[key]):
                print('{0} vs {1} for {2}'.format(
                    self.__dict__[key], other.__dict__[key], key))

def get_caller_name():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 3)
    filename = os.path.basename(calframe[2][1])
    function = calframe[2][3]
    return '{0}-{1}'.format(filename, function)
