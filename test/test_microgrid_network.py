from mgts.microgrid import MicrogridNetworkFactory


def test_get_current_moment():
    path = "./datasets/test.xlsx"

    microgrid_network = MicrogridNetworkFactory.create_from_file(path=path)
    assert microgrid_network.get_current_moment() == 0
    microgrid_network.step_time()
    assert microgrid_network.get_current_moment() == 1


def test_trade_one_to_one():
    path = "./datasets/test.xlsx"

    mgn = MicrogridNetworkFactory.create_from_file(path=path)

    mgn.microgrids[0].charge_efficiency = 0.8
    mgn.microgrids[2].discharge_efficiency = 0.5

    mgn.microgrids[0].buy_threshold = 100.0
    mgn.microgrids[0].soft_buy_threshold = 100.0
    mgn.microgrids[0].soft_sell_threshold = 100.0
    mgn.microgrids[0].sell_threshold = 100.0

    mgn.microgrids[2].buy_threshold = 0.0
    mgn.microgrids[2].soft_buy_threshold = 0.0
    mgn.microgrids[2].soft_sell_threshold = 0.0
    mgn.microgrids[2].sell_threshold = 0.0

    mgn.step_time()

    assert mgn.microgrids[0].stored_energy_post_trade[0] == 80 * 0.8 * 0.5
    assert mgn.microgrids[2].stored_energy_post_trade[0] == 0

def test_trade_soft_sell_activation_uncovered_demand():
    path = "./datasets/test.xlsx"

    mgn = MicrogridNetworkFactory.create_from_file(path=path)

    mgn.microgrids[0].charge_efficiency = 1
    mgn.microgrids[1].discharge_efficiency = 0.4
    mgn.microgrids[2].discharge_efficiency = 1

    mgn.microgrids[0].initial_stored_energy = 0
    mgn.microgrids[1].initial_stored_energy = 100
    mgn.microgrids[2].initial_stored_energy = 100

    mgn.microgrids[0].buy_threshold = 100.0
    mgn.microgrids[0].soft_buy_threshold = 100.0
    mgn.microgrids[0].soft_sell_threshold = 100.0
    mgn.microgrids[0].sell_threshold = 100.0

    mgn.microgrids[1].buy_threshold = 0.0
    mgn.microgrids[1].soft_buy_threshold = 0.0
    mgn.microgrids[1].soft_sell_threshold = 0.0
    mgn.microgrids[1].sell_threshold = 100.0

    mgn.microgrids[2].buy_threshold = 0.0
    mgn.microgrids[2].soft_buy_threshold = 0.0
    mgn.microgrids[2].soft_sell_threshold = 0.0
    mgn.microgrids[2].sell_threshold = 0.0

    mgn.step_time()

    assert mgn.microgrids[0].stored_energy_post_trade[0] == 100 * 0.4 + 100
    assert mgn.microgrids[1].stored_energy_post_trade[0] == 0
    assert mgn.microgrids[2].stored_energy_post_trade[0] == 0

def test_trade_soft_sell_activation_covered_demand():
    path = "./datasets/test.xlsx"

    mgn = MicrogridNetworkFactory.create_from_file(path=path)

    mgn.microgrids[0].charge_efficiency = 1
    mgn.microgrids[1].discharge_efficiency = 1
    mgn.microgrids[2].discharge_efficiency = 1

    mgn.microgrids[0].initial_stored_energy = 350
    mgn.microgrids[1].initial_stored_energy = 100
    mgn.microgrids[2].initial_stored_energy = 100

    mgn.microgrids[0].buy_threshold = 100.0
    mgn.microgrids[0].soft_buy_threshold = 100.0
    mgn.microgrids[0].soft_sell_threshold = 100.0
    mgn.microgrids[0].sell_threshold = 100.0

    mgn.microgrids[1].buy_threshold = 0.0
    mgn.microgrids[1].soft_buy_threshold = 0.0
    mgn.microgrids[1].soft_sell_threshold = 0.0
    mgn.microgrids[1].sell_threshold = 100.0

    mgn.microgrids[2].buy_threshold = 0.0
    mgn.microgrids[2].soft_buy_threshold = 0.0
    mgn.microgrids[2].soft_sell_threshold = 0.0
    mgn.microgrids[2].sell_threshold = 0.0

    mgn.step_time()

    assert mgn.microgrids[0].stored_energy_post_trade[0] == mgn.microgrids[0].max_stored_energy #500 = 350 + 100 + 50
    assert mgn.microgrids[1].stored_energy_post_trade[0] == 100 - 50
    assert mgn.microgrids[2].stored_energy_post_trade[0] == 0



def test_trade_soft_sell_activation_covered_demand_split_soft_sell():
    path = "./datasets/test.xlsx"

    mgn = MicrogridNetworkFactory.create_from_file(path=path)

    mgn.microgrids[0].charge_efficiency = 1
    mgn.microgrids[1].discharge_efficiency = 1
    mgn.microgrids[2].discharge_efficiency = 1
    mgn.microgrids[3].discharge_efficiency = 1

    mgn.microgrids[0].initial_stored_energy = 350
    mgn.microgrids[1].initial_stored_energy = 100
    mgn.microgrids[2].initial_stored_energy = 100
    mgn.microgrids[3].initial_stored_energy = 100

    mgn.microgrids[0].buy_threshold = 100.0
    mgn.microgrids[0].soft_buy_threshold = 100.0
    mgn.microgrids[0].soft_sell_threshold = 100.0
    mgn.microgrids[0].sell_threshold = 100.0

    mgn.microgrids[1].buy_threshold = 0.0
    mgn.microgrids[1].soft_buy_threshold = 0.0
    mgn.microgrids[1].soft_sell_threshold = 0.0
    mgn.microgrids[1].sell_threshold = 0.0

    mgn.microgrids[2].buy_threshold = 0.0
    mgn.microgrids[2].soft_buy_threshold = 0.0
    mgn.microgrids[2].soft_sell_threshold = 0.0
    mgn.microgrids[2].sell_threshold = 100.0

    mgn.microgrids[3].buy_threshold = 0.0
    mgn.microgrids[3].soft_buy_threshold = 0.0
    mgn.microgrids[3].soft_sell_threshold = 0.0
    mgn.microgrids[3].sell_threshold = 100.0

    mgn.step_time()

    assert mgn.microgrids[0].stored_energy_post_trade[0] == mgn.microgrids[0].max_stored_energy #500 = 350 + 100 + 50
    assert mgn.microgrids[1].stored_energy_post_trade[0] == 0
    assert mgn.microgrids[2].stored_energy_post_trade[0] == 100 - (500 - 350 - 100)/2
    assert mgn.microgrids[3].stored_energy_post_trade[0] == 100 - (500 - 350 - 100)/2