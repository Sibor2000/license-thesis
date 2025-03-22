from mgts.microgrid import Microgrid
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

        self.circumstance_matrices = []

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

    def calculate_circumstance_matrix(self):

        desires = [
            microgrid.calculate_tradeable_energy(self.__time)
            for microgrid in self.microgrids
        ]

        circumstance_matrix = np.zeros((len(self.microgrids), len(self.microgrids)))

        for i, seller_desires in enumerate(desires):
            for j, buyer_desires in enumerate(desires):
                if i == j:
                    continue
                elif (
                    seller_desires[0] > 0
                    and seller_desires[1] > 0
                    and buyer_desires[0] > 0
                    and buyer_desires[1] > 0
                ):
                    # Stable dove-dove meeting
                    # TODO: maybe see if they are indeed stable to avoid edge case?
                    continue
                else:
                    circumstance_matrix[i][j] = min(seller_desires[0], buyer_desires[1])

        self.circumstance_matrices.append(circumstance_matrix)

    def total_strategy_cost(self)->float:
        total_strategy_cost = 0
        # total_overhead_cost = 0

        for microgrid in self.microgrids:
            total_strategy_cost += microgrid.cost_strategy(self.__time)

        return total_strategy_cost

    def total_overhead_cost(self, outcome)->float:

        total_cost = 0

        for i in range(0, len(self.microgrids)):
            # total = sold + bought
            total_traded = np.sum(outcome[i]) + np.sum(np.transpose(outcome)[i])

            if total_traded > self.E_MAX_LINES:
                total_cost += 1.0 * total_traded / self.E_MAX_LINES

        return total_cost

    def total_battery_cost(self, outcome)->float:
        outcome_t = np.transpose(outcome)
        battery_cost = 0

        for i, microgrid in enumerate(self.microgrids):
            past_operations = microgrid.timeframe_battery_operations(self.__time)
            current_operations = np.count_nonzero(outcome[i]) + np.count_nonzero(outcome_t[i])
            total_operations = past_operations + current_operations

            battery_cost += total_operations / microgrid.battery_lifetime_cycles

        return battery_cost


    def evaluate_trade(self, solution):

        decision = np.array(solution).reshape(
            (len(self.microgrids), len(self.microgrids))
        )
        circumstance = self.circumstance_matrices[self.__time]

        outcome = decision * circumstance

        total_strategy_cost = self.total_strategy_cost()
        total_overhead_cost = self.total_overhead_cost(outcome=outcome)
        total_battery_cost = self.total_battery_cost(outcome=outcome)

        final_cost = total_strategy_cost + total_overhead_cost + total_battery_cost

        return -final_cost

    def find_optimal_trade(self):
        problem_dict = {
            "bounds": FloatVar(
                lb=[0] * (len(self.microgrids) ** 2),
                ub=[1] * (len(self.microgrids) ** 2),
            ),
            "obj_func": self.evaluate_trade,
            "minmax": "max",
        }

        model = GA.BaseGA(
            epoch=GA_EPOCH, pop_size=GA_POP_SIZE, pc=GA_CROSSOVER, pm=GA_MUTATION
        )
        model.solve(problem_dict)

        #print("Best solution:")
        #print(model.g_best.solution)

        final_decision = np.array(model.g_best.solution).reshape(
            (len(self.microgrids), len(self.microgrids))
        )

        print(self.circumstance_matrices[self.__time] * final_decision)

    def step_time(self):
        self.conduct_internal_energy()  # should be ok
        self.calculate_circumstance_matrix()
        self.find_optimal_trade()
        self.update_current_moment()
