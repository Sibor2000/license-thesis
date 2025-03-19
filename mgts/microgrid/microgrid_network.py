from mgts.microgrid import Microgrid
from mealpy.evolutionary_based import GA
from mealpy.utils.problem import Problem
from mealpy import FloatVar
import numpy as np


class MicrogridNetwork:
    def __init__(self, microgrids: list[Microgrid] = None):
        self.microgrids = microgrids if microgrids else []
        self.__time = 0

        self.circumstande_matrices = []

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

        desires = [microgrid.calculate_tradeable_energy(self.__time) for microgrid in self.microgrids]

        print(desires)

        circumstance_matrix = np.zeros((len(self.microgrids), len(self.microgrids)))

        for i, seller_desires in enumerate(desires):
            for j, buyer_desires in enumerate(desires):
                if i==j:
                    continue
                elif seller_desires[0] > 0 and seller_desires[1] > 0 and buyer_desires[0] > 0 and buyer_desires[1] > 0:
                    #Stable dove-dove meeting
                    #TODO: maybe see if they are indeed stable to avoid edge case?
                    continue
                else:
                    circumstance_matrix[i][j] = min(seller_desires[0], buyer_desires[1])

        self.circumstande_matrices.append(circumstance_matrix)

    def find_optimal_trade(self):
        pass

    def step_time(self):
        self.conduct_internal_energy()  # should be ok
        self.calculate_circumstance_matrix()
        self.update_current_moment()
