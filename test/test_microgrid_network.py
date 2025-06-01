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
