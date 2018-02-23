import difflib


def get_matches(sentence, possibilities, n=1):
    return difflib.get_close_matches(sentence.lower(),
                                     [p.lower() for p in possibilities],
                                      n)


def get_match(sentence, possibilities, n=1):
    matches = get_matches(sentence, possibilities, n)
    if (len(matchednames) > 0):
        return matches[0]
    return None


def get_match_score(string1, string2):
    return difflib.SequenceMatcher(None, string1, string2).ratio()
