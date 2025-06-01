from mgts.reader import Reader
from mgts.microgrid import Microgrid
import pandas as pd
from typing_extensions import List
from mgts.behavior import get_role_from_str


class MicrogridFactory:
    def __init__(self, path=None):
        self.path = path

        if path is not None:
            self.__reader = Reader(path)

    @staticmethod
    def create_from_dataframe(
        df: pd.DataFrame,
        microgrid_id=None,
        produced_energy_column="produce",
        consumed_energy_column="consume",
    ) -> Microgrid:

        produced = df[produced_energy_column].to_list()
        consumed = df[consumed_energy_column].to_list()

        return Microgrid(
            microgrid_id, produced_energy=produced, consumed_energy=consumed
        )

    def create_from_sheet(
        self,
        sheet_name: str,
        microgrid_id=None,
        produced_energy_column="produce",
        consumed_energy_column="consume",
    ) -> Microgrid:
        if self.path is None:
            raise Exception(
                "Microgrid factory: No default path (spreadsheet) specified."
            )

        df = self.__reader.read_sheet(sheet_name)

        if microgrid_id is None:
            microgrid_id = sheet_name

        return MicrogridFactory.create_from_dataframe(
            df,
            microgrid_id=microgrid_id,
            produced_energy_column=produced_energy_column,
            consumed_energy_column=consumed_energy_column,
        )

    def create_from_file(
        self,
        microgrid_statcard="MG stats",
        microgrid_id_column="id",
        charge_efficiency_column="charge_efficiency",
        discharge_efficiency_column="discharge_efficiency",
        initial_stored_energy_column="initial_stored_energy",
        battery_lifetime_cycles_column="battery_lifetime_cycles",
        max_stored_energy_column="max_stored_energy",
        produced_energy_column="produce",
        consumed_energy_column="consume",
    ) -> list[Microgrid]:
        sheets = pd.read_excel(self.path, sheet_name=None)
        statcard = pd.read_excel(self.path, sheet_name=microgrid_statcard)

        microgrids = []

        for _, row in statcard.iterrows():
            microgrid = self.create_from_sheet(
                row[microgrid_id_column],
                produced_energy_column=produced_energy_column,
                consumed_energy_column=consumed_energy_column,
            )
            microgrid.charge_efficiency = row[charge_efficiency_column]
            microgrid.discharge_efficiency = row[discharge_efficiency_column]
            microgrid.initial_stored_energy = row[initial_stored_energy_column]
            microgrid.max_stored_energy = row[max_stored_energy_column]
            microgrid.battery_lifetime_cycles = row[battery_lifetime_cycles_column]
            microgrids.append(microgrid)

        return microgrids

    def create_from_dict(simulation_dict) -> list[Microgrid]:
        microgrids_raw = simulation_dict["microgrids"]
        nr_of_mgs = simulation_dict["nrOfMicrogrids"]

        microgrids_raw = microgrids_raw[:nr_of_mgs]


        microgrids = []

        for microgrid_raw in microgrids_raw:
            microgrids.append(
                Microgrid(
                    microgrid_raw["id"],
                    max_stored_energy=microgrid_raw["maxStored"],
                    charge_efficiency=microgrid_raw["chargeEfficiency"],
                    discharge_efficiency=microgrid_raw["dischargeEfficiency"],
                    initial_stored_energy=microgrid_raw["initialStored"],
                    role=[get_role_from_str(microgrid_raw["initialRole"])],
                    produced_energy=microgrid_raw["production"],
                    consumed_energy=microgrid_raw["consumption"],
                    sell_threshold=simulation_dict["sellThreshold"],
                    buy_threshold=simulation_dict["buyThreshold"],
                    e_max_lines=simulation_dict["eMax"]
                )
            )

        return microgrids
