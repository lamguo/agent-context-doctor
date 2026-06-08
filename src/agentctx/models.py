from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Problem:
    level: str
    code: str
    message: str
    file: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    root: str
    repository: str
    score: int
    rating: str
    files: Dict[str, bool]
    commands: Dict[str, List[str]]
    problems: List[Problem] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "repository": self.repository,
            "score": self.score,
            "rating": self.rating,
            "files": self.files,
            "commands": self.commands,
            "problems": [problem.to_dict() for problem in self.problems],
            "suggestions": self.suggestions,
        }


@dataclass
class HandoffData:
    repository: str
    branch: str
    recent_commits: List[str]
    modified_files: List[str]
    untracked_files: List[str]
    detected_commands: Dict[str, List[str]]
    next_steps: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
