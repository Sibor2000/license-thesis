from __future__ import annotations
import numpy as np
from mgts.microgrid import Microgrid

class Trade:
    def __init__(self, seller:Microgrid, buyer:Microgrid, amount:float):
        self.seller = seller
        self.buyer = buyer
        self.amount = amount

    @staticmethod
    def calculate_outcome(circumstance:list[Trade], decision:np.array)->list[Trade]:
        outcome:list[Trade] = []

        for i, max_trade in enumerate(circumstance):
            outcome.append(
                Trade(
                    seller=max_trade.seller,
                    buyer=max_trade.buyer,
                    amount=max_trade.amount *
                    decision[i],
                )
            )

        return outcome