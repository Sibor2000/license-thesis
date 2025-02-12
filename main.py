from mgts.microgrid import MicrogridFactory
import pandas as pd

path = "./datasets/test.xlsx"
sheet_name="MG1 measurements"

mgf = MicrogridFactory(path=path)

microgrids = mgf.create_from_file()

for microgrid in microgrids:
    print(microgrid.id)
    print(microgrid.charge_efficiency)
    print(microgrid.produced_energy)