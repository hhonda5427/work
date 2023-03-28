def count_func_con(data,row,iota):
    #・・・連続勤務日数の計算・・・
    
    #結果格納リスト

    
    data3 = data.iloc[row,:]#変更された行のみ取得

    
    #行列の長さの取得
    columss=len(data3)
    tail=columss-1#変更された行の今月分のみ取得
    
    

    cwork=0#加算用変数

    l=[]#格納リスト

    
    for i in range(columss):
                
        zzz=data.iloc[row,i]
        
        if zzz=='休':
            l.append(cwork)
            cwork=0
        elif zzz=='暇':
            l.append(cwork)
            cwork=0
        elif zzz=='夏':
            l.append(cwork)
            cwork=0
        elif zzz=='特':
            l.append(cwork)
            cwork=0
        else :
            cwork+=1
    l.append(cwork)
    cwork=0
    mwork=max(l)
    print(mwork)
    data4 = data.iloc[row,iota:tail]#今月分データ
    kin=(data4=='勤').sum()
    kyu=(data4=='休').sum()
    ka=(data4=='暇').sum()
    ake=(data4=='明').sum()
    fni=(data4=='F日').sum()
    cni=(data4=='C日').sum()
    ani=(data4=='A日').sum()
    mni=(data4=='M日').sum()
    cya=(data4=='C夜').sum()
    aya=(data4=='A夜').sum()
    mya=(data4=='M夜').sum()
    kin2=(data4==None).sum()
    #各項目の計算
    hd=kyu
    hd_2=ka
    return mwork,hd

def countfunc_col(data,colmun):
    data6 = data.iloc[:,colmun]

    data5=data6.T
    kyu=(data5=='休').sum()
    
    return kyu

