from pydantic import BaseModel
from .microgrid import MicrogridModel
from .ga_params import GAParamsModel

class SimulationModel(BaseModel):
    sellThreshold: float
    buyThreshold: float
    simulationDuration: int
    nrOfMicrogrids: int
    eMax: float
    microgrids: list[MicrogridModel]
    gaParams: list[GAParamsModel]