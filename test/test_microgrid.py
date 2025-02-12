from mgts.microgrid import Microgrid
from mgts.simulation.constants import CHARGE_TIME_WINDOW

def test_frequency():
    micro = Microgrid(1, battery_operations=range(1, 2*CHARGE_TIME_WINDOW+2))
    expected_value = ((CHARGE_TIME_WINDOW/2)*(1 + CHARGE_TIME_WINDOW))/CHARGE_TIME_WINDOW
    assert micro.calculate_charge_frequency(CHARGE_TIME_WINDOW - 1)==expected_value

def test_thresholds():
    #base case 1: regular thresholds
    micro = Microgrid(1, buy_threshold=10, soft_buy_threshold=20, sell_threshold=80, soft_sell_threshold=70)
    assert micro.is_valid_thresholds()

    #base case 2: all thresholds equal
    micro = Microgrid(1, buy_threshold=50, soft_buy_threshold=50, sell_threshold=50, soft_sell_threshold=50)
    assert micro.is_valid_thresholds()

    #base case 3: regular thresholds, but soft thresholds are overlapping
    micro = Microgrid(1, buy_threshold=10, soft_buy_threshold=70, sell_threshold=80, soft_sell_threshold=20)
    assert micro.is_valid_thresholds()

    #invalid case 1: sell and buy have invalid values
    micro = Microgrid(1, buy_threshold=-1, soft_buy_threshold=70, sell_threshold=101, soft_sell_threshold=20)
    assert not(micro.is_valid_thresholds())

    #invalid case 2: soft thresholds have wrong values
    micro = Microgrid(1, buy_threshold=10, soft_buy_threshold=5, sell_threshold=80, soft_sell_threshold=85)
    assert not(micro.is_valid_thresholds())
