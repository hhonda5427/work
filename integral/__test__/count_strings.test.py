import pandas as pd

# 各列ごとに指定された文字列の出現回数をカウントする関数を定義
def count_strings(column, strings_to_count):
    return column.apply(lambda x: x in strings_to_count).sum()



def test_count_strings():
    # テスト用データフレームを作成
    df = pd.DataFrame({
        'col1': ['休', '勤', '夏', '暇', '特', '休'],
        'col2': ['勤', '休', '休', '勤', '勤', '暇']
    })

    # col1列について、'休'と'暇'の出現回数をテスト
    assert count_strings(df['col1'], ['休', '暇']) == 2, count_strings(df['col1'], ['休', '暇'])
    
    # col2列について、'休'と'暇'の出現回数をテスト
    assert count_strings(df['col2'], ['休', '暇']) == 2, count_strings(df['col2'], ['休', '暇'])
    
    # 存在しない文字列を指定した場合のテスト
    assert count_strings(df['col1'], ['存在しない文字列']) == 0, count_strings(df['col1'], ['存在しない文字列'])

test_count_strings()
