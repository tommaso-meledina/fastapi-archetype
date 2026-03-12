from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Role(StrEnum):
    ADMIN = "admin"
    WRITER = "writer"
    READER = "reader"


@dataclass(frozen=True, kw_only=True)
class Principal:
    subject: str
    user_id: str
    name: str | None = None
    scope: str | None = None
    app_id: str | None = None
    roles: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    claims: dict[str, Any] = field(default_factory=dict)
