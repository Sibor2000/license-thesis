from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import base64
from models.simulation import SimulationModel
from models.simulation_request import SimulationRequest
from mgts.microgrid import Microgrid, MicrogridNetwork
from mgts.behavior.behavior import Role
import random
from mgts.charting.mgn_charts import MicrogridNetworkCharts
from mgts.microgrid import MicrogridNetworkFactory
import matplotlib.pyplot as plt


app = FastAPI()

simulations = {}
active_websockets: dict[str, WebSocket] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_img_b64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


@app.websocket("/ws/simulation/{sim_id}")
async def ws_endpoint(websocket: WebSocket, sim_id: str):
    await websocket.accept()

    active_websockets[sim_id] = websocket

    # await websocket.send_text(f"Connected {sim_id} to sim!")

    await websocket.send_json({"type": "msg", "text": f"Connected {sim_id} to sim!"})

    try:
        # await websocket.receive_text()
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        active_websockets.pop(sim_id, None)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/example_scenario/{scenario_id}")
def example_scenario(scenario_id: str):
    with open("./assets/small_scenarios.json") as f:
        scenarios = json.load(f)

    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario

    raise HTTPException(status_code=404, detail="Scenario not found")


@app.get("/example_scenario_ids")
def example_scenario_ids():
    with open("./assets/small_scenarios.json") as f:
        scenarios = json.load(f)

    ids = list(map(lambda x: x["id"], scenarios))
    return ids


@app.post("/create_simulation")
def create_simulation(sim: SimulationRequest):

    # sim_model = SimulationModel(**sim.model_copy(exclude={'id'}))

    data = sim.model_dump()
    filtered_data = {k: v for k, v in data.items() if k != "id"}
    sim_model = SimulationModel(**filtered_data)
    id = data["id"]

    mgn = MicrogridNetworkFactory.create_from_dict(filtered_data)

    simulations[id] = mgn

    # print(filtered_data["microgrids"][0]['chargeEfficiency'])

    return mgn


###
# Testing stuff


async def step_time_and_send_charts(ws: WebSocket, mgn: MicrogridNetwork):
    mgn.step_time()

    fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(
        mgn, axs_before=axes[0][0], axs_after=axes[0][1]
    )
    img_b64 = MicrogridNetworkCharts.generate_img_from_axs(axes[0][0])

    await ws.send_json({"type": "chart", "data": img_b64})

@app.get("/test_ws/{sim_id}")
async def test_ws(sim_id: str):
    ws = active_websockets[sim_id]

    # await ws.send_text("Booha")

    mgs = []

    sell_threshold = 55
    buy_threshold = 45

    dove_count = 80
    hawk_count = 40

    for i in range(0, dove_count):
        mgs.append(
            Microgrid(
                id=i,
                max_stored_energy=100,
                initial_stored_energy=random.uniform(0, 100),
                sell_threshold=sell_threshold,
                buy_threshold=buy_threshold,
                role=[Role.DOVE],
                produced_energy=[0] * 100,
                consumed_energy=[0] * 100,
            )
        )

    print("Doves ready")

    for i in range(dove_count, dove_count + hawk_count):
        mgs.append(
            Microgrid(
                id=i,
                max_stored_energy=100,
                initial_stored_energy=random.uniform(0, 100),
                sell_threshold=sell_threshold,
                buy_threshold=buy_threshold,
                role=[Role.HAWK],
                produced_energy=[0] * 100,
                consumed_energy=[0] * 100,
            )
        )

    print("Hawks ready")

    mgn = MicrogridNetwork(microgrids=mgs)

    asyncio.create_task(step_time_and_send_charts(ws, mgn))


@app.post("/simulation/{sim_id}/step")
async def step_simulation_time(sim_id: str):
    mgn = simulations[sim_id]
    ws = active_websockets[sim_id]

    asyncio.create_task(step_time_and_send_charts(ws, mgn))

    return {"message":"OK"}
