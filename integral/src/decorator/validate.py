import logging

from database.member import Members


class damagedDataError(Exception):
    pass


class Validater(Members):
    # デコレータとして検証

    # データの欠損を検証
    # 汎用性がなく、いい書き方ではない
    @staticmethod
    def validJobPerDay(func, logger=False):
        def wrapper(*args, **kwargs):
            membersInfo: Members = func(*args, **kwargs)

            for person in membersInfo.members.values():
                for day in membersInfo.day_previous_next:
                    try:
                        person.jobPerDay[day]
                    except KeyError as _ex:
                        # データ穴埋め
                        person.jobPerDay[day] = None
                        if (logger):
                            print('欠損データはNoneで埋められました')
                            print(f'対象名: {person.name} 職員ID: {person.staffid}')
                            print(f'日時: {day}')

            return membersInfo
        return wrapper
