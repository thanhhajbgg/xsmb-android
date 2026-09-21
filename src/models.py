
from dataclasses import dataclass
@dataclass(frozen=True)
class Draw:
    day: str
    numbers: tuple[str, ...]
    special_prize: str
    source_url: str = ""
