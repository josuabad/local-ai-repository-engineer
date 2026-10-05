from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RepositoryContext:
    root_path: Path

    files: list[str] = field(default_factory=list)
    directories: list[str] = field(default_factory=list)
    languages: dict[str, int] = field(default_factory=dict)
    test_files: list[str] = field(default_factory=list)
