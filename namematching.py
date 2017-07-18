import difflib


def get_match(sentance, possibilities, n=1):
    return difflib.get_close_matches(sentance, possibilities, n)
