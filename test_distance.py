import Levenshtein

# Some sample text pairs
text_pairs = [
    ("hello", "hallo"),  # similar words
    ("example", "samples"),  # somewhat similar
    ("python", "pythons"),  # plural form
    ("test", "testing"),  # different lengths
    ("Levenshtein", "Levenstein"),  # common typo
    ("distance", "instance"),  # shared letters, different order
    ("giraffe", "refrigerator"),  # not similar
    ("你應該直接告訴我消息內容，而不是提供網站，因為我不是在請你搜尋網站",
     "但我不會英文你應該直接告訴我消息內容，而不是提供網站，因為我不是在請你搜尋網站")  # not similar
]


def get_similarity(s1, s2):
    distance = Levenshtein.distance(s1, s2)
    total = max(len(s1), len(s2))
    ratio = 1 - float(distance) / float(total)
    return ratio


def print_levenshtein_distance(text_pairs):
    for s1, s2 in text_pairs:
        distance = Levenshtein.distance(s1, s2)
        similarity = get_similarity(s1, s2)
        print(f"[{s1}] - [{s2}] distance = {distance}, similarity = {similarity}")


if __name__ == '__main__':
    print_levenshtein_distance(text_pairs)
