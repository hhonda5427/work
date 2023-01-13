from dataclasses import dataclass
import datetime

"""
初めからデータをpandas DataFrameで持たないようにした理由
・読み込み時のvalidationが楽
・読み込み元データを保持しようと考えた　-> 後々元に戻す機能を実装する際に対応できるように
・個人で複数のDataFrameを持つことがある。なので管理しやすいようにした
"""


# @dataclass(slots=True)
class Person:

    # 個人の情報
    staffid: str
    name: str
    dept: str
    jobPerDay: dict[tuple[int, int, int, int], str]
    requestPerDay: dict[tuple[int, int, int, int], str]

    def __init__(self, staffid: str, name: str) -> None:
        self.staffid = staffid
        self.name = name
        self.jobPerDay = {}
        self.requestPerDay = {}
        self.dept = ""


# @dataclass(slots=True)
class Members:
    members: dict[int, Person]

    # 全職員で共通な情報
    # (year, month, day, dayofweek) のtupleにする
    date: datetime
    #                        [( 年,  月,  日, 曜日)]
    previous_month: list[tuple[int, int, int, int]]
    now_month: list[tuple[int, int, int, int]]
    next_month: list[tuple[int, int, int, int]]
    day_previous_next: list[tuple[int, int, int, int]]

    def __init__(self):
        self.members = {}
