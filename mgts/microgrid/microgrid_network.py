from mgts.microgrid import Microgrid


###
# You might get inconsistencies if you call get_current_moment outside step time
###
class MicrogridNetwork:
    def __init__(self, microgrids: list[Microgrid] = None):
        self.microgrids = microgrids if microgrids else []
        self.__time = 0

    def update_current_moment(self):
        self.__time = len(self.microgrids[0].stored_energy)

    def get_current_moment(self):
        return self.__time

    def conduct_internal_energy(self):
        for microgrid in self.microgrids:
            microgrid.calculate_stored_energy(self.__time)

    def conduct_trade(self):
        desires = []
        for microgrid in self.microgrids:
            desires.append(microgrid.calculate_tradeable_energy(t=self.__time))
        self.desires = desires

        # sell, soft sell, soft buy, buy
        state_of_market = (0, 0, 0, 0)

        for desire in desires:
            state_of_market = (
                state_of_market[0] + desire[0],
                state_of_market[1] + desire[1],
                state_of_market[2] + desire[2],
                state_of_market[3] + desire[3],
            )

        print(desires)

        hard_delta = state_of_market[3] - state_of_market[0]  # buy-sell

        if hard_delta < 0:
            # Supply is high, soft buys step in
            supply = state_of_market[0]
            demand = state_of_market[2] + state_of_market[3]

            amount = min(supply, demand)

            satisfaction_rate = amount / supply

            if satisfaction_rate < 1:
                # uncovered supply
                for i in range(0, len(self.microgrids)):
                    if self.desires[i][0] > 0:
                        # sellers sell as much as they can, proportionately to their offering
                        self.microgrids[i].energy_transact(
                            amount=-satisfaction_rate * self.desires[i][0],
                            t=self.__time,
                        )

                    if self.desires[i][2] > 0 or self.desires[i][3] > 0:
                        # buyers buy as much as they asked for
                        self.microgrids[i].energy_transact(
                            amount=self.desires[i][2] + self.desires[i][3],
                            t=self.__time,
                        )
            else:
                # covered supply

                # split the remaining energy to be covered between the soft buyers
                buy_split_ratio = hard_delta / state_of_market[2]

                for i in range(0, len(self.microgrids)):
                    if self.desires[i][0] > 0:
                        # sellers sell all they want
                        self.microgrids[i].energy_transact(
                            amount=-self.desires[i][0], t=self.__time
                        )

                    if self.desires[i][2] > 0 or self.desires[i][3]:
                        # the hard buys go through as is, the soft sells are split between microgrids
                        self.microgrids[i].energy_transact(
                            amount=self.desires[i][3]
                            + buy_split_ratio * self.desires[i][2],
                            t=self.__time,
                        )

        elif hard_delta > 0:
            # Demand is high, soft sells step in

            supply = state_of_market[0] + state_of_market[1]
            demand = state_of_market[3]

            amount = min(supply, demand)

            satisfaction_rate = amount / demand

            if satisfaction_rate < 1:
                # uncovered demand
                for i in range(0, len(self.microgrids)):
                    if self.desires[i][0] > 0 or self.desires[i][1] > 0:
                        # sellers sell as much as they posted
                        self.microgrids[i].energy_transact(
                            amount=-(self.desires[i][0] + self.desires[i][1]),
                            t=self.__time,
                        )

                    if self.desires[i][3] > 0:
                        # buyers get as much as they can, proportionately to their personal demand
                        self.microgrids[i].energy_transact(
                            amount=satisfaction_rate * self.desires[i][3], t=self.__time
                        )
            else:
                # covered demand

                # split the remaining energy to be covered between the soft sellers
                sell_split_ratio = hard_delta / state_of_market[1]

                for i in range(0, len(self.microgrids)):
                    if self.desires[i][0] > 0 or self.desires[i][1] > 0:
                        # the hard sells go through as is, the soft sells are proportionately affected
                        self.microgrids[i].energy_transact(
                            amount=-(
                                self.desires[i][0]
                                + sell_split_ratio * self.desires[i][1]
                            ),
                            t=self.__time,
                        )
                    if self.desires[i][3] > 0:
                        # buyers get as much as they ordered
                        self.microgrids[i].energy_transact(
                            amount=self.desires[i][3], t=self.__time
                        )
        else:
            # balanced energy trade, no one steps in, only direct trades occur, everyone is satisfied
            for i in range(0, len(self.microgrids)):
                amount = desires[i][3] - desires[i][0]
                self.microgrids[i].energy_transact(amount=amount, t=self.__time)

    def conduct_post_trade_energy(self):
        for microgrid in self.microgrids:
            microgrid.resolve_trade(t=self.__time)

    def conduct_threshold_adjustment(self):
        pass

    def step_time(self):
        self.conduct_internal_energy()
        self.conduct_trade()
        self.conduct_post_trade_energy()
        self.conduct_threshold_adjustment()
        self.update_current_moment()
