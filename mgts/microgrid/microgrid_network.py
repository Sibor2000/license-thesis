from mgts.microgrid import Microgrid
from mgts.microgrid import Trade
from mealpy.evolutionary_based import GA
from mealpy.utils.problem import Problem
from mealpy.utils.agent import Agent
from mealpy import FloatVar
import numpy as np
from mgts.simulation.constants import E_MAX_LINES, FLOAT_ROUNDING_DECIMALS
import math
import csv


class MicrogridNetwork:
    def __init__(self, microgrids: list[Microgrid] = None):
        self.microgrids = microgrids if microgrids else []
        self.__time = 0

        self.circumstance_arrays: list[list[Trade]] = []
        self.desires = []
        self.decision_arrays = []

        self.E_MAX_LINES = E_MAX_LINES

        self.models_global_histories: list[dict] = []
        self.models_diversities: list[dict] = []
        self.models_exploration: list[dict] = []
        self.models_exploitation: list[dict] = []
        self.models_runtimes: list[dict] = []

        self.__circumstance_and_decision = False

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

        circumstance_array: list[Trade] = []

        for i, i_desires in enumerate(desires):
            for j_raw, j_desires in enumerate(desires[i + 1 :]):
                j = i + j_raw + 1

                i_to_j = min(i_desires[0], j_desires[1])
                j_to_i = min(j_desires[0], i_desires[1])

                # print(f"i:{i} j:{j} itoj{i_to_j} jtoi:{j_to_i}")

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

    def total_overhead_cost(self, outcome: list[Trade]) -> float:
        exceed_count = sum(1 for trade in outcome if trade.amount > self.E_MAX_LINES)

        return 1.0 * exceed_count / len(outcome)

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

        return (
            float(no_stabilised - no_destabilised) / no_initally_unstable
            - buyer_penalty
            - seller_penalty
        )

    def variance_bonus(self, outcome: list[Trade]) -> float:
        square_sum = 0
        for trade in outcome:
            square_sum += trade.amount**2

        base_sum = sum(
            desire[0] ** 2 + desire[1] ** 2 for desire in self.desires[self.__time]
        )

        return 2.0 * square_sum / base_sum

    def evaluate_trade(self, solution):

        decision = np.array(solution)

        if self.__circumstance_and_decision:
            outcome_raw = []

            circumstance = self.circumstance_arrays[self.__time]
            for i, trade in enumerate(circumstance):
                outcome_raw.append(
                    Trade(seller=trade.seller, buyer=trade.buyer, amount=decision[i])
                )
        else:
            outcome_raw: list[Trade] = Trade.calculate_outcome(
                circumstance=self.circumstance_arrays[self.__time],
                decision=decision,
            )

        outcome = self.scale_trades(
            trades=outcome_raw, desires=self.desires[self.__time]
        )

        total_overhead_cost = self.total_overhead_cost(outcome=outcome)
        total_battery_cost = self.total_battery_cost(outcome=outcome)

        # print(f"total_overhead_cost {total_overhead_cost}")
        # print(f"total_battery_cost {total_battery_cost}")

        variance_bonus = self.variance_bonus(outcome=outcome)
        stabilisation_bonus = self.stabilisation_bonus(outcome=outcome)

        # print(f"variance_bonus {variance_bonus}")
        # print(f"stabilisation_bonus {stabilisation_bonus}")

        return (
            -(
                total_overhead_cost
                + total_battery_cost
                + (1.0 - stabilisation_bonus)
                + (1.0 - variance_bonus)
            )
            / 4.0
        )

    def find_optimal_trade(self):
        possible_trades = len(self.circumstance_arrays[self.__time])

        full_scale = [trade.amount for trade in self.circumstance_arrays[self.__time]]

        print(f"{possible_trades} possible trades")

        csv_write = False
        csv_file = None
        csv_writer = None

        custom_combos = True
        combos = None

        if csv_write:
            csv_file = open("sol.csv", "w", newline="", encoding="utf-8")
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)

        if custom_combos:
            combos = [
                #TODO: calculate the best solutions params
                (200, 0.95, 0.025, "tournament", "uniform", False, "flip", False, 25),
                (200, 0.75, 0.025, "tournament", "uniform", False, "flip", False, 25),
                (200, 0.95, 0.050, "tournament", "uniform", False, "flip", False, 25),
                (200, 0.75, 0.050, "tournament", "uniform", False, "flip", False, 25)
                ]

            combos = [
                (20, 0.95, 0.025, "tournament", "uniform", False, "flip", False, 10),
                (40, 0.95, 0.025, "tournament", "uniform", False, "flip", False, 10),
            ]
        else:
            pop_sizes = [50, 200]
            pcs = [0.75, 0.95]
            pms = [0.025, 0.05, 0.25]
            selection = ["roulette", "tournament"]
            crossover = ["one_point", "multi_points", "uniform", "arithmetic"]
            mutation_multipoints = [True, False]
            mutation = ["flip", "swap"]
            search_scaling = [False, True]
            epoch = [25]

            combos = [
                (pop, pc, pm, sel, cros, mp, mut, ss, ep)
                for pop in pop_sizes
                for pc in pcs
                for pm in pms
                for sel in selection
                for cros in crossover
                for mp in mutation_multipoints
                for mut in mutation
                for ss in search_scaling
                for ep in epoch
            ]

        print(f"There are {len(combos)} in total")

        best_fits = {}
        diversities = {}
        explorations = {}
        exploitations = {}
        runtimes = {}
        print("Multimodelmaking")

        model2 = []
        best_agent: Agent = None

        for pop, pc, pm, sel, cros, mp, mut, ss, ep in combos:
            self.__circumstance_and_decision = ss

            problem_dict = {
                "bounds": FloatVar(
                    lb=[0.0] * possible_trades,
                    ub=(
                        [1.0] * possible_trades
                        if self.__circumstance_and_decision
                        else full_scale
                    ),
                ),
                "obj_func": self.evaluate_trade,
                "minmax": "max",
            }

            model2 = GA.BaseGA(
                epoch=ep,
                pop_size=pop,
                pc=pc,
                pm=pm,
                mutation_multipoints=mp,
                mut=mut,
                selection=sel,
                crossover=cros,
            )
            model2.solve(problem_dict)

            model_id = f"{pop}-{pc}-{pm}-{mp}-{mut}-{sel}-{cros}-{ss}"

            best_fits[model_id] = model2.history.list_global_best_fit
            diversities[model_id] = model2.history.list_diversity
            explorations[model_id] = model2.history.list_exploration
            exploitations[model_id] = model2.history.list_exploitation
            runtimes[model_id] = sum(model2.history.list_epoch_time)

            if best_agent == None:
                best_agent = model2.g_best
            else:
                best_agent = best_agent.get_better_solution(model2.g_best, minmax="max")

            if csv_write:
                csv_writer.writerow(
                    [
                        pop,
                        pc,
                        pm,
                        sel,
                        cros,
                        ss,
                        model2.g_best.target.fitness,
                        model2.history.list_diversity[-1],
                        model2.history.list_exploration[-1],
                        model2.history.list_exploitation[-1],
                        sum(model2.history.list_epoch_time)
                    ]
                )

        if csv_write:
            csv_file.close()

        self.models_global_histories.append(best_fits)
        self.models_diversities.append(diversities)
        self.models_exploration.append(explorations)
        self.models_exploitation.append(exploitations)
        self.models_runtimes.append(runtimes)

        final_decision = np.array(best_agent.solution)
        self.decision_arrays.append(final_decision)

    def execute_optimal_trade(self):
        decision = np.array(self.decision_arrays[self.__time])

        if self.__circumstance_and_decision:
            outcome_raw = Trade.calculate_outcome(
                circumstance=self.circumstance_arrays[self.__time],
                decision=decision,
            )
        else:
            outcome_raw = []

            circumstance = self.circumstance_arrays[self.__time]
            for i, trade in enumerate(circumstance):
                outcome_raw.append(
                    Trade(seller=trade.seller, buyer=trade.buyer, amount=decision[i])
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

        # print(desires)

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

        factor = 10**FLOAT_ROUNDING_DECIMALS

        return [
            Trade(
                seller=trade.seller,
                buyer=trade.buyer,
                amount=math.floor(
                    trade.amount
                    * sell_scale[trade.seller.id]
                    * buy_scale[trade.buyer.id]
                    * factor
                )
                / factor,
            )
            for trade in trades
        ]
