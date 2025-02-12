class MicrogridNetwork:
    def __init__(self, microgrids=[]):
        self.microgrids = microgrids

    def conduct_internal_energy(self):
        pass

    def conduct_trade(self):
        pass

    def conduct_post_trade_energy(self):
        pass

    def conduct_threshold_adjustment(self):
        pass

    def step_time(self):
        self.conduct_internal_energy()
        self.conduct_trade()
        self.conduct_post_trade_energy()
        self.conduct_threshold_adjustment()