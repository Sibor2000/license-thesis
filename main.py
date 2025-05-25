from mgts.microgrid import MicrogridFactory, MicrogridNetworkFactory, Microgrid, MicrogridNetwork
from mgts.behavior.behavior import Role
from mgts.charting.mgn_charts import MicrogridNetworkCharts
import random
import matplotlib.pyplot as plt

random.seed(42)
mgs = []

sell_threshold = 55
buy_threshold = 45

dove_count = 80
hawk_count = 40

for i in range(0, dove_count):
    mgs.append(
        Microgrid(
            id=i,
            max_stored_energy=100,
            initial_stored_energy=random.uniform(0, 100),
            sell_threshold=sell_threshold,
            buy_threshold=buy_threshold,
            role=[Role.DOVE],
            produced_energy=[0]*100,
            consumed_energy=[0]*100
        )
    )

print("Doves ready")

for i in range(dove_count, dove_count + hawk_count):
    mgs.append(
        Microgrid(
            id=i,
            max_stored_energy=100,
            initial_stored_energy=random.uniform(0, 100),
            sell_threshold=sell_threshold,
            buy_threshold=buy_threshold,
            role=[Role.HAWK],
            produced_energy=[0]*100,
            consumed_energy=[0]*100
        )
    )

print("Hawks ready")

mgn = MicrogridNetwork(microgrids=mgs)

mgn.step_time()
mgn.step_time()
mgn.step_time()
mgn.step_time()


charts = True

if charts:
    fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes[0][0], axs_after=axes[0][1])

    MicrogridNetworkCharts.charts_role_and_strategy(mgn, t=0, axs=axes[1][1])
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes[1][0])

    fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.charts_global_best_fitness(mgn=mgn, axs=axes2[0], t=0)
    MicrogridNetworkCharts.charts_diveristy(mgn=mgn, axs=axes2[1], t=0)

    fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn=mgn, axs=axes3[0], t=0)
    MicrogridNetworkCharts.chart_runtime(mgn=mgn, axs=axes3[1], t=0)

    fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.charts_stabilities_before_and_after_trade(mgn=mgn, axs=axes4, t=0)

    plt.tight_layout()
    plt.show()
