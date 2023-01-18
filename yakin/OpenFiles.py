import datetime
import pandas as pd
import math

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
def config():#勤務表作成における必要変数を格納
    #ShiftManager ⇒　20221220/sample1
    # fti = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/configvar.dat")
    fti = pd.read_table(r'C:\Users\honda\radschedule\data\configvar.dat')
    # print(fti)
    #基準日
    sd = fti.columns.values  #sdにdateを入れる
    
    sd = sd[0]               #配列からdateを取り出す
    
    sd = sd[-10:]            #date，2023/04/01から日付だけを取り出す
    
    sd = datetime.datetime.strptime(sd,'%Y/%m/%d')  #文字列をdate型に変換
    
    rk = fti.iloc[1, :].values  #iota(連続勤務日数)を取り出しrkに入れる
    # print(rk)
    rk = rk[0]                  #配列からiotaを取り出す
    rk = rk[-2:]                #iotaを取り除く
    kn = fti.iloc[2, :].values  #myuを取り出しknに入れる
    # print(kn)
    kn = kn[0]                  #配列からmyuを取り出す
    kn = kn[4:]                 #myuを取り除く
    return sd, rk , kn  # 基準日(yyyy/mm/dd),連続勤務，休日数

def beta(): #各モダリティにおける最低限必要な正規スタッフ人数を格納、各行がそれぞれのモダリティ，2列目移行に1日から月末までの最低限必要な正規スタッフ人数を記載
    # DFbeta = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/beta.dat", sep=',',header=None)
    DFbeta = pd.read_table(r"C:\Users\honda\radschedule\data\beta.dat", sep=',',header=None)
    return DFbeta

def gamma() :#各モダリティにおける責任者クラスの必要人数を格納各行がそれぞれのモダリティ，2列目移行に1日から月末までの最低限必要な責任者クラスの人数を記載
    # DFgamma = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/gamma.dat", sep=',',header=None)
    DFgamma = pd.read_table(r"C:\Users\honda\radschedule\data\gamma.dat", sep=',',header=None)
    return DFgamma

def Nrdeptcore():#スケジュールの対象となるスタッフUIDとその所属モダリティ，各モダリティスキルを格納。
    #0=X,1=△,2=〇,3=▲,4=●,5=★,6=◎
    # DFNrdeptcore = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/Nrdeptcore.dat", sep=',', header=None)
    DFNrdeptcore = pd.read_table(r"C:\Users\honda\radschedule\data\Nrdeptcore.dat", sep=',', header=None)
    
    DFNrdeptcore.columns = ["UID", "Mo", "RT", "MR", "TV", "KS", "NM", "XP", "CT", "XO", "AG", "MG", "MT"]
    # DFNrdeptcore.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFNrdeptcore.csv")
    RawDFNrdeptcore = DFNrdeptcore
    DFNrdeptcore = DFNrdeptcore[["UID","Mo"]]
    return DFNrdeptcore,RawDFNrdeptcore

def stuff():
    #スタッフ
    # dfstaff = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/staffinfo.dat", sep=',', header=None)
    dfstaff = pd.read_table(r'C:\Users\honda\radschedule\data\staffinfo.dat', sep=',', header=None)
    dfstaff.columns = ["No", "ID", "Name"]
    
    #人数数え
    number_of_stuff = len(dfstaff)
    staff_list = dfstaff["No"].to_list()        #UIDのリストを取得
    
    # スタッフ数，UIDリスト，[UID, ID, Name]のリスト
    return number_of_stuff, staff_list, dfstaff

def converttable ():
    # dfconverttable = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/converttable.dat", sep=',', header=None)
    dfconverttable = pd.read_table(r"C:\Users\honda\radschedule\data\converttable.dat", sep=',', header=None)
    dfconverttable.columns = ["Job", "No"]
    return dfconverttable

