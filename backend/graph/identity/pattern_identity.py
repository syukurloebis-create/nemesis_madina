import hashlib
import json


def build_pattern_key(entities: list, cycle: str) -> str:
    """
    Membuat ID unik pattern agar tidak duplicate.
    """

    normalized_entities = sorted(entities)

    payload = {
        "cycle": cycle,
        "entities": normalized_entities
    }

    raw = json.dumps(payload, sort_keys=True)

    return hashlib.sha256(raw.encode()).hexdigest()