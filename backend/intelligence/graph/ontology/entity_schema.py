from enum import Enum
import re

class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    ORGANIZATION = "organization"
    ACCOUNT = "account"
    AMOUNT = "amount"  # ❌ NOT NODE, ONLY EDGE PROPERTY


class EntityOntology:

    @staticmethod
    def classify(name: str, source: str = "") -> EntityType:
        name_lower = name.lower()

        # ❌ FILTER: AMOUNT DETECTION
        if re.fullmatch(r"\d{6,}", name):
            return EntityType.AMOUNT

        # ❌ COMPANY PATTERN
        if any(x in name_lower for x in ["pt ", "cv ", "ltd", "inc", "corp"]):
            return EntityType.COMPANY

        # ❌ ACCOUNT / NUMBER
        if name.isdigit():
            return EntityType.ACCOUNT

        # ❌ ORGANIZATION keywords
        if any(x in name_lower for x in ["bank", "agency", "ministry"]):
            return EntityType.ORGANIZATION

        # ❌ DEFAULT PERSON FILTER (STRICT)
        if re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+$", name):
            return EntityType.PERSON

        # fallback safe
        return EntityType.ORGANIZATION