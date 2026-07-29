from dataclasses import dataclass

@dataclass(frozen=True)
class IRVersion:
    schema: str
    builder: str

CURRENT_VERSION = IRVersion(
    schema="3.1-candidate",
    builder="1.0.0"
)

DEFAULT_HASH_ALGORITHM = "sha256"