def shift():
    #シフト
    # input_data = open("C:/Users/pelu0/Desktop/20221220/sample1/shift.dat", 'r')
    input_data = open(r'C:\Users\honda\radschedule\data\shift.dat', 'r')
    # dfshift = pd.read_csv(r'C:\Users\honda\radschedule\data\shift.dat', header=)
    b = []
    # 一行ずつ読み込んでは表示する
    for rows in input_data:
        # コメントアウト部分を省く処理
        # if rows[0] == '#':
        if rows[0] == '"':
            s = rows
            continue
        # 値を変数に格納する
        row = rows.rstrip('\n').split(',')
        month = [int(i) for i in row]
        b.append(month)
    # print(b) #honda   
    # ファイルを閉じる
    dfshift = pd.DataFrame(b)
    dfshift.columns = ["UID", "Date", "Job"]
    input_data.close()
    # print(dfshift)
    ed = dfshift['Date'].max()      #月末を取得
    # print(ed)     #honda
    #夜勤表
    #シフトから日直・夜勤の抽出  4=A夜勤　5=M夜勤　6=C夜勤　0=A日　1=M日　2=C日　3=F日 30=NF
    # 
    dfnightshift = dfshift[(dfshift["Job"] == 4) | (dfshift["Job"] == 5) | (dfshift["Job"] == 6) | (dfshift["Job"] == 0) | (dfshift["Job"] == 1) | (dfshift["Job"] == 2) | (dfshift["Job"] == 3) | (dfshift["Job"] == 30)]
    # print(dfnightshift)
    # dfnightshift から重複しないようにdate（ここでは基準日が0となっている）だけをリストとして取得
    data_list = dfshift.drop_duplicates(subset="Date")["Date"].tolist() 
   
    cols = [4, 5, 6, 0, 1, 2, 3, 30]
    # indexを日付（ここでは基準日を0）として，カラムをそれぞれの勤務となる空(NAN)のデータフレームを用意
    DFyakinhyou = pd.DataFrame(index=data_list, columns=cols)
    # print(DFyakinhyou)
    # 抽出した日勤夜勤データをレコード数でループ
    for i in range(len(dfnightshift)):
        # 抽出したレコードを日付，勤務，氏名の変数に入れる
        day = dfnightshift.iat[i, 1]
        job = dfnightshift.iat[i, 2]
        name = dfnightshift.iat[i, 0]
        #作成した空の夜勤表で行名＝日付と列名＝勤務の値が'nan'か判定する
        if math.isnan(DFyakinhyou.at[day, job]):
            #データがNANであれば夜勤表に氏名を入れる
            DFyakinhyou.at[day, job] = name
        elif not math.isnan(DFyakinhyou.at[day, job]) and job == 3:
            #データがNANでなければ　⇒　既に1人目のF日が埋まっていたならば，右隣の配列に入れる
            DFyakinhyou.at[day, 30] = name
    # DFyakinhyou.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFyakinhyou.csv")
    # 夜勤表のカラム名を変更する
    DFyakinhyou.columns = ["Angio夜勤", "MRI夜勤", "CT夜勤", "Angio日勤", "MRI日勤", "CT日勤", "Free日勤", "Free日勤"]
    # 基準日(yyyy/mm/dd),連続勤務，休日数を取得する
    sd, rk , kn= config()
    # index名を変更するために日時の連続値を生成する
    dates = pd.date_range(sd, periods=ed + 1, freq='D').strftime('%m/%d')
    # index名を変換する
    DFyakinhyou.index = dates
    
    #名前に変換
    number_of_stuff, staff_list, dfstaff = stuff()
    # 全てのUIDリストをループしてDFyakinhyoのUIDをNameに変換する
    for j in range(number_of_stuff):

        DFyakinhyou = DFyakinhyou.replace(dfstaff.iat[j, 0], dfstaff.iat[j, 2])
    # DFyakinhyou.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFyakinhyouname.csv", encoding='Shift_JIS')
    
    # ed = 月末 , dfshift = [UID, date, shift] , DFyakinhyou = 夜勤表 , data_list = 基準日を0とした日付のリスト
    return ed, dfshift, DFyakinhyou, data_list

#リクエスト
def request():
    # dfrequest = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/request.dat", sep=',', header=None)
    dfrequest = pd.read_table(r"C:\Users\honda\radschedule\data\request.dat", sep=',', header=None)
    dfrequest.columns = ["UID", "Date", "Job"]
    return dfrequest

#先月データ
def previous():
    #先月データ
    # dfprevious = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/previous.dat", sep=',', header=None)
    dfprevious = pd.read_table(r"C:\Users\honda\radschedule\data\previous.dat", sep=',', header=None)
    dfprevious.columns = ["UID", "Date", "Job"]
    # dfprevious.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/dfprevious.csv")
    return dfprevious

