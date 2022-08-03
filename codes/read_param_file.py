import json
import pandas as pd
from pprint import pprint


class SetAttrs:
    """set information about each atom as attribute"""
    def __init__(self, data: dict) -> None:
        self.set_attrs(data)

    def set_attrs(self, data: dict) -> None:
        df = pd.DataFrame.from_dict(data)
        print(df)
        for item in df['atoms']:
            print(item)



with open("param.json") as f:
    data = json.load(f)

for files in data['files']:
    s = SetAttrs(files)

    for atom in files['atoms']:
        if files['symb'] == "D":
            atom['type'] += 2