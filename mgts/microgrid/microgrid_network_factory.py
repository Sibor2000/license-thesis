from mgts.microgrid import MicrogridFactory, MicrogridNetwork


class MicrogridNetworkFactory:
    def __init__(self):
        pass

    def create_from_file(
        path,
        microgrid_statcard="MG stats",
        microgrid_id_column="id",
        charge_efficiency_column="charge_efficiency",
        discharge_efficiency_column="discharge_efficiency",
        max_stored_energy_column="max_stored_energy",
        battery_lifetime_cycles_column="battery_lifetime_cycles",
        produced_energy_column="produce",
        consumed_energy_column="consume",
    ) -> MicrogridNetwork:
        mgf = MicrogridFactory(path=path)
        microgrids = mgf.create_from_file(
            microgrid_statcard=microgrid_statcard,
            microgrid_id_column=microgrid_id_column,
            charge_efficiency_column=charge_efficiency_column,
            discharge_efficiency_column=discharge_efficiency_column,
            max_stored_energy_column=max_stored_energy_column,
            battery_lifetime_cycles_column=battery_lifetime_cycles_column,
            produced_energy_column=produced_energy_column,
            consumed_energy_column=consumed_energy_column,
        )

        return MicrogridNetwork(microgrids=microgrids)
