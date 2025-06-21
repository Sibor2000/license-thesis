from pydantic import BaseModel

class GAParamsModel(BaseModel):
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