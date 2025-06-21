from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GAParams:
    id: str
    pop_size: int
    pc: float
    pm: float
    sel: str
    cros: str
    mp: bool
    mut: str
    ss: bool
    ep: int


class GAParamsFactory:
    @staticmethod
    def create_from_dict(simulation_dict: dict) -> Optional[List[GAParams]]:
        ga_params_list = simulation_dict.get("gaParams")
        if not ga_params_list:
            return None

        return [GAParams(**param) for param in ga_params_list]