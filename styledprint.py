from colorama import Fore


def print_styled(color, text, *args):
    print(color + text + Fore.RESET, *args)


def print_error(text, *args):
    print_styled(Fore.RED, text, *args)


def print_info(text, *args):
    print_styled(Fore.YELLOW, text, *args)


def print_info_begin(text, *args):
    print_info('******* {0} *******'.format(text), *args)


def print_info_end(text, *args):
    print_info('******* {0} *******\n'.format(text), *args)
