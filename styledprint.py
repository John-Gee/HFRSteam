from colorama import Fore
from enum import Enum


class Verbosity(Enum):
    Error   = 0
    Warning = 1
    Debug   = 2
    def __ge__(self, other):
        if (self.__class__ is other.__class__):
            return self.value >= other.value
        return NotImplemented

default_verbosity = Verbosity.Error


def set_verbosity(level):
    global default_verbosity
    default_verbosity = Verbosity(level)


def print_styled(verbosity, color, text, *args):
    if (default_verbosity >= verbosity):
        print(color + text + Fore.RESET, *args)


def print_error(text, *args):
    print_styled(Verbosity.Error, Fore.RED, text, *args)


def print_info(text, *args):
    print_styled(Verbosity.Warning, Fore.YELLOW, text, *args)


def print_info_begin(text, *args):
    print_info('******* {0} *******'.format(text), *args)


def print_info_end(text, *args):
    print_info('******* {0} *******\n'.format(text), *args)


def print_debug(text, *args):
    print_styled(Verbosity.Debug, Fore.CYAN, text, *args)
