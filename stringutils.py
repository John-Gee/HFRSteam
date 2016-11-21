import sys

def substringafter(string, after, offset = 0):
    if (after in string):
        return string[string.lower().index(after.lower()) + len(after) + offset:]
    return string

def substringbefore(string, before, offset = 0):
    if (before in string):
        return string[:string.lower().index(before.lower()) + offset]
    return string
