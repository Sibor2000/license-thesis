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
import matplotlib.pyplot as plt
import random
from mgts.behavior import Role, Strategy
import mgts.style as styl
from scipy.optimize import linprog


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

            if sold > self.desires[self.__time-1][i][0]:
                seller_penalty+=100

            if bought > self.desires[self.__time][i][1]:
                buyer_penalty+=100

        #if no_initally_unstable == 0 and no_destabilised > 0:
            # actually impossible
            #return -100

        return (
            float(no_stabilised - no_destabilised) / no_initally_unstable
            - buyer_penalty
            - seller_penalty
        )

    def evaluate_trade(self, solution):

        decision = np.array(solution)

        #dropout_chance = solution[-1]

        #decision = np.array(
        #    [x if random.random() >= dropout_chance else 0 for x in solution[:-1]]
        #)

        outcome_raw: list[Trade] = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        outcome = self.scale_trades(trades=outcome_raw, desires=self.desires[self.__time])
        #outcome = scale_trades(trades=outcome_raw, desires=self.desires)

        total_strategy_cost = self.total_strategy_cost()
        total_overhead_cost = self.total_overhead_cost(outcome=outcome)
        total_battery_cost = self.total_battery_cost(outcome=outcome)

        stabilisation_bonus = self.stabilisation_bonus(outcome=outcome)

        final_cost = (
            total_strategy_cost + total_overhead_cost + total_battery_cost
        ) / 3.0

        return stabilisation_bonus - final_cost

    def find_optimal_trade(self):

        possible_trades = len(self.circumstance_arrays[self.__time])
        print(f"{possible_trades} possible trades")

        problem_dict = {
            "bounds": FloatVar(
                lb=[0] * possible_trades,
                ub=[1] * possible_trades,
                #lb=[0] * (possible_trades + 1),
                #ub=[1] * (possible_trades + 1),
            ),
            "obj_func": self.evaluate_trade,
            "minmax": "max",
        }

        print("Modelmaking")

        model = GA.BaseGA(
            epoch=GA_EPOCH, pop_size=GA_POP_SIZE, pc=GA_CROSSOVER, pm=GA_MUTATION
        )
        model.solve(problem_dict)

        final_decision = np.array(model.g_best.solution)
        self.decision_arrays.append(final_decision)

    def execute_optimal_trade(self):

        #dropout_rate = self.decision_arrays[self.__time][-1]
        #decision = np.array(self.decision_arrays[self.__time][:-1])
        decision = np.array(self.decision_arrays[self.__time])

        #print(decision)

        #print(f"Dropout rate is: {dropout_rate}")

        outcome_raw = Trade.calculate_outcome(
            circumstance=self.circumstance_arrays[self.__time],
            decision=decision,
        )

        outcome = self.scale_trades(trades=outcome_raw, desires=self.desires[self.__time])

        #for trade in outcome:
            #print(f"s:{trade.seller.id} b:{trade.buyer.id} a:{trade.amount}")

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

    def charts_energy_delta(self):
        initial_energies = [mg.calculate_initial_battery_percentage() for mg in self.microgrids]
        latest_energies = [mg.calculate_post_trade_battery_percentage(t=(self.__time-1)) for mg in self.microgrids]

        mg_ids = [mg.id for mg in self.microgrids]

        fig, axes = plt.subplots(1,3, figsize=(12,5))

        axes[0].bar(mg_ids, initial_energies, color="yellow")
        axes[0].set_ylim(0, 1)
        axes[0].set_title("Initial energies")

        axes[1].bar(mg_ids, latest_energies, color="green")
        axes[1].set_ylim(0, 1)
        axes[1].set_title("Post trade energies")

    def charts_role_and_strategy(self, t):

        trade_counts = {
            (Role.DOVE, Strategy.SELLER) : 0,
            (Role.DOVE, Strategy.BUYER) : 0,
            (Role.DOVE, Strategy.STABLE) : 0,
            (Role.HAWK, Strategy.SELLER) : 0,
            (Role.HAWK, Strategy.BUYER) : 0,
            (Role.HAWK, Strategy.STABLE) : 0,
        }

        for microgrid in self.microgrids:
            trade_counts[(microgrid.role[t], microgrid.strategy(t=t))] += 1

        #print(trade_counts)

        labels = []
        amounts = []

        for rs, amount in trade_counts.items():
            labels.append(rs[0].name + " " + rs[1].name)
            amounts.append(amount)

        fig = plt.pie(amounts, labels=labels, colors=styl.STRATEGIES_COLOR_ARRAY)

    def charts_stabilities_before_and_after_trade(self, t):
        stabilities = {
            "stable_before":0,
            "unstable_before":0,
            "stable_after":0,
            "unstable_after":0
        }

        for microgrid in self.microgrids:

            if microgrid.is_stable(t):
                stabilities["stable_before"] +=1
            else:
                stabilities["unstable_before"] +=1

            if microgrid.is_stable(t, post_trade=True):
                stabilities["stable_after"] +=1
            else:
                stabilities["unstable_after"] +=1

    def charts_roles_and_strategies_over_time(self):
        trade_counts = {
            (Role.DOVE, Strategy.SELLER) : [],
            (Role.DOVE, Strategy.BUYER) : [],
            (Role.DOVE, Strategy.STABLE) : [],
            (Role.HAWK, Strategy.SELLER) : [],
            (Role.HAWK, Strategy.BUYER) : [],
            (Role.HAWK, Strategy.STABLE) : [],
        }

        for t in range(0, self.__time):

            for rs, records in trade_counts.items():
                records.append(0)

            for mg in self.microgrids:
                trade_counts[(mg.role[t], mg.strategy(t=t))][t]+=1

        for _, records in trade_counts.items():
            records = np.array(records)

        print(trade_counts)

        #fig, axes = plt.subplots(1, 1, figsize=(12,5))

        #axes[0].stairs(trade_counts[(Role.DOVE, Strategy.SELLER)])
        plt.stairs(trade_counts[(Role.DOVE, Strategy.SELLER)])

    def scale_trades2(self, trades:list[Trade], desires:list[(float, float)])->list[Trade]:
        nr_of_mgs = len(desires)

        #print(desires)

        #What fails?
        #Due to the nature of the linprog maximalizing a row of zeroes sends it crashing

        c= -np.ones(nr_of_mgs)

        A_sell = np.zeros((nr_of_mgs, nr_of_mgs))

        for trade in trades:
            A_sell[trade.seller.id, trade.buyer.id] = trade.amount

        A_buy = A_sell.transpose()

        b_sell_raw = []
        b_buy_raw = []

        for desire in desires:
            b_sell_raw.append(desire[0])
            b_buy_raw.append(desire[1])

        #Zero row_eliminiation
        for i in range(nr_of_mgs-1, -1, -1):
            #sell
            if not np.any(A_sell[i]):
                A_sell = np.delete(A_sell, i, axis=0)
                del b_sell_raw[i]
                #print("Sell row deleted")

            #buy
            if not np.any(A_buy[i]):
                A_buy = np.delete(A_buy, i, axis=0)
                del b_buy_raw[i]
                #print("Buy row deleted")

        b_sell = np.array(b_sell_raw)
        b_buy = np.array(b_buy_raw)

        res1 = linprog(
            c=c,
            A_ub=A_sell,
            b_ub=b_sell,
            method='highs',
            bounds=[(0.0,1.0)]*nr_of_mgs,
            #options={"disp":True}
        )

        res2 = linprog(
            c=c,
            A_ub=A_buy,
            b_ub=b_buy,
            method='highs',
            bounds=[(0.0,1.0)]*nr_of_mgs,
            #options={"disp":True}
        )

        #print(res1.success, res2.success)

        if res1.success and res2.success:
            #final_scale = np.minimum.reduce([res1.x, res2.x])

            #print(final_scale)

            new_trades =[]

            #print(res1.x)
            #print(res2.x)

            for trade in trades:
                #This might be wrong
                scale_factor = min(res2.x[trade.buyer.id], res1.x[trade.seller.id])
                #print(scale_factor)
                new_trades.append(Trade(seller=trade.seller, buyer=trade.buyer, amount=trade.amount*scale_factor))

            #raise Exception("HAHA")
            return new_trades
        else:
            print ("Failed scaling")
            raise Exception("Uh oh")

    def scale_trades(self, trades:list[Trade], desires:list[(float, float)])->list[Trade]:
        nr_of_mgs = len(desires)

        total_sales = np.zeros(nr_of_mgs)
        total_buys = np.zeros(nr_of_mgs)


        for trade in trades:
            total_sales[trade.seller.id] += trade.amount

        sell_scale = np.ones(nr_of_mgs)
        for i, total_sale in enumerate(total_sales):
            if total_sale <= desires[i][0]:
                continue
            sell_scale[i]=desires[i][0]/total_sale

        for i, trade in enumerate(trades):
            total_buys[trade.buyer.id] += trade.amount * sell_scale[trade.seller.id]

        buy_scale = np.ones(nr_of_mgs)
        for i, total_buy in enumerate(total_buys):
            if total_buy <= desires[i][1]:
                continue
            buy_scale[i]=desires[i][1]/total_buy

        return [
            Trade(
                seller=trade.seller,
                buyer=trade.buyer,
                amount=trade.amount * sell_scale[trade.seller.id] * buy_scale[trade.buyer.id]
                )
                for trade in trades]

        scaled_trades = []
        for trade in trades:
            amount = 1.0 * round(trade.amount * sell_scale[trade.seller.id] * buy_scale[trade.buyer.id])
            if amount > 0:
                #print(amount)
                scaled_trades.append(Trade(seller=trade.seller.id, buyer=trade.buyer.id, amount=amount))

        #raise Exception("UHOH")
        return scaled_trades