from mgts.simulation.constants import CHARGE_TIME_WINDOW


class Microgrid:
    def __init__(
        self,
        id,
        max_stored_energy=0.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        initial_stored_energy=0.0,
        stored_energy: list = None,
        stored_energy_post_trade: list = None,
        consumed_energy: list = None,
        produced_energy: list = None,
        sell_threshold=50.0,
        soft_sell_threshold=15.0,
        buy_threshold=5.0,
        soft_buy_threshold=25.0,
        battery_operations: list = None,
    ):
        self.id = id

        #! Energy related fields
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        self.max_stored_energy = max_stored_energy
        self.initial_stored_energy = initial_stored_energy
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
        self.soft_sell_threshold = soft_sell_threshold
        self.soft_buy_threshold = soft_buy_threshold
        self.buy_threshold = buy_threshold

    def state(self, t):
        return self.produced_energy[t] + self.stored_energy[t] - self.consumed_energy[t]

    def calculate_stored_energy(self, t):
        previous_energy = 0
        if t == 0:
            previous_energy = self.initial_stored_energy
        else:
            # previous_energy = self.stored_energy[t-1]
            previous_energy = self.stored_energy_post_trade[t - 1]

        delta_energy = self.produced_energy[t] - self.consumed_energy[t]
        if delta_energy > 0:  # charge
            next_stored = previous_energy + self.charge_efficiency * delta_energy
            self.stored_energy.append(
                min(self.max_stored_energy, next_stored)
            )  #!overcharge
        elif delta_energy < 0:  # discharge
            next_stored = previous_energy - (1 / self.discharge_efficiency) * abs(
                delta_energy
            )
            self.stored_energy.append(max(0, next_stored))  #!undercharge
        else:
            self.stored_energy.append(previous_energy)

    def is_stable(self, t):
        return (
            self.produced_energy[t] - self.consumed_energy[t] + self.stored_energy[t]
            >= 0
        )

    def is_valid_thresholds(self):
        return all(
            (
                0 <= self.buy_threshold,  # buy
                self.buy_threshold <= 100,
                0 <= self.sell_threshold,  # sell
                self.sell_threshold <= 100,
                self.buy_threshold <= self.sell_threshold,  # buy and sell
                self.buy_threshold <= self.soft_buy_threshold,  # soft buy
                self.soft_buy_threshold <= self.sell_threshold,
                self.buy_threshold <= self.soft_sell_threshold,  # soft sell
                self.soft_sell_threshold <= self.sell_threshold,
            )
        )

    def calculate_charge_frequency(self, t):
        start = max(0, t - CHARGE_TIME_WINDOW)
        return (
            sum(self.battery_operations[i] for i in range(start, t + 1))
            / CHARGE_TIME_WINDOW
        )

    def calculate_tradeable_energy(self, t):
        battery_percent = (self.stored_energy[t] / self.max_stored_energy) * 100

        # These desires are amounts of electricity that the other party sees, as battery efficiency affects chargin/discharging
        sell_desire_raw = (
            max(0, battery_percent - self.sell_threshold) / 100
        ) * self.max_stored_energy
        soft_sell_desire_raw = (
            max(0, battery_percent - sell_desire_raw - self.soft_sell_threshold) / 100
        ) * self.max_stored_energy

        buy_desire_raw = (
            max(0, self.buy_threshold - battery_percent) / 100
        ) * self.max_stored_energy
        soft_buy_desire_raw = (
            max(0, self.soft_buy_threshold + buy_desire_raw - battery_percent) / 100
        ) * self.max_stored_energy

        sell_desire = sell_desire_raw * self.discharge_efficiency
        soft_sell_desire = soft_sell_desire_raw * self.discharge_efficiency
        buy_desire = buy_desire_raw * (1.0 / self.charge_efficiency)
        soft_buy_desire = soft_buy_desire_raw * (1.0 / self.charge_efficiency)

        return (sell_desire, soft_sell_desire, soft_buy_desire, buy_desire)

    def energy_transact(self, amount, t):

        new_amount = self.stored_energy[t]

        if amount > 0:
            new_amount += amount * self.charge_efficiency
        elif amount < 0:
            new_amount += amount * (1 / self.discharge_efficiency)

        self.stored_energy_post_trade.append(new_amount)
