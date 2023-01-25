
from typing import Union
import pandas as pd


class ConvertTable:

    convertTable: dict[Union[int, str], str] = {}

    @staticmethod
    def id2Name(func):
        def wrapper(*args, **kwargs):
            dataFrame: pd.DataFrame = func(*args, **kwargs)
            for key, value in ConvertTable.convertTable.items():
                # UnionTypeで扱っていれば一行でかけるんだけどな...
                dataFrame.replace(int(key), value, inplace=True)
                dataFrame.replace(str(key), value, inplace=True)

            return dataFrame
        return wrapper

    # @staticmethod
    # def name2Id(name:str):
        