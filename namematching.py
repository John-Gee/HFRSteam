import difflib


def get_match(sentence, possibilities, n=1):
    return difflib.get_close_matches(sentence, possibilities, n)


def get_match_score(string1, string2):
    return difflib.SequenceMatcher(None, string1, string2).ratio()
