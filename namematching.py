import difflib
import re
import roman


def get_matches(sentence, possibilities, n=3, cutoff=0.6):
    return difflib.get_close_matches(sentence, possibilities,
                                      n, cutoff)


def get_clean_matches(sentence, possibilities, cutoff=0.6):
    matches      = get_matches(sentence, possibilities, 10, cutoff)
    cleanmatches = []
    for match in matches:
        ms = re.search('.*(\d+)\Z', sentence)
        mm = re.search('.*(\d+)\Z', match)
        if (((ms) and (mm) and (ms.group(1) == mm.group(1)))
            or ((not ms) and (not mm))):
            cleanmatches.append(match)
    return cleanmatches


def get_match(sentence, possibilities, cutoff=0.6):
    matches = get_matches(sentence, possibilities, 1, cutoff)
    if (len(matches) == 1):
        return matches[0]
    return None


def get_match_score(string1, string2):
    return difflib.SequenceMatcher(None, string1, string2).ratio()


def nameclean(orig):
    name = orig.encode('ascii', errors='ignore').decode('ascii')
    name = name.upper().strip()
    name = name.replace('GOTY', 'GAME OF THE YEAR')
    ignoredphrases = ['\(', '\)', 'the', 'with', 'Early Access', 'bundle', 'and', '&', 'in', 'vr', 'beta', 'Double Pack', 'Pack', 'Free to Play', 'Edition']
    for phrase in ignoredphrases:
        name = re.sub(r'\b{0}\b'.format(phrase), '', name, flags=re.IGNORECASE)
    name = re.sub(r'\bone\b', '1', name, flags=re.IGNORECASE)
    name = re.sub(r'\btwo\b', '2', name, flags=re.IGNORECASE)
    name = re.sub(r'\b40k\b', '40,000', name, flags=re.IGNORECASE)
    name = re.sub(r'\+', 'PLUS', name, flags=re.IGNORECASE)
    name = re.sub(r'[^\w\s]',' ', name, flags=re.IGNORECASE)
    name = re.sub(r'(\A|\s)(\b(?=[MDCLXVI]+\b)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b)(\s|\Z)', lambda x: x.group(1) + str(roman.fromRoman(x.group(2).strip())) + x.group(6) if (x.group(0).strip()) else '', name, flags=re.IGNORECASE)
    name = re.sub(r'(\w*)s\b', r'\1', name, flags=re.IGNORECASE)
    words = name.split()
    name = ' '.join(sorted(set(words), key=words.index))
    name = re.sub(r'\s+', '', name, flags=re.IGNORECASE).strip()
    return name
