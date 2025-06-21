from pydantic import BaseModel, Field
from .microgrid import MicrogridModel
from .ga_params import GAParamsModel

class SimulationModel(BaseModel):
    sellThreshold: float = Field(..., ge=0, le=100)
    buyThreshold: float = Field(..., ge=0, le=100)
    simulationDuration: int = Field(..., ge=1)
    nrOfMicrogrids: int
    eMax: float
    microgrids: list[MicrogridModel]
    gaParams: list[GAParamsModel]