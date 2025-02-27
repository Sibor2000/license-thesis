from mgts.microgrid import MicrogridFactory, MicrogridNetworkFactory
import pandas as pd

path = "./datasets/test.xlsx"
sheet_name="MG1 measurements"

mgn = MicrogridNetworkFactory.create_from_file(path=path)

mgn.step_time()
mgn.step_time()
mgn.step_time()
mgn.step_time()


print(mgn.microgrids[2].stored_energy)
print(mgn.desires)