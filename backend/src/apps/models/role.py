from enum import Enum


class Role(str, Enum):
    SUPERUSER = "SUPERUSER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    CLIENT = "CLIENT"
