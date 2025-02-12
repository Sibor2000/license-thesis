from mgts.simulation.constants import CHARGE_TIME_WINDOW

class Microgrid:
    def __init__(self, id, max_stored_energy=0.0,charge_efficiency=1.0, discharge_efficiency=1.0, stored_energy=[], consumed_energy=[], produced_energy=[], sell_threshold=100.0, soft_sell_threshold=100.0, buy_threshold=0.0, soft_buy_threshold=0.0, battery_operations=[]):
        self.id=id

        #! Energy related fields
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        self.max_stored_energy = max_stored_energy
        #each of these fields is an array,
        #that holds the value in the given moment t
        self.stored_energy = stored_energy
        self.produced_energy = produced_energy
        self.consumed_energy = consumed_energy
        #self.production_uncertainty = production_uncertainty
        self.battery_operations = battery_operations

        #! Behavior related fields
        self.sell_threshold = sell_threshold
        self.soft_sell_threshold = soft_sell_threshold
        self.buy_threshold = buy_threshold
        self.soft_buy_threshold = soft_buy_threshold


    def state(self, t):
        return self.produced_energy[t] + self.stored_energy[t] - self.consumed_energy[t]

    def calculate_stored_energy(self, t):
        delta_energy = self.produced_energy[t] - self.consumed_energy[t]
        if delta_energy > 0:    #charge
            next_stored = self.stored_energy[t-1] + self.charge_efficiency * delta_energy
            self.stored_energy[t] = min(self.max_stored_energy, next_stored)    #!overcharge
        elif delta_energy < 0:  #discharge
            next_stored = self.stored_energy[t-1] - (1/self.discharge_efficiency) * abs(delta_energy)
            self.stored_energy[t] = max(0, next_stored)     #!undercharge
        else:
            self.stored_energy[t] = self.stored_energy[t-1]

    def is_stable(self, t):
        return self.produced_energy[t] - self.consumed_energy[t] + self.stored_energy[t] >= 0

    def is_valid_thresholds(self):
        return all((
            0 <= self.buy_threshold,    #buy
            self.buy_threshold <= 100,
            0 <= self.sell_threshold,   #sell
            self.sell_threshold <= 100,
            self.buy_threshold <= self.sell_threshold,  #buy and sell
            self.buy_threshold <= self.soft_buy_threshold,  #soft buy
            self.soft_buy_threshold <= self.sell_threshold,
            self.buy_threshold <= self.soft_sell_threshold, #soft sell
            self.soft_sell_threshold <= self.sell_threshold
            ))

    def calculate_charge_frequency(self,t):
        start = max(0, t - CHARGE_TIME_WINDOW)
        return sum(self.battery_operations[i] for i in range(start, t+1))/CHARGE_TIME_WINDOW