def kinmuhyou():
    dfrequest = request()    #リクエスト　["UID", "Date", "Job"]
    '''
    ed = 月末 , dfshift = [UID, date, shift] , 
    DFyakinhyou = 夜勤表 , data_list = 基準日を0とした日付のリスト
    '''
    ed, dfshift, DFyakinhyou, data_list = shift()    #夜勤

    dfprevious = previous() # 先月データ　["UID", "Date", "Job"]
    sd, rk, kn = config()   # 基準日(yyyy/mm/dd), 連続勤務，休日数
    dfconverttable = converttable() # ["Job", "No"]

    #先月＋今月のデータを結合
    dfprevious_dfshift = pd.concat([dfprevious, dfshift])
    # print('non')
    # print(dfprevious_dfshift)
    # 重複した行を削除
    longday = dfprevious_dfshift.loc[:, ['Date']].drop_duplicates().dropna(subset=['Date'])
    # print(dfprevious_dfshift)
    '''日付（数値）のリスト'''
    longday = longday["Date"].to_list()     # 前月分を含めた日付のリストを取得する
    # print(longday)

    # 基準日から日付計算
    for i in range(len(dfprevious_dfshift)):
        # 数値の状態の日付を取得
        IntVar = dfprevious_dfshift.iat[i, 1]
        # sd（基準日）に対して数値に応じた日数を加算する
        dfprevious_dfshift.iat[i, 1] = sd + datetime.timedelta(days=1) * IntVar
        # 日付を文字列に変換する
        dfprevious_dfshift.iat[i, 1] = dfprevious_dfshift.iat[i, 1].strftime('%m/%d')
    
    # 列名(日付)日付ダブり削除＋Nan削除
    '''日付のリスト'''
    list_cols = dfprevious_dfshift.loc[:, ['Date']].drop_duplicates().dropna(subset=['Date'])
    list_cols = list_cols["Date"].to_list()
    # print(list_cols)
    # DataFrame(先月+今月)
    number_of_stuff, staff_list, dfstaff = stuff()      # スタッフ数，UIDリスト，[UID, ID, Name]のリスト
    # index=UIDとカラム=日付を設定した空のデータフレームを用意する
    DFkinmuhyou_long = pd.DataFrame(index = staff_list, columns = list_cols)

    # dfprevious_dfshiftの'Job'列の値をdfconverttableに応じて変換する
    for i in range(len(dfconverttable)):
        dfprevious_dfshift = dfprevious_dfshift.replace({'Job': {dfconverttable.iat[i, 1]: dfconverttable.iat[i, 0]}})

    # 値代入
    # dfprevious_dfshiftの各値に応じて，DFkinmuhyo_longを作成する
    for i in range(len(dfprevious_dfshift)):
        a = dfprevious_dfshift.iat[i, 0]
        b = dfprevious_dfshift.iat[i, 1]
        c = dfprevious_dfshift.iat[i, 2]
        DFkinmuhyou_long.at[a, b] = c

    # DFkinmuhyou_longのindex(Name)をUIDから氏名に変換する
    list_row1 = dfstaff["Name"].to_list()
    # ダミーを追加してindexを作成する
    list_row1.extend([900, 901, 902, 903, 904, 905, 906, 907, 908, 909])
    DFkinmuhyou_long.index = list_row1
    # DFkinmuhyou_long.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFkinmuhyou_long.csv", encoding='Shift_JIS')
    
    # print(DFkinmuhyou_long)
    #DFkinmuhyou_long = DFkinmuhyou_long.replace({0: "A日", 1: "M日", 2: "C日", 3: "F日", 4: "A夜", 5: "M夜", 6: "C夜", 7: "明", 8: "日勤", 9: "他勤"})
    #DFkinmuhyou_long = DFkinmuhyou_long.replace({10: "休日", 11: "休暇", 12: "ダ"})

    #今月(夜勤のみ)+リクエスト
    #夜勤以外を空に
    for i in range(len(dfshift)):
        if dfshift.iat[i, 2] > 7:
            dfshift.iat[i, 2] = ""
    #DataFrame今月(夜勤のみ)+リクエスト
    dfkinmuhyou = pd.concat([dfprevious, dfshift, dfrequest])
    # print(dfkinmuhyou)
    #基準日から日付計算
    for i in range(len(dfkinmuhyou)):
        IntVar = dfkinmuhyou.iat[i, 1]
        dfkinmuhyou.iat[i, 1] = sd + datetime.timedelta(days=1)*IntVar
        dfkinmuhyou.iat[i, 1] = dfkinmuhyou.iat[i, 1].strftime('%m/%d')
    #DataFrame
    number_of_stuff, staff_list, dfstaff = stuff()
    
    print(staff_list)
    # print(dfkinmuhyou)
    DFkinmuhyou = pd.DataFrame(index=staff_list, columns=list_cols)

    for i in range(len(dfconverttable)):
        dfkinmuhyou= dfkinmuhyou.replace({'Job': {dfconverttable.iat[i, 1]: dfconverttable.iat[i, 0]}})

    #値代入
    for i in range(len(dfkinmuhyou)):
        a = dfkinmuhyou.iat[i, 0]
        b = dfkinmuhyou.iat[i, 1]
        c = dfkinmuhyou.iat[i, 2]
        DFkinmuhyou.at[a, b] = c

    DFkinmuhyou.index = list_row1
    # DFkinmuhyou.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFkinmuhyou.csv", encoding='Shift_JIS')
    print(DFkinmuhyou)
    #DFkinmuhyou = DFkinmuhyou.replace({0: "A日", 1: "M日", 2: "C日", 3: "F日", 4: "A夜", 5: "M夜", 6: "C夜", 7: "明", 8: "日勤", 9: "他勤"})
    #DFkinmuhyou = DFkinmuhyou.replace({10: "休日", 11: "休暇", 12: "ダ"} )

    # DFkinmuhyou.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFkinmuhyouname.csv", encoding='Shift_JIS')
    
     #DFkinmuhyou:今月のリクエスト＋夜勤 DFkinmuhyou_long:先月からのシフト連続勤務計算
    
    return DFkinmuhyou, DFkinmuhyou_long, longday 

