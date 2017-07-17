import difflib


def get_match(sentence, possibilities, n=1):
    return difflib.get_close_matches(sentence, possibilities, n)
