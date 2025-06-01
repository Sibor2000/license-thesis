from mgts.behavior import Role, Strategy
import mgts.style as styl
from matplotlib.ticker import MultipleLocator
import numpy as np
from mgts.microgrid.microgrid_network import MicrogridNetwork
import io
import base64
import matplotlib.pyplot as plt

class MicrogridNetworkCharts:
    def charts_energy_delta(mgn:MicrogridNetwork, axs_before, axs_after):
        initial_energies = [
            mg.calculate_initial_battery_percentage() for mg in mgn.microgrids
        ]
        latest_energies = [
            mg.calculate_post_trade_battery_percentage(t=(mgn.get_current_moment() - 1))
            for mg in mgn.microgrids
        ]

        mg_ids = [mg.id for mg in mgn.microgrids]

        axs_before.bar(mg_ids, initial_energies, color="yellow")
        axs_before.set_xlabel("Microgrid ids")
        axs_before.set_ylabel("Stored energy ratio")
        #axes[0].set_xticks(np.arange(len(mgn.microgrids)))
        #for label in axes[0].get_xticklabels():
        #    label.set_rotation(45)
        axs_before.set_ylim(0, 1)
        axs_before.set_title("Initial energies")
        axs_before.axhline(y=mgn.microgrids[0].sell_threshold/100.0, color='green', linestyle="--", linewidth=2, label="Sell threshold")
        axs_before.axhline(y=mgn.microgrids[0].buy_threshold/100.0, color='red', linestyle="--", linewidth=2, label="Buy threshold")

        axs_after.bar(mg_ids, latest_energies, color="blue")
        axs_after.set_xlabel("Microgrid ids")
        axs_after.set_ylabel("Stored energy ratio")
        axs_after.set_ylim(0, 1)
        axs_after.set_title("Post trade energies")
        axs_after.axhline(y=mgn.microgrids[0].sell_threshold/100.0, color='green', linestyle="--", linewidth=2, label="Sell threshold")
        axs_after.axhline(y=mgn.microgrids[0].buy_threshold/100.0, color='red', linestyle="--", linewidth=2, label="Buy threshold")

    def charts_role_and_strategy(mgn:MicrogridNetwork, t, axs):
        trade_counts = {
            (Role.DOVE, Strategy.SELLER): 0,
            (Role.DOVE, Strategy.BUYER): 0,
            (Role.DOVE, Strategy.STABLE): 0,
            (Role.HAWK, Strategy.SELLER): 0,
            (Role.HAWK, Strategy.BUYER): 0,
            (Role.HAWK, Strategy.STABLE): 0,
        }

        for microgrid in mgn.microgrids:
            trade_counts[(microgrid.role[t], microgrid.strategy(t=t))] += 1

        labels = []
        amounts = []

        for rs, amount in trade_counts.items():
            labels.append(rs[0].name + " " + rs[1].name)
            amounts.append(amount)

        axs.pie(amounts, labels=labels, colors=styl.STRATEGIES_COLOR_ARRAY)
        axs.set_title(f"Roles and strategies at moment {t}")

    def charts_stabilities_before_and_after_trade(mgn:MicrogridNetwork, axs, t):
        stabilities = {
            "stable_before": 0,
            "unstable_before": 0,
            "stable_after": 0,
            "unstable_after": 0,
        }

        for microgrid in mgn.microgrids:

            if microgrid.is_stable(t, post_trade=False):
                stabilities["stable_before"] += 1
            else:
                stabilities["unstable_before"] += 1

            if microgrid.is_stable(t, post_trade=True):
                stabilities["stable_after"] += 1
            else:
                stabilities["unstable_after"] += 1

        #states = list(stabilities.keys())
        #counts = list(stabilities.values())

        labels = ["Stable", "Unstable"]
        befores = [stabilities["stable_before"], stabilities["unstable_before"]]
        afters = [stabilities["stable_after"], stabilities["unstable_after"]]

        x= np.arange(len(labels))
        width = 0.35

        axs.bar(x-width/2, befores, width, label="Before trade", color="orange")
        axs.bar(x+width/2, afters, width, label="After trade", color="blue")

        axs.set_title(f"Stable and unstable microgrids before and after trade in moment {t}")

        axs.set_xticks(x)
        axs.set_xticklabels(labels)

        axs.set_ylabel("Nr. Of MGs")

        axs.legend()


    def charts_roles_and_strategies_over_time(mgn:MicrogridNetwork, axs):
        trade_counts = {
            (Role.DOVE, Strategy.SELLER): [],
            (Role.DOVE, Strategy.BUYER): [],
            (Role.DOVE, Strategy.STABLE): [],
            (Role.HAWK, Strategy.SELLER): [],
            (Role.HAWK, Strategy.BUYER): [],
            (Role.HAWK, Strategy.STABLE): [],
        }

        for t in range(0, mgn.get_current_moment()):
            for rs, records in trade_counts.items():
                records.append(0)

            for mg in mgn.microgrids:
                trade_counts[(mg.role[t], mg.strategy(t=t))][t] += 1

        values = list(trade_counts.values())

        axs.xaxis.set_major_locator(MultipleLocator(1))

        baseline = np.zeros(mgn.get_current_moment())
        for idx, ((role, strat), y) in enumerate(trade_counts.items()):
            y_next = y + baseline

            axs.stairs(y_next, baseline=baseline, fill=True, label=f"{role} {strat}")

            baseline += np.array(values[idx])

        axs.legend(loc='best')
        axs.set_title("Roles and strategies over time")
        axs.set_xlabel("Time")
        axs.set_ylabel("Amount of MGs")

    def charts_global_best_fitness(mgn:MicrogridNetwork, axs, t:int):

        if t >= mgn.get_current_moment() or t<0:
            raise Exception(f"Invalid moment {t}, valid range is 0 - {mgn.get_current_moment()}")

        best_fits = mgn.models_global_histories[t]

        for key, value in best_fits.items():
            axs.plot(value, label=key)

        axs.legend(loc='best')
        axs.set_xlabel("Epoch")
        axs.set_ylabel("Fitness")
        axs.set_title(f"Global best fitness at moment {t}")

    def charts_diveristy(mgn:MicrogridNetwork, axs, t:int):
        if t >= mgn.get_current_moment() or t<0:
            raise Exception(f"Invalid moment {t}, valid range is 0 - {mgn.get_current_moment()}")

        diversities = mgn.models_diversities[t]

        for key, value in diversities.items():
            axs.plot(value, label=key)

        axs.legend(loc='best')
        axs.set_xlabel("Epoch")
        axs.set_ylabel("Diversity")
        axs.set_title(f"Diversity at moment {t}")

    def chart_exploration_vs_exploitation(mgn: MicrogridNetwork, axs, t:int):
        if t >= mgn.get_current_moment() or t<0:
            raise Exception(f"Invalid moment {t}, valid range is 0 - {mgn.get_current_moment()}")

        explorations = mgn.models_exploration[t]
        exploitations = mgn.models_exploitation[t]

        for key, value in explorations.items():
            axs.plot(value, label=f"Exploration {key}")

            exploitations_value = exploitations[key]

            axs.plot(exploitations_value, label=f"Exploitation {key}")

        axs.set_title(f"Exploration vs Exploitation for various hyperparameters")
        axs.set_xlabel("Epoch")
        axs.legend(loc='best')

    def chart_final_fitness(mgn: MicrogridNetwork, axs, t:int):
        if t >= mgn.get_current_moment() or t<0:
            raise Exception(f"Invalid moment {t}, valid range is 0 - {mgn.get_current_moment()}")

    def chart_runtime(mgn: MicrogridNetwork, axs, t:int):
        if t >= mgn.get_current_moment() or t<0:
            raise Exception(f"Invalid moment {t}, valid range is 0 - {mgn.get_current_moment()}")

        mod_run = mgn.models_runtimes[t]
        models = list(mod_run.keys())
        runtimes = list(mod_run.values())

        axs.bar(models, runtimes, color='skyblue')

        axs.set_title(f'Runtimes at moment {t}')
        axs.set_ylabel("Time (s)")

    def generate_img_from_axs(axs: plt.Axes):
        fig = axs.get_figure()

        buf = io.BytesIO()

        fig.savefig(buf, format="png")
        buf.seek(0)

        img_bytes = buf.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_b64