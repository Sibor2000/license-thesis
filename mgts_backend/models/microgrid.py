from pydantic import BaseModel

class MicrogridModel(BaseModel):
    id: int
    chargeEfficiency: float
    dischargeEfficiency: float
    initialStored: float
    maxStored:float
    initialRole:str
    production:list[float]
    consumption:list[float]