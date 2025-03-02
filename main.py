from mgts.microgrid import MicrogridFactory, MicrogridNetworkFactory
import pandas as pd

path = "./datasets/test.xlsx"

mgn = MicrogridNetworkFactory.create_from_file(path=path)

mgn.microgrids[0].charge_efficiency = 1
mgn.microgrids[1].discharge_efficiency = 0.4
mgn.microgrids[2].discharge_efficiency = 1

mgn.microgrids[0].initial_stored_energy = 0
mgn.microgrids[1].initial_stored_energy = 100
mgn.microgrids[2].initial_stored_energy = 100

mgn.microgrids[0].buy_threshold = 100.0
mgn.microgrids[0].soft_buy_threshold = 100.0
mgn.microgrids[0].soft_sell_threshold = 100.0
mgn.microgrids[0].sell_threshold = 100.0

mgn.microgrids[1].buy_threshold = 0.0
mgn.microgrids[1].soft_buy_threshold = 0.0
mgn.microgrids[1].soft_sell_threshold = 0.0
mgn.microgrids[1].sell_threshold = 100.0

mgn.microgrids[2].buy_threshold = 0.0
mgn.microgrids[2].soft_buy_threshold = 0.0
mgn.microgrids[2].soft_sell_threshold = 0.0
mgn.microgrids[2].sell_threshold = 0.0

mgn.conduct_internal_energy()

print(mgn.microgrids[2].stored_energy)

mgn.conduct_trade()
mgn.conduct_post_trade_energy()

print("MG1")
print(mgn.microgrids[0].stored_energy)
print(mgn.microgrids[0].stored_energy_post_trade)

print("MG2")
print(mgn.microgrids[1].stored_energy)
print(mgn.microgrids[1].stored_energy_post_trade)

print("MG3")
print(mgn.microgrids[2].stored_energy)
print(mgn.microgrids[2].stored_energy_post_trade)
#self.conduct_threshold_adjustment()
#self.update_current_moment()