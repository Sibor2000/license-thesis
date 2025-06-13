from mgts.microgrid import MicrogridNetworkFactory
from mgts.behavior import Role
import numpy as np


def test_get_current_moment():
    path = "./datasets/test.xlsx"

    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)
    assert microgrid_network.get_current_moment() == 0
    # partial step time
    microgrid_network.conduct_internal_energy()
    microgrid_network.update_current_moment()
    assert microgrid_network.get_current_moment() == 1

def test_mng_reset():
    path = "./datasets/test.xlsx"

    mgn = MicrogridNetworkFactory.create_from_file(path=path)
    mgn.get_current_moment() == 0
    mgn.step_time()
    mgn.get_current_moment() == 1
    mgn.reset()
    mgn.get_current_moment() == 0
