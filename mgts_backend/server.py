from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hello":"World"}

@app.get('/example_scenario/{scenario_id}')
def example_scenario(scenario_id:str):
    with open("./assets/small_scenarios.json") as f:
        scenarios = json.load(f)

    for scenario in scenarios:
        if scenario["id"]==scenario_id:
            return scenario


    raise HTTPException(status_code=404, detail="Scenario not found")

@app.get('/example_scenario_ids')
def example_scenario_ids():
    with open("./assets/small_scenarios.json") as f:
        scenarios = json.load(f)

    ids = list(map(lambda x: x["id"],scenarios))
    return ids