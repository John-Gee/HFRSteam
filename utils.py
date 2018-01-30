import requests


class ComparableClass():
    def compare(self, other):
        for key in self.__dict__:
            if(isinstance(self.__dict__[key], ComparableClass)):
                self.__dict__[key].compare(other.__dict__[key])
            elif (self.__dict__[key] != other.__dict__[key]):
                print('{0} vs {1} for {2}'.format(
                    self.__dict__[key], other.__dict__[key], key))
