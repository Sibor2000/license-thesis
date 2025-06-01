from mgts.microgrid import MicrogridFactory
from mgts.behavior import Role
import json

def test_create_from_sheet():
    path = "./datasets/test.xlsx"
    sheet_name = "MG1"

    mgf = MicrogridFactory(path=path)

    microgrid = mgf.create_from_sheet(sheet_name=sheet_name)

    assert microgrid.consumed_energy == [0, 5, 15, 15, 15, 15, 15, 15, 15]
    assert microgrid.produced_energy == [0, 10, 15, 20, 25, 25, 25, 25, 25]

    sheet_name = "MG2"

    microgrid = mgf.create_from_sheet(sheet_name=sheet_name)

    assert microgrid.consumed_energy == [0, 5, 15, 15, 15, 15, 8, 7, 6]
    assert microgrid.produced_energy == [0, 10, 15, 20, 25, 25, 20, 20, 20]


def test_create_from_file():
    path = "./datasets/test.xlsx"

    mgf = MicrogridFactory(path=path)

    microgrids = mgf.create_from_file()

    assert len(microgrids) == 6
    assert microgrids[0].id == "MG1"
    assert microgrids[0].charge_efficiency == 0.8
    assert microgrids[0].initial_stored_energy == 0
    assert microgrids[0].battery_lifetime_cycles == 15

    assert microgrids[1].consumed_energy == [0, 5, 15, 15, 15, 15, 8, 7, 6]
    assert microgrids[1].produced_energy == [0, 10, 15, 20, 25, 25, 20, 20, 20]
    assert microgrids[1].initial_stored_energy == 0
    assert microgrids[1].battery_lifetime_cycles == 20

def test_create_from_dict():
    path = "./datasets/test/one_scenario.json"

    with open(path, 'r') as f:
        data = json.load(f)

    microgrids = MicrogridFactory.create_from_dict(data)

    assert len(microgrids) == data["nrOfMicrogrids"]
    assert microgrids[2].produced_energy == [1,2,3,4,5]
    assert microgrids[2].consumed_energy == [9,8,7,6,5]
    assert microgrids[0].role[0] == Role.DOVE
    assert microgrids[3].role[0] == Role.HAWK
