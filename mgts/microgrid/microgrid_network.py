from mgts.microgrid import Microgrid

###
# You might get inconsistencies if you call get_current_moment outside step time
###
class MicrogridNetwork:
    def __init__(self, microgrids:list[Microgrid]=None):
        self.microgrids = microgrids if microgrids else []

    def get_current_moment(self):
        return len(self.microgrids[0].stored_energy)

    def conduct_internal_energy(self):
        time = self.get_current_moment()
        for microgrid in self.microgrids:
            microgrid.calculate_stored_energy(time)


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