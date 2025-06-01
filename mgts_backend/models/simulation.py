from pydantic import BaseModel
from .microgrid import MicrogridModel

class SimulationModel(BaseModel):
    sellThreshold: float
    buyThreshold: float
    simulationDuration: int
    nrOfMicrogrids: int
    eMax: float
    microgrids: list[MicrogridModel]