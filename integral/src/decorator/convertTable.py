
from pathlib import Path
from typing import Union
import pandas as pd

from settings.settings import LOG_PATH


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

    @staticmethod
    def name2Id(name:str) -> int:
        for key, value in ConvertTable.convertTable.items():
            if name == value:
                return int(key)
                
class Debugger:
    root = Path(LOG_PATH)

    @staticmethod
    def toCSV(func):
        def wrapper(*args, **kwargs):
            result:pd.DataFrame = func(*args, **kwargs)
            result.to_csv(Debugger.root / Path(func.__name__ + '.csv'))
            return result
        return wrapper      