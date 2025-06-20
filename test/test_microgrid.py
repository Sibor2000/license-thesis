from mgts.microgrid import Microgrid
from mgts.simulation.constants import CHARGE_TIME_WINDOW
from mgts.behavior import Role


def test_frequency():
    micro = Microgrid(1, battery_operations=list(range(1, 2 * CHARGE_TIME_WINDOW + 2)))
    expected_value = (
        (CHARGE_TIME_WINDOW / 2) * (1 + CHARGE_TIME_WINDOW)
    ) / CHARGE_TIME_WINDOW
    assert micro.calculate_charge_frequency(CHARGE_TIME_WINDOW - 1) == expected_value


def test_thresholds():
    # base case 1: regular thresholds
    micro = Microgrid(1, buy_threshold=10, sell_threshold=80)
    assert micro.is_valid_thresholds()

    # base case 2: all thresholds equal
    micro = Microgrid(1, buy_threshold=50, sell_threshold=50)
    assert micro.is_valid_thresholds()

    # invalid case 1: sell and buy have invalid values
    micro = Microgrid(1, buy_threshold=-1, sell_threshold=101)
    assert not (micro.is_valid_thresholds())

    # invalid case 2: thresholds are swapped
    micro = Microgrid(1, buy_threshold=80, sell_threshold=10)
    assert not (micro.is_valid_thresholds())


def test_strategy_cost():
    micro = Microgrid(
        1, role=[Role.DOVE] * 6 + [Role.HAWK] * 4 + [Role.DOVE] * 6 + [Role.HAWK] * 4
    )

    assert micro.cost_strategy(19) == 0.4


def test_is_stable():
    microgrid = Microgrid(
        1,
        stored_energy=[50],
        max_stored_energy=100,
        sell_threshold=66,
        buy_threshold=33,
    )
    assert microgrid.is_stable(t=0)
    microgrid.stored_energy = [67]
    assert not (microgrid.is_stable(t=0))
    microgrid.stored_energy = [30]
    assert not (microgrid.is_stable(t=0))
    microgrid.sell_threshold = 33
    microgrid.buy_threshold = 28
    assert microgrid.is_stable(t=0)


def test_is_energy_stabilising():
    microgrid = Microgrid(
        1,
        stored_energy=[20],
        max_stored_energy=100,
        sell_threshold=66,
        buy_threshold=33,
    )
    assert not (microgrid.is_stable(t=0))
    assert not (microgrid.is_energy_stabilising(t=0, sell_buy_amount=(20, 0)))
    assert not (microgrid.is_energy_stabilising(t=0, sell_buy_amount=(0, 50)))
    assert microgrid.is_energy_stabilising(t=0, sell_buy_amount=(0, 30))

    microgrid.charge_efficiency = 0.2

    assert not (microgrid.is_stable(t=0))
    assert not (microgrid.is_energy_stabilising(t=0, sell_buy_amount=(0, 50 * (1.0/0.2))))
    assert microgrid.is_energy_stabilising(t=0, sell_buy_amount=(0, 20 * (1.0 / 0.2)))

    microgrid.discharge_efficiency = 0.2
    microgrid.stored_energy = [70]

    assert not (microgrid.is_stable(t=0))
    assert not (microgrid.is_energy_stabilising(t=0, sell_buy_amount=(50 * 0.2, 0)))
    assert microgrid.is_energy_stabilising(t=0, sell_buy_amount=(20 * 0.2, 0))


def test_dove_chance():
    microgrid = Microgrid(
        1,
        stored_energy_post_trade=[0],
        max_stored_energy=100,
        sell_threshold=66,
        buy_threshold=33,
    )
    assert microgrid.calculate_dove_chance(t=0) == 0.0

    microgrid.stored_energy_post_trade = [25]
    assert microgrid.calculate_dove_chance(t=0) > 0.0
    assert microgrid.calculate_dove_chance(t=0) < 1.0

    microgrid.stored_energy_post_trade = [50]
    assert microgrid.calculate_dove_chance(t=0) == 1.0

    microgrid.stored_energy_post_trade = [75]
    assert microgrid.calculate_dove_chance(t=0) > 0.0
    assert microgrid.calculate_dove_chance(t=0) < 1.0

    microgrid.stored_energy_post_trade = [100]
    assert microgrid.calculate_dove_chance(t=0) == 0.0

    microgrid.stored_energy_post_trade = [16.5]
    assert microgrid.calculate_dove_chance(t=0) == 0.5