def Skill():
    # dfskill = pd.read_table("C:/Users/pelu0/Desktop/20221220/sample1/Skill.dat", sep=',', header=None)
    dfskill = pd.read_table(r"C:\Users\honda\radschedule\data\skill.dat", sep=',', header=None)
    dfskill.columns = ["UID", "A夜", "M夜", "C夜", "F日", "夜勤", "日直"]
    dfskill = dfskill.sort_values("UID", ascending=True)
    ed, dfshift, DFyakinhyou, data_list = shift()
    DFkinmuhyou, DFkinmuhyou_long, longday = kinmuhyou()
    dfprevious = previous()
    number_of_stuff, staff_list, dfstaff = stuff()

    #勤務日を1に置き換える
    dfjob1 = pd.concat([dfprevious, dfshift])
    
    # 日勤：８までを１に置き換え　⇒　さらに0以上を１に置き換え
    # それ以外を０に置き換え    　⇒　０は’　’に置き換え
    dfjob1 = dfjob1.replace({"Job" : {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1}})
    dfjob1 = dfjob1.replace({"Job" : {10: 0, 11: 0, 12: 0,  50: 0, 60: 0, 61: 0, 63: 0}})

    dfjob1.loc[dfjob1["Job"] > 0, "Job"] = 1
    dfjob1.loc[dfjob1["Job"] == 0, "Job"] = ""
    
    # 勤務は１，それ以外はNoneのデータフレームを作成
    DFrenzoku = pd.DataFrame(index=staff_list, columns=longday)
    for i in range(len(dfjob1)):
        a = dfjob1.iat[i, 0]
        b = dfjob1.iat[i, 1]
        c = dfjob1.iat[i, 2]
        DFrenzoku.at[a, b] = c
    # DFrenzoku.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFrenzoku.csv", encoding='Shift_JIS')
    '''
    dfskill = ["UID", "A夜", "M夜", "C夜", "F日", "夜勤", "日直"]のレコード
    dfjob1 = [UID, Date, Job] 勤務が1, それ以外はNoneとなっている
    DFrenzoku =  dfjob1を勤務表形式に変化したtable
    '''
    return dfskill, dfjob1, DFrenzoku


def main():
    # a, b, c = config()
    # ed, dfshift, DFyakinhyou, data_list = shift()
    # dfskill, dfjob1, DFrenzoku = Skill()
    DFkinmuhyou, DFkinmuhyou_long, longday = kinmuhyou()
    # DFNrdeptcore,RawDFNrdeptcore = Nrdeptcore()
    # print(RawDFNrdeptcore)
        # 各モダリティのコアメンバー抽出
    # DFRTCore = RawDFNrdeptcore.query('RT== 6 ')
    # DFMRCore = RawDFNrdeptcore.query('MR== 6 ')
    # DFTVCore = RawDFNrdeptcore.query('TV== 6 ')
    # DFKSCore = RawDFNrdeptcore.query('KS== 6 ')
    # DFNMCore = RawDFNrdeptcore.query('NM== 6 ')
    # DFXPCore = RawDFNrdeptcore.query('XP== 6 ')
    # DFCTCore = RawDFNrdeptcore.query('CT== 6 ')
    # DFXOCore = RawDFNrdeptcore.query('XO== 6 ')
    # DFAGCore = RawDFNrdeptcore.query('AG== 6 ')
    # DFMGCore = RawDFNrdeptcore.query('MG== 6 ')
    # DFMTCore = RawDFNrdeptcore.query('MT== 6 ')
    # print(DFRTCore)
    # print(longday)
if __name__ == '__main__':
    main()