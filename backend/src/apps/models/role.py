from __future__ import annotations

from enum import Enum, IntEnum


class RolePriority(IntEnum):
    SUPERUSER = 1
    ADMIN = 2
    MANAGER = 3
    USER = 4
    CLIENT = 5


class Role(str, Enum):
    SUPERUSER = "SUPERUSER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    CLIENT = "CLIENT"

    @property
    def priority(self) -> int:
        return RolePriority[self.name].value

    def can_access(self, required_role: "Role") -> bool:
        return self.priority <= required_role.priority
