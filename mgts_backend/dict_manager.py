import pickle
import os

class DictSaveManager:
    def __init__(self, filename="simulations.pkl"):
        self.filename:str = filename
        self.data:dict[str,dict] = {"simulations":{}, "simulation_charts":{}}

        if os.path.exists(filename):
            self.load()
        else:
            self.save()

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self):
        with open(self.filename, 'rb') as f:
            self.data = pickle.load(f)

    def set(self, dict_name, key, value):
        self.data[dict_name][key]=value
        self.save()

    def get(self, dict_name, key):
        return self.data[dict_name].get(key)

    def get_dict(self, dict_name):
        return self.data[dict_name]