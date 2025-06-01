import pandas as pd

class Reader:
    def __init__(self, path):
        self.path = path

    def read_sheet(self, sheet_name):
        return pd.read_excel(self.path, sheet_name=sheet_name)