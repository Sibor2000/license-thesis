from mgts.microgrid import MicrogridNetworkFactory


def test_get_current_moment():
    path = "./datasets/test.xlsx"

    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)
    assert microgrid_network.get_current_moment() == 0
    microgrid_network.step_time()
    assert microgrid_network.get_current_moment() == 1