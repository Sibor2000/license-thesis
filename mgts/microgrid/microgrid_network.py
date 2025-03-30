from mgts.microgrid import Microgrid
from mgts.microgrid import Trade
from mealpy.evolutionary_based import GA
from mealpy.utils.problem import Problem
from mealpy import FloatVar
import numpy as np
from mgts.simulation.ga_constants import (
    GA_EPOCH,
    GA_POP_SIZE,
    GA_CROSSOVER,
    GA_MUTATION,
)
from mgts.simulation.constants import E_MAX_LINES


class MicrogridNetwork:
    def __init__(self, microgrids: list[Microgrid] = None):
        self.microgrids = microgrids if microgrids else []
        self.__time = 0

        self.circumstance_arrays: list[list[Trade]] = []
        self.desires = []
        self.decision_arrays = []

        self.E_MAX_LINES = E_MAX_LINES

    def update_current_moment(self):
        self.__time = len(self.microgrids[0].stored_energy)

    def get_current_moment(self):
        return self.__time

    def conduct_internal_energy(self):
        for microgrid in self.microgrids:
            microgrid.calculate_stored_energy(self.__time)

    def set_new_universal_thresholds(self, sell_threshold, buy_threshold):
        for microgrid in self.microgrids:
            microgrid.sell_threshold = sell_threshold
            microgrid.buy_threshold = buy_threshold

    def calculate_circumstance_array(self):

        desires = [
            microgrid.calculate_tradeable_energy(self.__time)
            for microgrid in self.microgrids
        ]

        circumstance_array = []

        for i, i_desires in enumerate(desires):
            for j, j_desires in enumerate(desires[i + 1 :]):
                i_to_j = min(i_desires[0], j_desires[1])
                j_to_i = min(j_desires[0], i_desires[1])

                if i_to_j > 0 and j_to_i == 0:
                    circumstance_array.append(
                        Trade(self.microgrids[i], self.microgrids[j], i_to_j)
                    )
                elif j_to_i > 0 and i_to_j == 0:
                    circumstance_array.append(
                        Trade(self.microgrids[j], self.microgrids[i], j_to_i)
                    )

        self.circumstance_arrays.append(circumstance_array)
        self.desires.append(desires)

    def total_strategy_cost(self) -> float:
        total_strategy_cost = 0
        # total_overhead_cost = 0

        for microgrid in self.microgrids:
            total_strategy_cost += microgrid.cost_strategy(self.__time)

        return total_strategy_cost

    def total_overhead_cost(self, outcome: list[Trade]) -> float:

        total_cost = 0

        for i, microgrid in enumerate(self.microgrids):
            total_traded = 0
            for trade in outcome:
                if trade.seller is microgrid or trade.buyer is microgrid:
                    total_traded += trade.amount

            if total_traded > self.E_MAX_LINES:
                total_cost += 1.0 * total_traded / self.E_MAX_LINES

        return total_cost

    def total_battery_cost(self, outcome: list[Trade]) -> float:
        battery_cost = 0

        for i, microgrid in enumerate(self.microgrids):
            past_operations = microgrid.timeframe_battery_operations(self.__time)
            current_operations = sum(
                1
                for trade in outcome
                if trade.buyer is microgrid or trade.seller is microgrid
            )
            total_operations = past_operations + current_operations

            battery_cost += total_operations / microgrid.battery_lifetime_cycles

        return battery_cost

    def stabilisation_bonus(self, outcome: list[Trade]) -> float:
        no_initally_unstable = 0
        no_stabilised = 0
        no_destabilised = 0

        buyer_penalty = 0
        seller_penalty = 0

        for i, microgrid in enumerate(self.microgrids):
            sold = 0
            bought = 0

            for j, trade in enumerate(outcome):
                if trade.seller is microgrid:
                    sold += trade.amount
                elif trade.buyer is microgrid:
                    bought += trade.amount

            stable_post_trade = microgrid.is_energy_stabilising(
                self.__time, (sold, bought)
            )

            if microgrid.is_stable(self.__time):
                if not (stable_post_trade):
                    no_destabilised += 1
                else:
                    pass
            else:
                no_initally_unstable += 1
                if stable_post_trade:
                    no_stabilised += 1
                else:
                    pass

        if no_initally_unstable == 0 and no_destabilised > 0:
            # actually impossible
            return -100

        return (
            float(no_stabilised - no_destabilised) / no_initally_unstable
            - buyer_penalty
            - seller_penalty
        )

    def evaluate_trade(self, solution):

        decision = np.array(solution)

        outcome: list[Trade] = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        total_strategy_cost = self.total_strategy_cost()
        total_overhead_cost = self.total_overhead_cost(outcome=outcome)
        total_battery_cost = self.total_battery_cost(outcome=outcome)

        stabilisation_bonus = self.stabilisation_bonus(outcome=outcome)

        final_cost = (
            total_strategy_cost + total_overhead_cost + total_battery_cost
        ) / 3.0

        return stabilisation_bonus - final_cost

    def find_optimal_trade(self):
        problem_dict = {
            "bounds": FloatVar(
                lb=[0] * (len(self.circumstance_arrays[self.__time])),
                ub=[1] * (len(self.circumstance_arrays[self.__time])),
            ),
            "obj_func": self.evaluate_trade,
            "minmax": "max",
        }

        print("Circumstance:")

        for trade in self.circumstance_arrays[self.__time]:
            print(f"s {trade.seller.id}")
            print(f"b {trade.buyer.id}")
            print(f"amount {trade.amount}")

        model = GA.BaseGA(
            epoch=GA_EPOCH, pop_size=GA_POP_SIZE, pc=GA_CROSSOVER, pm=GA_MUTATION
        )
        model.solve(problem_dict)

        final_decision = np.array(model.g_best.solution)
        self.decision_arrays.append(final_decision)

    def execute_optimal_trade(self):

        decision = np.array(self.decision_arrays[self.__time])

        outcome = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        print("Final outcome:")
        for trade in outcome:
            print(f"s {trade.seller.id}")
            print(f"b {trade.buyer.id}")
            print(f"amount {trade.amount}")

        for i, microgrid in enumerate(self.microgrids):
            sell = 0
            buy = 0

            for j, trade in enumerate(outcome):
                if microgrid is trade.seller:
                    sell += trade.amount
                elif microgrid is trade.buyer:
                    buy += trade.amount

            microgrid.resolve_trade(self.__time, (sell, buy))

    def calculate_roles(self):
        for microgrid in self.microgrids:
            microgrid.calculate_next_role()

    def step_time(self):
        self.conduct_internal_energy()  # should be ok
        self.calculate_circumstance_array()
        self.find_optimal_trade()
        self.execute_optimal_trade()
        self.calculate_roles()
        self.update_current_moment()
