synonyms = {'temperature': ['weather', 'climate'], 'open': ['launch', 'start'], 'navigate': ['where', 'find']}
list = synonyms.items()


def find_match(s):
    for item in list:
        for word in item[1]:
            if word == s:
                return item[0]

    return "sss"