import sys

def substringafter(string, after, offset = 0):
    if (after.lower() in string.lower()):
        return string[string.lower().index(after.lower()) + len(after) + offset:]
    return string

def substringbefore(string, before, offset = 0):
    if (before.lower() in string.lower()):
        return string[:string.lower().index(before.lower()) + offset]
    return string

def rsubstringafter(string, after, offset = 0):
    if (after.lower() in string.lower()):
        return string[string.lower().rindex(after.lower()) + len(after) + offset:]
    return string

def rsubstringbefore(string, before, offset = 0):
    if (before.lower() in string.lower()):
        return string[:string.lower().rindex(before.lower()) + offset]
    return string
