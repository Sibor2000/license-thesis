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
from mgts.exceptions import EndOfSimulationException
import matplotlib.pyplot as plt


app = FastAPI()

simulations:dict[str, MicrogridNetwork] = {}
simulation_charts:dict[str, dict] = {}
#simulation_charts["momentChartsList"] = []
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
    data = sim.model_dump()

    filtered_data = {k: v for k, v in data.items() if k != "id"}
    sim_model = SimulationModel(**filtered_data)
    id = data["id"]

    mgn = MicrogridNetworkFactory.create_from_dict(filtered_data)

    simulations[id] = mgn
    simulation_charts[id] = {}
    simulation_charts[id]["momentChartsList"] = []

    # print(filtered_data["microgrids"][0]['chargeEfficiency'])

    return mgn

async def step_time_and_send_charts(sim_id:str):
    mgn:MicrogridNetwork = simulations[sim_id]
    ws:WebSocket = active_websockets[sim_id]

    try:
        mgn.step_time()
    except EndOfSimulationException:
        await ws.send_json({
            "type":"text",
            "payload":"End of simulation has been reached"
            })
        return

    #Sim charts
    fig_energy_delta, axes_energy_delta = plt.subplots(1, 2)
    fig_role_strat_progress, axes_role_strat_progress = plt.subplots()
    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes_energy_delta[0], axs_after=axes_energy_delta[1])
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axes_role_strat_progress)
    chart_en_delta_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_energy_delta)
    chart_ro_st_ot_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_role_strat_progress)

    #Moment charts
    fig_role_strat, axes_role_strat = plt.subplots()
    fig_glob_best_fit, axes_glob_best_fit = plt.subplots()
    fig_diversity, axes_diversity = plt.subplots()
    fig_exp_vs_exp, axes_exp_vs_exp = plt.subplots()
    fig_runtime, axes_runtime = plt.subplots()
    MicrogridNetworkCharts.chart_role_and_strategy(mgn, axes_role_strat)
    MicrogridNetworkCharts.chart_global_best_fitness(mgn, axes_glob_best_fit)
    MicrogridNetworkCharts.chart_diveristy(mgn, axes_diversity)
    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn, axes_exp_vs_exp)
    MicrogridNetworkCharts.chart_runtime(mgn, axes_runtime)
    chart_ro_st_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_role_strat)
    chart_glob_bf_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_glob_best_fit)
    chart_div_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_diversity)
    chart_ex_v_ex_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_exp_vs_exp)
    chart_runtime_b64 = MicrogridNetworkCharts.generate_img_from_fig(fig_runtime)

    simulation_charts[sim_id]["simulationCharts"]=[chart_en_delta_b64, chart_ro_st_b64]
    simulation_charts[sim_id]["momentChartsList"].append([
        chart_ro_st_b64,
        chart_glob_bf_b64,
        chart_div_b64,
        chart_ex_v_ex_b64,
        chart_runtime_b64
    ])

    await ws.send_json({
        "type":"charts",
        "simCharts":[
            chart_en_delta_b64,
            chart_ro_st_ot_b64
        ],
        "momentCharts":[
            chart_ro_st_b64,
            chart_glob_bf_b64,
            chart_div_b64,
            chart_ex_v_ex_b64,
            chart_runtime_b64
        ]
    })

@app.post("/simulation/{sim_id}/step")
async def step_simulation_time(sim_id: str):
    mgn = simulations[sim_id]
    ws = active_websockets[sim_id]

    asyncio.create_task(step_time_and_send_charts(sim_id))

    return {"message":"OK"}

@app.post("/simulation/{sim_id}/reset")
def reset_sim(sim_id: str):
    mgn = simulations[sim_id]

    mgn.reset()

    simulation_charts[sim_id] = {}
    simulation_charts[sim_id]["momentChartsList"] = []

@app.get("/simulation/{sim_id}/charts")
def send_simulation_charts(sim_id: str):
    if sim_id in simulation_charts:
        return simulation_charts[sim_id]
    return {}

@app.get("/simulation/{sim_id}/params/json")
def send_simulation_params(sim_id:str):
    if sim_id in simulations:
        return simulations[sim_id].to_scenario_dict()

    return None

@app.get('/active_simulation_ids')
def active_simulation_ids():
    return list(simulations.keys())