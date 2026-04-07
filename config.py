from dataclasses import dataclass, field

@dataclass
class ParserConfig:
    min_time: int
    max_time: int
    max_request_attempts: int

    custom_headers: dict[str, str|int|bool|list] = field(default_factory=dict[str, str])
    cat_subreddits: list[str] = field(
            default_factory=(lambda: ["cats", "blackcats", "OneOrangeBraincell", "danglers", "Catswithjobs", "airplaneears", "IllegallySmolCats", "catsareliquid", "Blep"])
    )
