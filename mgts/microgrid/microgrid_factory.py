from mgts.reader import Reader
from mgts.microgrid import Microgrid
import pandas as pd

class MicrogridFactory:
    def __init__(self, path=None):
        self.path=path

        if path is not None:
            self.__reader = Reader(path)

    @staticmethod
    def create_from_dataframe(df:pd.DataFrame, microgrid_id=None, produced_energy_column="produce", consumed_energy_column="consume"):

        produced = df[produced_energy_column].to_list()
        consumed = df[consumed_energy_column].to_list()

        return Microgrid(microgrid_id, produced_energy=produced, consumed_energy=consumed)

    def create_from_sheet(self, sheet_name:str, microgrid_id=None, produced_energy_column="produce", consumed_energy_column="consume"):
        if self.path is None:
            raise Exception("Microgrid factory: No default path (spreadsheet) specified.")

        df = self.__reader.read_sheet(sheet_name)

        if microgrid_id is None:
            microgrid_id = sheet_name

        return MicrogridFactory.create_from_dataframe(df, microgrid_id=microgrid_id, produced_energy_column=produced_energy_column, consumed_energy_column=consumed_energy_column)

    def create_from_file(self, microgrid_statcard = "MG stats",microgrid_id_column="id", charge_efficiency_column = "charge_efficiency", discharge_efficiency_column = "discharge_efficiency", produced_energy_column="produce", consumed_energy_column="consume"):
        sheets = pd.read_excel(self.path, sheet_name=None)
        statcard = pd.read_excel(self.path, sheet_name=microgrid_statcard)

        microgrids = []

        for _, row in statcard.iterrows():
            microgrid = self.create_from_sheet(row[microgrid_id_column], produced_energy_column=produced_energy_column, consumed_energy_column=consumed_energy_column)
            microgrid.charge_efficiency = row[charge_efficiency_column]
            microgrid.discharge_efficiency = row[discharge_efficiency_column]

            #print(row)
            microgrids.append(microgrid)

        return microgrids





