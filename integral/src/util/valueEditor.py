from typing import Callable


class EmptyError(Exception):
    pass


class ModelDataEditor():
    """
    modelに変更を反映させるもの
    クラスメンバで値の受け渡しをするようにしている
    """
    preValue: str
    callbackFunc: Callable

    @staticmethod
    def getPostValue() -> str:
        try:
            if ModelDataEditor.callbackFunc == None:
                raise AttributeError
            if ModelDataEditor.preValue == None:
                raise EmptyError
            
            return ModelDataEditor.callbackFunc()
        except AttributeError as ex:
            print(f'コールバック関数が設定されていません。\nテキスト編集のみ有効になります\nエラー詳細: {ex}')
            return ModelDataEditor.preValue
        except EmptyError as ex:
            print(f'Noneだったデータを""に置き換えました\n詳細: {ex}')
