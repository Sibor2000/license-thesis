from pydantic import BaseModel
from .simulation import SimulationModel

class SimulationRequest(SimulationModel):
    id: str