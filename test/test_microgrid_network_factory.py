from mgts.microgrid import MicrogridNetworkFactory

def test_create_from_file():
    path = "./datasets/test.xlsx"

    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)
    microgrids = microgrid_network.microgrids

    assert len(microgrids) == 3
    assert microgrids[0].id == "MG1"
    assert microgrids[0].charge_efficiency == 0.8
    assert microgrids[0].initial_stored_energy == 0

    assert microgrids[1].consumed_energy==[0, 5, 15, 15, 15, 15, 8, 7, 6]
    assert microgrids[1].produced_energy==[0, 10, 15, 20, 25, 25, 20, 20, 20]
    assert microgrids[1].initial_stored_energy == 5