from mgts.microgrid import MicrogridNetworkFactory
from mgts.behavior import Role
import numpy as np


def test_get_current_moment():
    path = "./datasets/test.xlsx"

    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)
    assert microgrid_network.get_current_moment() == 0
    microgrid_network.step_time()
    assert microgrid_network.get_current_moment() == 1


def test_circumstance_matrix():
    path = "./datasets/test.xlsx"
    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)

    microgrid_network.set_new_universal_thresholds(65, 35)

    microgrid_network.microgrids[0].role = [Role.DOVE]
    microgrid_network.microgrids[1].role = [Role.HAWK]
    microgrid_network.microgrids[2].role = [Role.DOVE]
    microgrid_network.microgrids[3].role = [Role.HAWK]
    microgrid_network.microgrids[4].role = [Role.DOVE]
    microgrid_network.microgrids[5].role = [Role.DOVE]

    microgrid_network.step_time()

    expected_matrix = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [100.0, 100.0, 0.0, 0.0, 75.0, 75.0],
            [100.0, 175.0, 0.0, 0.0, 75.0, 75.0],
            [75.0, 75.0, 0.0, 0.0, 0.0, 0.0],
            [75.0, 75.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )

    assert np.array_equal(expected_matrix, microgrid_network.circumstande_matrices[0])
