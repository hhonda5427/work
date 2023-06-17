import os
import csv
import pulp
import datetime
import readdata as rd
import tokaifunc as tfunc
import config
import time

def calc_schedule():

    
    # 変数
    # N = Nr + Ndummy 
    # Nr：スケジュールの対象となる技師の集合
    # Ndaily：休日勤が可能な技師集合　Nnight：夜勤が可能な技師集合　Nboth：どちらかできる技師の集合
    # Ns：各休日勤・夜勤が可能な技師集合
    staff = {}
    N = []; Nr = []; Ndum = []; Ndaily = []; Nnight = []; Nboth = []; Ns = []

    # G：モダリティグループに属する技師集合
    # Core：モダリティリーダーを任せることのできる技師集合
    # G = 0:MR, 1:TV, 2:HT, 3:MN, 4:XA, 5:RT, 6:XP, 7:CT, 8:XO, 9:etc
    G = []; Core = []

    # T：日にちの集合（前月13日分と次月1日分を含む）
    # Tr：スケジュールの対象となる日にちの集合
    # Topened：診療日となる日にちの集合
    # Tclosed：休診日となる日にちの集合
    Tdict = {}
    T = []; Tr = []; Tclosed = []; Topened = []

    # 勤務の種類
    # W1 = ['A日', 'M日', 'C日', 'F日', 'A夜', 'M夜', 'C夜', '明', '日勤', '他勤', '休日', '休暇']
    # 0:A日->dA, 1:M日->dM, 2:C日->dC, 3:F日->dF, 
    # 4:A夜->nA, 5:M夜->nM, 6:C夜->nC, 7:明 ->n,
    # 8:日勤->'', 9:他勤->e, 10:休日->/, 12:休暇->#
    # 初回作成時の明けなし宿直に関しては明けをつけなくても大丈夫。夜勤・明けの制約は作成月のみ
    Wdict = {'A日':'dA', 'M日':'dM', 'C日':'dC', 'F日':'dF', 'A夜':'nA', 'M夜':'nM', 'C夜':'nC', '明':'nn',
            'A宿':'nA', 'M宿':'nM', 'C宿':'nC',
            '日':'dW', '勤':'dW', '援':'eW', '張':'eW', 
            'RT':'dW','MR':'dW','TV':'dW','KS':'dW','NM':'dW', 'AG':'dW','XP':'dW',
            'MG':'dW','MT':'dW','CT':'dW','XO':'dW','FR':'dW','NF':'dW','AS':'dW','ET':'dW','半':'dW',
            '休':'do', '振':'do', '年':'ho','夏':'ho', '特':'ho',
            '例外':'Ex'}
    W1 = ['dA', 'dM', 'dC', 'dF', 'nA', 'nM', 'nC', 'nn', 'dW', 'eW', 'do', 'ho']
    W2 = ['Ex']
    W = W1 + W2

    # 禁止シフトの集合
    Q = ['n','n','n']

    # 日付ごとの制約条件変数
    # alpha[work][date]
    # alpha 0:A日,1:M日,2:C日,3:F日,4:A夜,5:M夜,6:C夜,7:明,8:日勤,9:他勤,10:休日,11:休暇
    # beta[modality][date]
    # beta 0:MR, 1:TV, 2:HT, 3:MN, 4:XA, 5:RT, 6:XP, 7:CT, 8:XO, 9:MG, 10:MT, 11:FR/NF
    # gamma[modality][date]
    # gamma 0:MR, 1:TV, 2:HT, 3:MN, 4:XA, 5:RT, 6:XP, 7:CT, 8:XO, 9:MG, 10:MT, 11:FR/NF
    alpha = []; beta = []; gamma = []

    # 前月分の勤務
    Fprev = []; Fp = []
    # 今月分の勤務希望
    Frequ = []; Fr = []

    staff = rd.read_staff_info()

    Ndum = tfunc.make_Ndum(10)

    Nr, G, Core = rd.read_Nr_Gm_Core(Ndum)
    Nnight, Ndaily, Ns = rd.read_skill(Ndum)        #Nnight,Ndailyにはdummyはいない。
    Nboth = list(set(Nnight) | set(Ndaily))

    N = Nr + Ndum

    alpha = rd.read_alpha()
    beta = rd.read_beta()
    gamma = rd.read_gamma()

    # createDate:作成日時 epsilon:夜勤日勤回数の上限 iota:連続勤務日数 kappa:所定労働時間
    # myu:休日数 nyu1,2,3:連休数 rho:休日数の下限 lam:勤務間隔の荷重係数
    createDate, epsilon, iota, kappa, myu, nyu, rho, lam, calctime = rd.read_config_var()
    
    twoConsecutiveHolidays = nyu[0] + nyu[1]*2 + nyu[2]*3
    threeConsecutiveHolidays = nyu[1] + nyu[2]*1
    fourConsecutiveHolidays = nyu[2]

    # 夜勤・休日日勤平均回数
    meanWorks = tfunc.calc_mean_of_night_and_daily(alpha, len(Ndaily), len(Nnight))

    Tdict, T, Tr, Tclosed, Topened, Toutput = tfunc.make_T(createDate, iota)

    Fprev = rd.read_previous(createDate)
    Frequ = rd.read_request(createDate)

    Fp = tfunc.reformat_F(Fprev, Wdict, Tdict)
    Fr = tfunc.reformat_F(Frequ, Wdict, Tdict)

    # 
    # 最小化問題を記述
    model = pulp.LpProblem(sense=pulp.LpMinimize)

    # 変数
    # x[i, j, k] 技師iがj日の勤務kであるかどうか
    x = pulp.LpVariable.dicts('x', [(n, t, w) for n in N for t in T for w in W], cat='Binary')
    # 勤務間隔変数
    i1 = pulp.LpVariable.dicts('i1', [(n, t) for n in Nboth for t in Tr], cat='Binary')
    i2 = pulp.LpVariable.dicts('i2', [(n, t) for n in Nboth for t in Tr], cat='Binary')
    i3 = pulp.LpVariable.dicts('i3', [(n, t) for n in Nboth for t in Tr], cat='Binary')
    i4 = pulp.LpVariable.dicts('i4', [(n, t) for n in Nboth for t in Tr], cat='Binary')
    # i5 = pulp.LpVariable.dicts('i5', [(n, t) for n in Nr for t in Tr], cat='Binary')
    # 各技師の合計夜勤・休日日勤回数
    s = pulp.LpVariable.dicts('s', [(n) for n in Nboth], cat='Integer')
    # 各技師の合計夜勤・休日日勤回数の平均偏差
    d = pulp.LpVariable.dicts('d', [(n) for n in Nboth], lowBound=0, cat='Continuous')
    # 連休変数''
    h2 = pulp.LpVariable.dicts('h2', [(n, t) for n in Nboth for t in Tr[:-1]], cat='Binary')
    h3 = pulp.LpVariable.dicts('h3', [(n, t) for n in Nboth for t in Tr[:-2]], cat='Binary')
    h4 = pulp.LpVariable.dicts('h4', [(n, t) for n in Nboth for t in Tr[:-3]], cat='Binary')

    # 目的関数（soft constraints）・・・
    model += pulp.lpSum([x[n, t, w] for n in Ndum for t in Tr for w in W1]) \
        + lam[0] * pulp.lpSum([i1[n, t] for n in Nboth for t in Tr]) \
        + lam[1] * pulp.lpSum([i2[n, t] for n in Nboth for t in Tr]) \
        + lam[2] * pulp.lpSum([i3[n, t] for n in Nboth for t in Tr]) \
        + lam[3] * pulp.lpSum([i4[n, t] for n in Nboth for t in Tr]) \
        + lam[4] * pulp.lpSum([d[n] for n in Nboth])
        # + pulp.lpSum([x[n, t, W2[0]] for n in Nr for t in Tr]) \
    # 制約条件（hard constraints）
    # 日にちtにおいて技師nに勤務wを必ず割り当てる・・・(5)
    for n in N:
        for t in Tr:
            model += pulp.lpSum([x[n, t, w] for w in W]) == 1

    # 日にちtにおける勤務wの必要人数を合わせる
    # W1 0:A日, 1:M日, 2:C日, 3:F日, 4:A夜, 5:M夜, 6:C夜, 7:明, 8:日, 9:他勤, 10:休日, 11:休暇
    # W1 = ['dA', 'dM', 'dC', 'dF', 'nA', 'nM', 'nC', 'nn', 'dW', 'eW', 'do', 'ho']
    # alpha 0:A日,1:M日,2:C日,3:F日,4:A夜,5:M夜,6:C夜,7:明,8:日勤,9:他勤,10:休日,11:休暇
    # beta
    # gamma
    i = 0
    for t in Tr:
        
        if t in Topened:
        
            # 診療日の日勤を設定人数以上で確保する・・・(6)
            model += pulp.lpSum([x[n, t, 'dW'] for n in N]) >= alpha[8][i]
            # 診療日の休日人数を設定人数以下で確保する・・・(9)
            model += pulp.lpSum([x[n, t, 'do'] for n in N]) <= alpha[10][i]
            
            for m in range(len(G)-1):
                # 正規スタッフ数を設定人数以上で確保・・・(11)
                model += pulp.lpSum([x[n, t, 'dW'] for n in G[m]]) >= beta[m][i]
                # 責任者クラスを設定人数以上で確保・・・(12)
                model += pulp.lpSum([x[n, t, 'dW'] for n in Core[m]]) >= gamma[m][i]
        else:
            # 休診日の日勤は設定人数分を確保する・・・(7)
            model += pulp.lpSum([x[n, t, 'dW'] for n in N]) == alpha[8][i]
            # 休診日の休日人数を設定人数以上で確保する・・・(10)
            model += pulp.lpSum([x[n, t, 'do'] for n in N]) >= alpha[10][i]

        # 各夜勤・休日勤の人数を確保する
        for w in W[:7]:
            # スタッフ全員に対して人数を確保する・・・(8)
            model += pulp.lpSum([x[n, t, w] for n in N]) == alpha[W.index(w)][i]
            # 対応可能なスタッフに各勤務を割り当てる・・・(13)(15)
            model += pulp.lpSum([x[n, t, w] for n in Ns[W.index(w)]]) == alpha[W.index(w)][i]
        # 明けの人数を確保する・・・(8)
        model += pulp.lpSum([x[n, t, 'nn'] for n in N]) == alpha[7][i]
        # 休暇の人数を確保する
        model += pulp.lpSum([x[n, t, 'ho'] for n in N]) == alpha[11][i]
        # 他勤の人数を確保する
        model += pulp.lpSum([x[n, t, 'eW'] for n in N]) == alpha[9][i]
        i += 1

    for n in N:
        for t in Tr:
            # 夜勤の翌日は明けにする・・・(14)
            model += pulp.lpSum([x[n, t, w] for w in W[4:7]]) == x[n, (t+1), W[7]]

    for n, t, w in Fp:
        # 前月分の勤務を入力
        model += x[n, t, w] == 1
    
    for n, t, w in Fr:    
        # 勤務希望を叶える・・・(16)
        model += x[n, t, w] == 1

    for n in Nr: 

        for t in Tr:
            # 連続勤務日数をι以内にする・・・(18)
            model += pulp.lpSum([x[n, t-i, w] for i in range(iota+1) for w in W[:10]]) <= iota
        
        # 1か月間に休日をμ回取得する・・・(19)
        model += pulp.lpSum([x[n, t, 'do'] for t in Tr]) == myu
        
        
        for t in Tr:
            # 3連続夜勤を禁止する
            model += x[n, t-4, 'nn'] + x[n, t-2, 'nn'] + x[n, t, 'nn'] <= 2

            # 対象スタッフの勤務にダミーが入ることを禁止する
            model += x[n, t, 'Ex'] == 0

    # 連休の取得を考慮するのは日勤夜勤対象者のみ→日勤夜勤に入らない人は休診日が休みになるため考慮する必要がない
    for n in Nboth:

        # 1カ月における夜勤・日勤合計回数をε以内にする・・・(17)
        model += pulp.lpSum([x[n, t, w] for t in Tr for w in W[:7]]) == s[n]
        model += s[n] <= epsilon
        # 各技師の合計夜勤・休日日勤回数の平均偏差・・・(32)
        model += meanWorks - s[n] >= -d[n]
        model += meanWorks - s[n] <= d[n]

        # 休診日における休日をρ回以上取得する・・・(20)
        model += pulp.lpSum([x[n, t, 'do'] for t in Tclosed]) >= rho

        # 連休取得・・・(21)(24)(27)
        model += pulp.lpSum([h2[n, t] for t in Tr[:-1]]) >= twoConsecutiveHolidays
        model += pulp.lpSum([h3[n, t] for t in Tr[:-2]]) >= threeConsecutiveHolidays
        model += pulp.lpSum([h3[n, t] for t in Tr[:-3]]) >= fourConsecutiveHolidays

        for t in Tr[:-1]:
            model += x[n, t, W[10]] + x[n, t+1, W[10]] -1 <= h2[n, t]                                           #(22)
            model += x[n, t, W[10]] + x[n, t+1, W[10]] >= 2 * h2[n, t]                                          #(23)
        for t in Tr[:-2]:
            model += x[n, t, W[10]] + x[n, t+1, W[10]] + x[n, t+2, W[10]] -2 <= h3[n, t]                        #(25)
            model += x[n, t, W[10]] + x[n, t+1, W[10]] + x[n, t+2, W[10]] >= 3 * h3[n, t]                       #(26)
        # for t in Tr[:-3]:
        #     model += x[n, t, W[10]] + x[n, t+1, W[10]] + x[n, t+2, W[10]] + x[n, t+3, W[10]] -3 <= h4[n, t]     #(28)
        #     model += x[n, t, W[10]] + x[n, t+1, W[10]] + x[n, t+2, W[10]] + x[n, t+3, W[10]] >= 4 * h4[n, t]    #(29)

        # 夜勤日勤勤務間隔         
        # 休日日勤の翌日に休日日勤や夜勤をできる限り入れない
        for t in Tr:
            model += pulp.lpSum([x[n, t-1, w] for w in W[:4]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) -1 <= i1[n, t]
            model += pulp.lpSum([x[n, t-1, w] for w in W[:4]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) >= 2 * i1[n, t]
        # 休日日勤・夜勤の2日後に休日日勤や夜勤をできる限り入れない
            model += pulp.lpSum([x[n, t-2, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) -1 <= i2[n, t]
            model += pulp.lpSum([x[n, t-2, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) >= 2 * i2[n, t]
        # 3日後
            model += pulp.lpSum([x[n, t-3, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) -1 <= i3[n, t]
            model += pulp.lpSum([x[n, t-3, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) >= 2 * i3[n, t]
        # 4日後
            model += pulp.lpSum([x[n, t-4, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) -1 <= i4[n, t]
            model += pulp.lpSum([x[n, t-4, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) >= 2 * i4[n, t]
        # 5日後
            # model += pulp.lpSum([x[n, t-5, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) -1 <= i5[n, t]
            # model += pulp.lpSum([x[n, t-5, w] for w in W[:7]]) + pulp.lpSum([x[n, t, w] for w in W[:7]]) >= 2 * i5[n, t]
                
    print(f'create at {createDate}')
    print(f'calculatin time : {calctime} s  start....')    

    cbcpath = config.readSettingJson("CBC_PATH")
    pulp.LpStatus[model.solve(pulp.COIN_CMD(timeLimit=calctime, path=cbcpath))]
    
    print(pulp.LpStatus[model.status])
    
    # data = convert_scheduling_data(N, staff, G, Tr, Tclosed, Tdict, W, x)
    data = rd.read_outcome(N, Toutput, Tdict, W, x, createDate)
    # data = output_scheduling_data(N, Tr, Tdict, W, x)
    # xl.output_data(N, staff, G, Tr, Tclosed, Tdict, W, x)
    try:
        dataDir = config.readSettingJson("DATA_DIR")
        outputPath = os.path.join(dataDir,'shift.dat')
        with open(outputPath, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['#' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ',' + pulp.LpStatus[model.status]])
            writer.writerows(data)
    except FileNotFoundError as e:
        print(e)
    except csv.Error as e:
        print(e)
    return pulp.LpStatus[model.status], data

def convertConfig(data):

    createDate = datetime.datetime.strptime(data[0][0], '%Y/%m/%d')
    epsilon = data[1][0]
    iota = data[2][0]
    kappa = data[3][0]
    myu = data[4][0]
    nyu = []
    nyu.append(data[5][0]); nyu.append(data[6][0]); nyu.append(data[7][0])
    rho = data[8][0]
    lam = []
    lam.append(data[9][0]); lam.append(data[10][0]); lam.append(data[11][0]); lam.append(data[12][0]); lam.append(data[13][0]) 
    
    return createDate, epsilon, iota, kappa, myu, nyu, rho, lam


def output_scheduling_data(N, Tr, Tdict, W, x):
    # W1 = ['dA', 'dM', 'dC', 'dF', 'nA', 'nM', 'nC', 'nn', 'dW', 'eW', 'do', 'ho']
    # W2 = ['Ex']
    invW = {'dA':'A日','dM':'M日','dC':'C日','dF':'F日','nA':'A夜','nM':'M夜','nC':'C夜','nn':'明','dW':'','eW':'他','do':'休','ho':'特','Ex':'ダ'}
    invDept = ['MR', 'TV', 'HT', 'NM', 'XA', 'RT', 'XP', 'CT', 'XO', 'FR/NF']
    buf = []

    for n in N:
        for t in Tr:
            shift = []
            for w in W:
                if x[n, t, w].value():
                    shift.append(n)
                    shift.append(Tdict[t])
                    shift.append(invW[w])
                    buf.append(shift)
    return buf                

def convert_scheduling_data(N, staff, G, Tr, Tclosed, Tdict, W, x):
    # W1 = ['dA', 'dM', 'dC', 'dF', 'nA', 'nM', 'nC', 'nn', 'dW', 'eW', 'do', 'ho']
    # W2 = ['Ex']
    invW = {'dA':'A日','dM':'M日','dC':'C日','dF':'F日','nA':'A夜','nM':'M夜','nC':'C夜','nn':'明','dW':'','eW':'他','do':'休','ho':'特','Ex':'ダ'}
    invDept = ['MR', 'TV', 'HT', 'NM', 'XA', 'RT', 'XP', 'CT', 'XO', 'FR/NF']

    buf = []
    for n in N:
        staff_info = []
        if staff.get(n):
            staff_info.append(n)
            staff_info.append(staff[n]['id'])
            staff_info.append(staff[n]['name'])
            for m in G:
                if n in m:
                    staff_info.append(invDept[G.index(m)])
                    break
        else:
            staff_info.append(n)
            staff_info.append('')
            staff_info.append('')
            staff_info.append('')

        for t in Tr:
            shift = []
            for w in W:
                if x[n, t, w].value():
                    for i in staff_info:
                        shift.append(i)
                    shift.append(Tdict[t])
                    shift.append(invW[w])
                    buf.append(shift)
    return buf
        

