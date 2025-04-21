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
from mgts.simulation.constants import E_MAX_LINES, FLOAT_ROUNDING_DECIMALS
import matplotlib.pyplot as plt
import random
from mgts.behavior import Role, Strategy
import mgts.style as styl
from scipy.optimize import linprog
import math
from matplotlib.ticker import MultipleLocator

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

        return total_strategy_cost / len(self.microgrids)

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

        return battery_cost / len(self.microgrids)

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

            if sold > self.desires[self.__time][i][0]:
                seller_penalty += 100
                # raise Exception("TOO HIGH")
                print(
                    f"SELL EXCEEDED BY {i} b:{sold} max:{self.desires[self.__time][i][0]}"
                )

            if bought > self.desires[self.__time][i][1]:
                buyer_penalty += 100
                print(
                    f"BUY EXCEEDED BY {i} b:{bought} max:{self.desires[self.__time][i][1]}"
                )

        # print(f"stabilised {no_stabilised}")
        # print(f"destabilised {no_destabilised}")
        # print(f"no_initially_unstable {no_initally_unstable}")
        #print(f"seller_penalty {seller_penalty}")
        #print(f"buyer_penalty {buyer_penalty}")

        return (
            float(no_stabilised - no_destabilised) / no_initally_unstable
            - buyer_penalty
            - seller_penalty
        )

    def evaluate_trade(self, solution):

        decision = np.array(solution)

        outcome_raw: list[Trade] = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        outcome = self.scale_trades(
            trades=outcome_raw, desires=self.desires[self.__time]
        )

        total_strategy_cost = self.total_strategy_cost()
        total_overhead_cost = self.total_overhead_cost(outcome=outcome)
        total_battery_cost = self.total_battery_cost(outcome=outcome)

        #print(f"total_strat_cost {total_strategy_cost}")
        #print(f"total_overhead_cost {total_overhead_cost}")
        #print(f"total_battery_cost {total_battery_cost}")

        stabilisation_bonus = self.stabilisation_bonus(outcome=outcome)

        #print(f"stabilisation_bonus {stabilisation_bonus}")

        #raise Exception("HAHA")

        return -(total_strategy_cost + total_overhead_cost + total_battery_cost + (1-stabilisation_bonus))/4.0

        final_cost = (
            total_strategy_cost + total_overhead_cost + total_battery_cost
        ) / 3.0

        #NOTES
        #1 You can't really put the fitness function between 0 and 1 since there is a minus inside
        #2 The strategy cost is actually irrelevant
        return stabilisation_bonus - final_cost

    def find_optimal_trade(self):

        possible_trades = len(self.circumstance_arrays[self.__time])
        print(f"{possible_trades} possible trades")

        problem_dict = {
            "bounds": FloatVar(
                lb=[0] * possible_trades,
                ub=[1] * possible_trades,
                # lb=[0] * (possible_trades + 1),
                # ub=[1] * (possible_trades + 1),
            ),
            "obj_func": self.evaluate_trade,
            "minmax": "max",
        }

        pop_sizes = [50, 100, 200]
        pcs = [0.75, 0.85, 0.95]
        pms = [0.05, 0.10, 0.25]

        combos = [(pop, pc, pm) for pop in pop_sizes for pc in pcs for pm in pms]

        combos=[]

        for (pop, pc, pm) in combos:
            model2 = GA.BaseGA(
                epoch=GA_EPOCH, pop_size=pop, pc=pc, pm=pm
            )
            model2.solve(problem_dict)

        print("Modelmaking")

        model = GA.BaseGA(
            epoch=GA_EPOCH, pop_size=GA_POP_SIZE, pc=GA_CROSSOVER, pm=GA_MUTATION
        )
        model.solve(problem_dict)

        #print(model.history)

        #model.history.save_global_objectives_chart(filename=f"model_charts/{self.__time}/global_obj")
        #model.history.save_local_objectives_chart(filename=f"model_charts/{self.__time}/local_obj")
        #model.history.save_global_best_fitness_chart(filename=f"model_charts/{self.__time}/global_bf")
        #model.history.save_local_best_fitness_chart(filename=f"model_charts/{self.__time}/local_bf")
        model.history.save_diversity_chart(filename=f"model_charts/{self.__time}/diversity")

        final_decision = np.array(model.g_best.solution)
        self.decision_arrays.append(final_decision)

    def execute_optimal_trade(self):

        # dropout_rate = self.decision_arrays[self.__time][-1]
        # decision = np.array(self.decision_arrays[self.__time][:-1])
        decision = np.array(self.decision_arrays[self.__time])

        # print(decision)

        # print(f"Dropout rate is: {dropout_rate}")

        outcome_raw = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        outcome = self.scale_trades(
            trades=outcome_raw, desires=self.desires[self.__time]
        )

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
        print("Internal energy calculations")
        self.conduct_internal_energy()
        print("Circumstance calculations")
        self.calculate_circumstance_array()
        print("Trade optimization")
        self.find_optimal_trade()
        print("Trade execution")
        self.execute_optimal_trade()
        print("Role calculation")
        self.calculate_roles()
        print("Time stepping")
        self.update_current_moment()

    def scale_trades(
        self, trades: list[Trade], desires: list[(float, float)]
    ) -> list[Trade]:
        nr_of_mgs = len(desires)

        total_sales = np.zeros(nr_of_mgs)
        total_buys = np.zeros(nr_of_mgs)

        for trade in trades:
            total_sales[trade.seller.id] += trade.amount

        sell_scale = np.ones(nr_of_mgs)
        for i, total_sale in enumerate(total_sales):
            if total_sale <= desires[i][0]:
                continue
            sell_scale[i] = desires[i][0] / total_sale

        for i, trade in enumerate(trades):
            total_buys[trade.buyer.id] += trade.amount * sell_scale[trade.seller.id]

        buy_scale = np.ones(nr_of_mgs)
        for i, total_buy in enumerate(total_buys):
            if total_buy <= desires[i][1]:
                continue
            buy_scale[i] = desires[i][1] / total_buy

        factor = 10 ** FLOAT_ROUNDING_DECIMALS

        return [
            Trade(
                seller=trade.seller,
                buyer=trade.buyer,
                amount=math.floor(trade.amount * sell_scale[trade.seller.id] * buy_scale[trade.buyer.id] *factor)/factor
                #amount=round(
                #    trade.amount
                #    * sell_scale[trade.seller.id]
                #    * buy_scale[trade.buyer.id],
                #    FLOAT_ROUNDING_DECIMALS,
                #),
            )
            for trade in trades
        ]
