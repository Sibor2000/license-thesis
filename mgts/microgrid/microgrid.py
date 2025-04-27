from mgts.simulation.constants import (
    CHARGE_TIME_WINDOW,
    FLOAT_ROUNDING_DECIMALS,
    DEFAULT_SELL_THRESHOLD,
    DEFAULT_BUY_THRESHOLD,
    E_MAX_LINES,
)
from mgts.behavior import Role, Strategy


class Microgrid:
    def __init__(
        self,
        id,
        max_stored_energy=0.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        initial_stored_energy=0.0,
        battery_lifetime_cycles=100,
        stored_energy: list = None,
        stored_energy_post_trade: list = None,
        consumed_energy: list = None,
        produced_energy: list = None,
        sell_threshold=DEFAULT_SELL_THRESHOLD,
        buy_threshold=DEFAULT_BUY_THRESHOLD,
        role: list[Role] = [Role.DOVE],
        battery_operations: list = None,
    ):
        self.id = id

        #! Energy related fields
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        self.max_stored_energy = max_stored_energy
        self.initial_stored_energy = initial_stored_energy
        self.battery_lifetime_cycles = battery_lifetime_cycles
        # each of these fields is an array,
        # that holds the value in the given moment t
        # Since Python shares object across multiple instances of a class, if defined as a default value, inner initialization is used.
        self.stored_energy = stored_energy if stored_energy else []
        self.stored_energy_post_trade = (
            stored_energy_post_trade if stored_energy_post_trade else []
        )
        self.produced_energy = produced_energy if produced_energy else []
        self.consumed_energy = consumed_energy if consumed_energy else []
        # self.production_uncertainty = production_uncertainty
        self.battery_operations = battery_operations if battery_operations else []

        #! Behavior related fields
        self.sell_threshold = sell_threshold
        self.buy_threshold = buy_threshold
        self.role = role

        #! Misc internal fields
        self.E_MAX_LINES = E_MAX_LINES

    def state(self, t):
        return self.produced_energy[t] + self.stored_energy[t] - self.consumed_energy[t]

    def calculate_stored_energy(self, t):
        previous_energy = 0
        if t == 0:
            previous_energy = self.initial_stored_energy
        else:
            previous_energy = self.stored_energy_post_trade[t - 1]

        delta_energy = self.produced_energy[t] - self.consumed_energy[t]
        if delta_energy > 0:  # charge
            next_stored = previous_energy + self.charge_efficiency * delta_energy
            self.stored_energy.append(
                round(min(self.max_stored_energy, next_stored), FLOAT_ROUNDING_DECIMALS)
            )  #!overcharge
            self.battery_operations.append(1)
        elif delta_energy < 0:  # discharge
            next_stored = previous_energy - (1.0 / self.discharge_efficiency) * abs(
                delta_energy
            )
            self.stored_energy.append(
                round(max(0, next_stored), FLOAT_ROUNDING_DECIMALS)
            )  #!undercharge
            self.battery_operations.append(1)
        else:
            self.stored_energy.append(previous_energy)
            self.battery_operations.append(0)

    def is_stable(self, t, post_trade=False):

        if post_trade:
            check_level = 100.0 * self.stored_energy_post_trade[t] / self.max_stored_energy
        else:
            check_level = 100.0 * self.stored_energy[t] / self.max_stored_energy

        if self.buy_threshold <= check_level and check_level <= self.sell_threshold:
            return True

        return False


    def strategy(self, t)->Strategy:
        check_level = 100.0 * self.stored_energy[t] / self.max_stored_energy

        if self.buy_threshold > check_level:
            return Strategy.BUYER
        if self.sell_threshold < check_level:
            return Strategy.SELLER

        return Strategy.STABLE

    # check whether a traded amount stabilises the MG
    def is_energy_stabilising(self, t, sell_buy_amount: tuple[float, float]):
        upper_stability_bound = 1.0 * self.sell_threshold * self.max_stored_energy / 100
        lower_stability_bound = 1.0 * self.buy_threshold * self.max_stored_energy / 100

        new_level = (
            self.stored_energy[t]
            - (1.0 / self.discharge_efficiency) * sell_buy_amount[0]
            + self.charge_efficiency * sell_buy_amount[1]
        )

        if lower_stability_bound <= new_level and new_level <= upper_stability_bound:
            return True

        return False

    def is_valid_thresholds(self):
        return all(
            (
                0 <= self.buy_threshold,  # buy
                self.buy_threshold <= 100,
                0 <= self.sell_threshold,  # sell
                self.sell_threshold <= 100,
                self.buy_threshold <= self.sell_threshold,  # buy and sell
            )
        )

    def timeframe_battery_operations(self, t, p=CHARGE_TIME_WINDOW):
        start = max(0, t - p)
        return sum(self.battery_operations[i] for i in range(start, t + 1))

    def calculate_charge_frequency(self, t):
        return self.timeframe_battery_operations(t) / CHARGE_TIME_WINDOW

    def calculate_battery_percentage(self, t) -> float:
        if len(self.stored_energy) > 0:
            return 1.0 * self.stored_energy[t] / self.max_stored_energy

        # return 1.0*self.initial_stored_energy/self.max_stored_energy

    def calculate_initial_battery_percentage(self):
        return 1.0 * self.initial_stored_energy / self.max_stored_energy

    def calculate_post_trade_battery_percentage(self, t) -> float:
        return 1.0 * self.stored_energy_post_trade[t] / self.max_stored_energy

    def calculate_tradeable_energy(self, t) -> tuple[float, float]:
        battery_percent = (self.stored_energy[t] / self.max_stored_energy) * 100

        # These desires are amounts of electricity that the other party sees, as battery efficiency affects chargin/discharging

        sell_desire_raw = 0
        buy_desire_raw = 0
        sell_desire = 0
        buy_desire = 0

        if self.role[t] == Role.HAWK:
            sell_desire_raw = (
                max(0, battery_percent - self.sell_threshold) / 100
            ) * self.max_stored_energy

            buy_desire_raw = (
                max(0, self.buy_threshold - battery_percent) / 100
            ) * self.max_stored_energy

        elif self.role[t] == Role.DOVE:
            sell_desire_raw = (
                max(0, battery_percent - self.buy_threshold) / 100
            ) * self.max_stored_energy

            buy_desire_raw = (
                max(0, self.sell_threshold - battery_percent) / 100
            ) * self.max_stored_energy

        sell_desire = round(
            sell_desire_raw * self.discharge_efficiency, FLOAT_ROUNDING_DECIMALS
        )
        buy_desire = round(
            buy_desire_raw * (1.0 / self.charge_efficiency), FLOAT_ROUNDING_DECIMALS
        )

        if self.role[t] == Role.DOVE:
            sell_desire = min(sell_desire, 1.0 * self.E_MAX_LINES)
            buy_desire = min(buy_desire, 1.0 * self.E_MAX_LINES)

        return (sell_desire, buy_desire)

    def resolve_trade(self, t, sell_buy_amount):
        self.stored_energy_post_trade.append(
            min(
                self.max_stored_energy,
                max(
                    0,
                    round(
                        self.stored_energy[t]
                        - (1.0 / self.discharge_efficiency) * sell_buy_amount[0]
                        + self.charge_efficiency * sell_buy_amount[1],
                        FLOAT_ROUNDING_DECIMALS,
                    ),
                ),
            )
        )

    def calculate_next_role(self):
        #self.role.append(self.role.append(self.role[0]))

        if self.role[-1]==Role.DOVE:
            self.role.append(Role.HAWK)
        else:
            self.role.append(Role.DOVE)

    def cost_strategy(self, t: int):
        # TODO: change
        if self.role[t] == Role.HAWK:
            return 1.0 * self.role.count(Role.HAWK) / len(self.role)
        return 0
