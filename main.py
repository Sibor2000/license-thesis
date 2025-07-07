from mgts.microgrid import Microgrid, MicrogridNetwork
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
            #initial_stored_energy=100,
            #sell_threshold=random.uniform(55, 75),
            sell_threshold=sell_threshold,
            buy_threshold=buy_threshold,
            role=[Role.DOVE],
            produced_energy=[0]*10,
            consumed_energy=[0]*10
        )
    )

print("Doves ready")

for i in range(dove_count, dove_count + hawk_count):
    mgs.append(
        Microgrid(
            id=i,
            max_stored_energy=100,
            initial_stored_energy=random.uniform(0, 100),
            #initial_stored_energy=100,
            sell_threshold=sell_threshold,
            buy_threshold=buy_threshold,
            role=[Role.HAWK],
            produced_energy=[0]*10,
            consumed_energy=[0]*10
        )
    )

print("Hawks ready")

mgn = MicrogridNetwork(microgrids=mgs)

mgn.step_time()
#mgn.step_time()
#mgn.step_time()
#mgn.step_time()


charts = True

if charts:
    #fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    fig0, axes0 = plt.subplots(1, 1, figsize=(12, 5))
    fig1, axes1 = plt.subplots(1, 1, figsize=(12, 5))
    fig2, axes2 = plt.subplots(1, 1, figsize=(12, 5))
    fig3, axes3 = plt.subplots(1, 1, figsize=(12, 5))
    fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))
    fig5, axes5 = plt.subplots(1, 1, figsize=(12, 5))
    fig6, axes6 = plt.subplots(1, 1, figsize=(12, 5))
    fig7, axes7 = plt.subplots(1, 1, figsize=(12, 5))
    fig8, axes8 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes0, axs_after=axes1)

    MicrogridNetworkCharts.chart_role_and_strategy(mgn, axs=axes2, t=0)
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes3)

    #fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_global_best_fitness(mgn=mgn, axs=axes4, t=0)
    MicrogridNetworkCharts.chart_diveristy(mgn=mgn, axs=axes5, t=0)

    #fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn=mgn, axs=axes6, t=0)
    MicrogridNetworkCharts.chart_runtime(mgn=mgn, axs=axes7, t=0)

    #fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.chart_stabilities_before_and_after_trade(mgn=mgn, axs=axes8)

    plt.tight_layout()
    plt.show()

mgn.step_time()

if charts:
    #fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    fig0, axes0 = plt.subplots(1, 1, figsize=(12, 5))
    fig1, axes1 = plt.subplots(1, 1, figsize=(12, 5))
    fig2, axes2 = plt.subplots(1, 1, figsize=(12, 5))
    fig3, axes3 = plt.subplots(1, 1, figsize=(12, 5))
    fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))
    fig5, axes5 = plt.subplots(1, 1, figsize=(12, 5))
    fig6, axes6 = plt.subplots(1, 1, figsize=(12, 5))
    fig7, axes7 = plt.subplots(1, 1, figsize=(12, 5))
    fig8, axes8 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes0, axs_after=axes1)

    MicrogridNetworkCharts.chart_role_and_strategy(mgn, axs=axes2, t=1)
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes3)

    #fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_global_best_fitness(mgn=mgn, axs=axes4, t=1)
    MicrogridNetworkCharts.chart_diveristy(mgn=mgn, axs=axes5, t=1)

    #fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn=mgn, axs=axes6, t=1)
    MicrogridNetworkCharts.chart_runtime(mgn=mgn, axs=axes7, t=1)

    #fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.chart_stabilities_before_and_after_trade(mgn=mgn, axs=axes8)

    plt.tight_layout()
    plt.show()

mgn.step_time()

charts = True

if charts:
    #fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    fig0, axes0 = plt.subplots(1, 1, figsize=(12, 5))
    fig1, axes1 = plt.subplots(1, 1, figsize=(12, 5))
    fig2, axes2 = plt.subplots(1, 1, figsize=(12, 5))
    fig3, axes3 = plt.subplots(1, 1, figsize=(12, 5))
    fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))
    fig5, axes5 = plt.subplots(1, 1, figsize=(12, 5))
    fig6, axes6 = plt.subplots(1, 1, figsize=(12, 5))
    fig7, axes7 = plt.subplots(1, 1, figsize=(12, 5))
    fig8, axes8 = plt.subplots(1, 1, figsize=(12, 5))
    fig9, axes9 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes0, axs_after=axes1)

    MicrogridNetworkCharts.chart_role_and_strategy(mgn, axs=axes2, t=2)
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes3)

    #fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_global_best_fitness(mgn=mgn, axs=axes4, t=2)
    MicrogridNetworkCharts.chart_diveristy(mgn=mgn, axs=axes5, t=2)

    #fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn=mgn, axs=axes6, t=2)
    MicrogridNetworkCharts.chart_runtime(mgn=mgn, axs=axes7, t=2)

    #fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.chart_stabilities_before_and_after_trade(mgn=mgn, axs=axes8)

    MicrogridNetworkCharts.chart_stabilities_over_time(mgn=mgn, axs=axes9)

    plt.tight_layout()
    plt.show()


mgn.step_time()

if charts:
    #fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    fig0, axes0 = plt.subplots(1, 1, figsize=(12, 5))
    fig1, axes1 = plt.subplots(1, 1, figsize=(12, 5))
    fig2, axes2 = plt.subplots(1, 1, figsize=(12, 5))
    fig3, axes3 = plt.subplots(1, 1, figsize=(12, 5))
    fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))
    fig5, axes5 = plt.subplots(1, 1, figsize=(12, 5))
    fig6, axes6 = plt.subplots(1, 1, figsize=(12, 5))
    fig7, axes7 = plt.subplots(1, 1, figsize=(12, 5))
    fig8, axes8 = plt.subplots(1, 1, figsize=(12, 5))
    fig9, axes9 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.charts_energy_delta(mgn, axs_before=axes0, axs_after=axes1)

    MicrogridNetworkCharts.chart_role_and_strategy(mgn, axs=axes2, t=3)
    MicrogridNetworkCharts.charts_roles_and_strategies_over_time(mgn, axs=axes3)

    #fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_global_best_fitness(mgn=mgn, axs=axes4, t=3)
    MicrogridNetworkCharts.chart_diveristy(mgn=mgn, axs=axes5, t=3)

    #fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    MicrogridNetworkCharts.chart_exploration_vs_exploitation(mgn=mgn, axs=axes6, t=3)
    MicrogridNetworkCharts.chart_runtime(mgn=mgn, axs=axes7, t=3)

    #fig4, axes4 = plt.subplots(1, 1, figsize=(12, 5))

    MicrogridNetworkCharts.chart_stabilities_before_and_after_trade(mgn=mgn, axs=axes8)

    MicrogridNetworkCharts.chart_stabilities_over_time(mgn=mgn, axs=axes9)

    plt.tight_layout()
    plt.show()

#print(mgn.to_scenario_dict()["microgrids"][70:])

#mgn.save_scenario_json()