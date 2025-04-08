from enum import Enum

class Role(Enum):
    DOVE=0
    HAWK=1

class Strategy(Enum):
    SELLER=0,
    BUYER=1,
    STABLE=2