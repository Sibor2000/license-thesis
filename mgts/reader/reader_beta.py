import pandas as pd
from mgts.microgrid import Microgrid

path="./datasets/test.xlsx" #adjust path as needed
xls = pd.ExcelFile(path)

print(xls.sheet_names)

dfs = pd.read_excel(path, sheet_name=None)
for sheet, df in dfs.items():
    print(f"Sheet: {sheet}")
    print(df.head(5))

mg1_df = pd.read_excel(path, sheet_name="MG1 measurements")
print("---")
print(mg1_df["produce"].to_list())


mg = Microgrid(2)
