from enum import Enum

class Role(Enum):
    DOVE=0
    HAWK=1

class Strategy(Enum):
    SELLER=0,
    BUYER=1,
    STABLE=2


def get_role_from_str(string:str):
    try:
        return Role[string.upper()]
    except KeyError:
        raise ValueError(f"Invalid string with value: {string}, no such role exists")

def get_str_from_role(role:Role):
    if(role == Role.DOVE):
        return "Dove"

    return "Hawk"