from mgts.microgrid import MicrogridFactory, MicrogridNetworkFactory, Microgrid, MicrogridNetwork
from mgts.behavior.behavior import Role
from mgts.charting.mgn_charts import MicrogridNetworkCharts
import random
import matplotlib.pyplot as plt

random.seed(42)
mgs = []

for i in range(0, 100):
    mgs.append(
        Microgrid(
            id=i,
            max_stored_energy=100,
            initial_stored_energy=random.uniform(0, 100),
            sell_threshold=66,
            buy_threshold=33,
            role=[Role.DOVE],
            produced_energy=[0]*100,
            consumed_energy=[0]*100
        )
    )

print("Doves ready")

for i in range(100, 150):
    mgs.append(
        Microgrid(
            id=i,
            max_stored_energy=100,
            initial_stored_energy=random.uniform(0, 100),
            sell_threshold=66,
            buy_threshold=33,
            role=[Role.HAWK],
            produced_energy=[0]*100,
            consumed_energy=[0]*100
        )
    )

print("Hawks ready")

mgn = MicrogridNetwork(microgrids=mgs)

mgn.step_time()
#mgn.step_time()
#mgn.step_time()
#mgn.step_time()

fig, axes = plt.subplots(2, 2, figsize=(12, 5))

MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes[0][0], axs_after=axes[0][1])

MicrogridNetworkCharts.chart_role_and_strategy(mgn, t=0, axs=axes[1][1])
MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes[1][0])

plt.tight_layout()
plt.show()