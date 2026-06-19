import re

STOPWORDS = [
    "kabupaten", "kota", "dinas", "badan", "bagian"
]

def normalize_entity(name: str) -> str:
    name = name.lower().strip()

    # remove punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)

    # remove government stopwords
    tokens = name.split()
    tokens = [t for t in tokens if t not in STOPWORDS]

    return " ".join(tokens)