
from enum import Enum 
# dataFrame要素のEnum
class ShiftElement(Enum):
    # 休み
    HOLIDAY = '休'
    # 暇
    FREE = '暇'
    # 夏休み
    SUMMER_HOLIDAY = '夏'
    # 特別休暇
    SPECIAL_HOLIDAY = '特'
    # 勤務
    WORK = '勤'
    # 夜勤明け
    NIGHT_WORK_NEXT = '明'
    # F日
    F_DAY = 'F日'
    # C日
    C_DAY = 'C日'
    # A日
    A_DAY = 'A日'
    # M日
    M_DAY = 'M日'
    # C夜
    C_NIGHT = 'C夜'
    # A夜
    A_NIGHT = 'A夜'
    # M夜
    M_NIGHT = 'M夜'
    # 未入力
    NONE = None
    


#def count_func_con(data,row,iota):
#    #・・・連続勤務日数の計算・・・
    
#    #結果格納リスト

    
#    data3 = data.iloc[row,:]#変更された行のみ取得

    
#    #行列の長さの取得
#    columss=len(data3)
#    tail=columss-1#変更された行の今月分のみ取得
    
    

#    mwork = count_consecutive_workdays(data, row, columss)
    
#    print(mwork)
#    data4 = data.iloc[row,iota:tail]#今月分データ
#    kin=(data4=='勤').sum()
#    kyu=(data4=='休').sum()
#    ka=(data4=='暇').sum()
#    ake=(data4=='明').sum()
#    fni=(data4=='F日').sum()
#    cni=(data4=='C日').sum()
#    ani=(data4=='A日').sum()
#    mni=(data4=='M日').sum()
#    cya=(data4=='C夜').sum()
#    aya=(data4=='A夜').sum()
#    mya=(data4=='M夜').sum()
#    kin2=(data4==None).sum()
#    #各項目の計算
#    hd=kyu
#    hd_2=ka
#    return mwork, hd

# def mwork_func(data, row, columss, isConstruct = False):
#     cwork=0#加算用変数

#     l=[]#格納リスト

#     for i in range(columss):
#         zzz=data.iloc[row,i]
        
#         if zzz=='休':
#             l.append(cwork)
#             cwork=0
#         elif zzz=='暇':
#             l.append(cwork)
#             cwork=0
#         elif zzz=='夏':
#             l.append(cwork)
#             cwork=0
#         elif zzz=='特':
#             l.append(cwork)
#             cwork=0
#         else :
#             cwork+=1
#     l.append(cwork)
#     cwork=0
#     mwork=max(l)

#     return mwork

#上記の関数を簡略化し、可読性を上げたもの


def count_consecutive_workdays(data, row, columns):
    max_consecutive = 0
    current_consecutive = 0

    for i in range(columns):
        value = data.iloc[row, i]
        
        if value in ['休', '暇', '夏', '特','年']:
            max_consecutive = max(max_consecutive, current_consecutive)
            current_consecutive = 0
        else:
            current_consecutive += 1
            
    max_consecutive = max(max_consecutive, current_consecutive)

    return max_consecutive




# ある１行のデータから、指定した文字列リストの最大連続出現回数を計算する関数を定義
def count_consecutive_column(column, want_to_countList: list[ShiftElement]):
    max_consecutive = 0
    current_consecutive = 0

    unique_elements = set([element.value for element in want_to_countList])

    # print(f'column: {column}')
    for value in column:
        if value in unique_elements:
            current_consecutive += 1
            # print(f'current_consecutive: {current_consecutive}')
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0

    return max_consecutive


# 各列ごとに指定された文字列の出現回数をカウントする関数を定義
def count_strings(column, strings_to_count):
    return column.apply(lambda x: x in strings_to_count).sum()


# つかいかた    
# 各列ごとに指定された文字列の合計数を計算し、結果を表示
# result = df.apply(count_strings, strings_to_count=strings_to_count)
# print(result)


# def countfunc_col(data,colmun):

#     data6 = data.iloc[:,colmun]

#     data5=data6.T
#     kyu=(data5=='休').sum()
    
#     return kyu

# 上記の関数を簡略化
# ’休’の出現回数をカウントする関数を定義
def countfunc_col(data, column_index):
    return (data.iloc[:, column_index] == '休').sum()
#　変更があった行のデータをカウントする関数を定義
def count_this_row(data,changedRow,iota, want_to_count: ShiftElement):    
    #変更された行
    changedColumn = data.iloc[changedRow, :]
    #今月分データ
    nowMonthColumn = changedColumn[iota: len(changedColumn) -1]

    #最大連続勤務日数をカウント
    workList = [
        ShiftElement.WORK,
        ShiftElement.A_DAY,
        ShiftElement.C_DAY, 
        ShiftElement.M_DAY, 
        ShiftElement.F_DAY, 
        ShiftElement.A_NIGHT, 
        ShiftElement.C_NIGHT, 
        ShiftElement.M_NIGHT,
        ShiftElement.NONE,
        ShiftElement.NIGHT_WORK_NEXT
        ]
    max_consective_workdays = count_consecutive_column(nowMonthColumn, workList) 

    # print(f'最大連続勤務日数:{max_consective_workdays}')

    #数えたい文字列の出現回数をカウント
    wanted_count = count_strings(nowMonthColumn, [want_to_count.value])
    

    return max_consective_workdays, wanted_count

