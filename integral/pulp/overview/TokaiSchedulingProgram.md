# 勤務表作成プログラムについて  
今回の勤務表作成プログラムはこれまでのような貪欲法ではなく組合せ最適化問題として捉え，様々な条件を定式化し問題を解決する  

勤務表作成において重要なことは，「業務の質」と「技師の労働環境」を保つことである  
これを達成するためには  

- 業務の質を保つ  
  - 毎日の各勤務において必要な人数を確保する
  - 正規スタッフの人数を一定以上確保する
  - 現場を任せることのできる技師を確保する
- スタッフの労働環境
  - 連続勤務日数の上限を守る
  - 決められて休日数を確保する
  - 一定数以上の連休を確保する
  - 夜勤・日勤合計回数の上限を守る
  - 休診日における勤務回数を平均化する
  - できる限り夜勤間隔を設ける
  - 勤務希望（夜勤回避，夜勤・日勤希望）を叶える  
  

以上の制約条件を守ることで最適な勤務表が作成できる。  
※今回の勤務表作成では夜勤回数を年間累積回数で揃えることはせず，月ごとに上限を超えないようにするだけである。 

勤務表作成プログラムは **pythonの「PULP」** というライブラリを用いて作成する。制約条件を増やしていくと最適な解を導き出すことができない可能性があるため，今回の作成プログラムではダミーの技師を配置することで対応する。 

# 言葉の定義
診療日：外来業務が行われている日  
休診日：外来業務が行われてない日  

日勤：診療日における日勤業務  
休日勤：休診日における日勤業務  
$A$日：休診日におけるアンギオ日勤業務  
$M$日：休診日における$MRI$日勤業務  
$C$日：休診日における$CT$日勤業務  
$F$日：休診日におけるフリー日勤業務  

夜勤：診療日における夜勤業務  
休夜勤：休診日における夜勤業務  
$A$夜：休診日におけるアンギオ夜勤業務  
$M$夜：休診日における$MRI$夜勤業務  
$C$夜：休診日における$CT$夜勤業務  
明&emsp;: 夜勤明け  

他勤：出張などの勤務  
休日：必ず取得させなければならない休み　4週7休+祝日  
休暇：年休・育休・リフレッシュ休暇など  

正規スタッフ：そのモダリティに配属されているスタッフ  


# 記号の定義
$N$：技師全員の集合(ダミーを含む)&emsp; $N = N_r + N_{dum}$  
$N_r$：スケジュールの対象となる技師の集合&emsp; $N_r \subset N$  
$N_{dum}$：ダミー技師の集合&emsp; $N_{dum} \subset N$  
$N_{daily}$：休日勤が可能な技師の集合&emsp; $N_{daily} \subset N$  
$N_{night}$：夜勤が可能な技師の集合&emsp; $N_{night} \subset N$  
$N_{both}$：夜勤または休日勤が可能な技師の集合&emsp; $N_{both} = N_{daily}\cup N_{night}$  
$N_s$：各休日勤及び夜勤業務が可能な技師の集合(ダミーを含む)&emsp; $N_s \subset N$
$$
\begin{pmatrix}
&s=0:日A & s=1:日M & s=2:日C & s=3:日F　\\
&s=4:夜A & s=5:夜M & s=6:夜C \\
\end{pmatrix}
$$

***
$G_m$：モダリティ$m$に属する技師の集合(ダミーを含む)&emsp; $G_m \subset N$  
$Core_m$：モダリティ$m$で現場を任せることのできる技師の集合(ダミーを含む)&emsp; $Core_m \subset N$  
$$
\begin{pmatrix}
& m=0:MR & m=1:TV & m=2:HT &\\
& m=3:NM & m=4:XA & m=5:RT &\\
& m=6:XP & m=7:CT & m=8:XO &\\
&& m=9:他\{FR,NF,MM, MT\}
\end{pmatrix}
$$
***
$T$：日にちの集合（前月と次月1日分を含む　前月分は連続勤務日数の上限で決まる）  
$T_r$：スケジュールの対象となる日にちの集合&emsp; $T_r=\{1,2,3,\dots,k\} \subset T$  
$T_{opened}$：診療日となる日にちの集合  
$T_{closed}$：休診日となる日にちの集合  
※プログラムの中で休診日の判定は内閣府が公表している「国民の祝日」のCSVファイルを用いている。毎年，ダウンロードして使用する。文字コードには気をつける。
***
$W$：勤務の種類の集合
$$
\begin{pmatrix}
& w=&0:A日, & w=&1:M日, & w=&2:C日&\\
& w=&3:F日, & w=&4:A夜, & w=&5:M夜&\\
& w=&6:C夜, & w=&7:明, & w=&8:日勤&\\
& w=&9:他勤, & w=&10:休日, & w=&11:休暇 
\end{pmatrix}
$$
$W^+$：勤務の集合$W$にダミー勤務（$w = 12$）を加えた集合 &emsp; $W^+=W \cup\{ダミー勤務\}$  
***
$Q$：禁止勤務の組合せ&emsp; $Q = \{3連続夜勤(夜勤，明け，夜勤，明け，夜勤，明け)\}$
***
$F_{previous}$：前月分の勤務の集合&emsp; $F_{prev}=\{(i,j,k),\quad i\in N_r, \quad j \in T \setminus T_r, \quad k \in W\}$  
$F_{request}$：勤務希望の集合&emsp; $F_{requ}=\{(i,j,k),\quad i\in N_r, \quad j \in T_r, \quad k \in W\}$  

***
#### 日付ごと=勤務表の列（業務の質）
$\alpha_{t\cdot w}$：日付$t$における各勤務$w$の必要人数  
$\beta_{t\cdot m}$：日付$t$における各モダリティ$m$の最低限必要な正規スタッフ人数  
$\gamma_{t\cdot m}$：日付$t$における各モダリティ$m$の責任者クラスの最低限必要な人数  
***
#### スタッフごと=勤務表の行（労働環境）
$\epsilon$：各月における夜勤・日勤合計回数の上限  
$\iota$：連続勤務日数の上限  
$\kappa$：所定労働時間（今回のプログラムでは考慮していない⇒超えた場合は残業で対応）  
$\lambda_{2\sim 4}$：夜勤間隔における荷重係数（できる限り短い間隔で入らないようにする）  
$\lambda_{5}$：夜勤・休日日勤回数の平均偏差における荷重係数（できる限り回数を揃える）  
$$
\begin{cases}
\lambda_2 = 0.1 \\
\lambda_3 = 0.001 \\
\lambda_4 = 0.0001 \\
\lambda_5 = 0.01 \\
\end{cases}
$$
$\mu$：各月における休日数  
$\nu_{2 \sim 4}$：各月における2・3・4連休数  
$\rho$：各月における休診日に最低限取得しなければならない休日数  

# 変数
$x$：各技師$n$が各日にち$t$における勤務$w$を行うどうかを決めるバイナリ変数  

$$
x_{n\cdot t \cdot w}\in \{0,1\}\qquad,n\in N,t\in T,w\in W^+\tag{1}
$$

$h_{2 \sim 4}$：2~4連休を数えるためのバイナリ変数  
$$
{h_k}_{n\cdot t} \in \{0,1\} \qquad ,k =\{2,3,4\},n \in Nr, t \in T_r \tag{2}
$$

$i_{2 \sim 5}$：2~4日間隔の夜勤を数えるためのバイナリ変数  
$$
{i_k}_{n \cdot t} \in \{0,1\} \qquad ,k =\{2,3,4\},n \in N_{night}, t \in T_r\tag{3}
$$

$d$：夜勤・休日日勤回数との偏差  
$$
d_{n} \geqq 0 \qquad ,n \in N_{both}
$$
# 目的関数 $\fallingdotseq Soft \quad Constrains$ 
ダミー技師が勤務$W$に配置される回数を最小にし，  
&emsp; &emsp; &emsp; 夜勤間隔をできる限り設けて，  
&emsp; &emsp; &emsp;  &emsp; 夜勤・休日日勤回数をできる限り揃える  
$$
\begin{align*}
min.\qquad  &\sum_{n\in N_{dum}}\sum_{t\in T_r}\sum_{w\in W}x_{ntw}
            + \lambda_2 \sum _{n \in N_{night}}\sum_{t = 0}^{T_r - 2}{i_2}_{n \cdot t}\\
            & + \lambda_3  \sum _{n \in N_{night}}\sum_{t = 0}^{T_r - 3}{i_3}_{n \cdot t} + \lambda_4  \sum _{n \in N_{night}}\sum_{t = 0}^{T_r - 4}{i_4}_{n \cdot t} \\
            &+ \lambda_5  \sum _{n \in N_{night}}\sum_{t = 0}^{T_r - 5}{i_5}_{n \cdot t} \tag{4}
\end{align*}
$$
# 制約条件 $\fallingdotseq Hard \quad Constraints$  
技師$n$に勤務$w$を必ず割り当てる  
$$
\sum_{w\in W^+}x_{ntw}=1\qquad n\in N, t\in T_r \tag{5}
$$
スケジュールの対象となる技師$Nr$にはダミー勤務（$w=12$）を割り当てない
$$
\sum_{w\in W^+}x_{nt12}=0\qquad n\in N_r, t\in T_r \tag{33}
$$


## 各日における制約（列）  

日にち$t$における勤務$w$の必要人数を合わせる  
&emsp; &emsp;日勤の人数を設定数以上で確保する・・・(6)  
&emsp; &emsp;休日勤の人数を設定数で確保する・・・(7)  
&emsp; &emsp;夜勤・休日勤・明けの人数を確保する・・・(8)  
&emsp; &emsp;診療日における休日取得人数を設定以下で確保する・・・(9)  
&emsp; &emsp;休診日における休日取得人数を設定以上で確保する・・・(10)    




$$
\begin{align*}
&\sum_{n\in N}x_{n \cdot t \cdot w} \geqq  \alpha_{t \cdot w}\qquad t\in T_{opened} \quad ,w=8& \tag{6} \\
&\sum_{n\in N}x_{n \cdot t \cdot w} =  \alpha_{t \cdot w}\qquad t\in T_{closed} \quad ,w=8& \tag{7} \\
&\sum_{n\in N} x_{n \cdot t \cdot w} = \alpha_{t \cdot w}\qquad t\in T_r\quad,w=\{0,1,2,3,4,5,6,7\} & \tag{8}\\
&\sum_{n\in N}x_{n \cdot t \cdot w} \leqq \alpha_{t \cdot w}\qquad t\in T_{opened} \quad ,w = 10 \tag{9}\\
&\sum_{n\in N}x_{n \cdot t \cdot w} \geqq \alpha_{t \cdot w}\qquad t\in T_{closed} \quad ,w = 10\tag{10}
\end{align*}
$$
日にち$t$の各モダリティ$m$における最低限必要な正規スタッフ数  
$$
\sum_{n\in G_m}x_{nt1}\geq \beta_{tm}\qquad t\in T_{r}\quad,m=\{1,2,\dots,9\}\tag{11}
$$
日にち$t$における責任者クラスのスタッフを確保する
$$
\sum_{n \in Core_{m}}x_{nt1}\geq \gamma_{m}\qquad t\in T_{opened}, m=\{1,2,\dots,9\}\tag{12}
$$
日にち$t$における各夜勤スタッフを確保する  
$$
\begin{align*}
\sum_{n \in N_{s}}x_{n\cdot t\cdot w}=\alpha_{t \cdot w} \qquad &t\in T_r \backslash \{1,2,\dots,k\} \quad \\
& s = \{0,1,2,3,4,5,6\} \\
& w = \{4,5,6\}\tag{13}
\end{align*}
$$
夜勤の翌日は明けにする  
$$
\begin{align*}
x_{n\cdot (t-1)\cdot w_{curr}}=x_{n\cdot t\cdot w_{next}}\qquad& n\in N_r \\
& w_{curr}\in \{4,5,6\} \quad ,w_{next} = 8\\
& t\in T_r\backslash \{1,\dots,k,k+1\}\tag{14}
\end{align*}
$$
休日勤のスタッフを確保する    
$$
\begin{align*}
\sum_{n \in N_{s}}x_{n\cdot t\cdot w}=\alpha_{t \cdot w} \qquad&  t\in T_{closed} \\
 &(s,w) = \begin{cases}(0,0),(1,1) \\
 (2,2),(3,3)
 \end{cases}\tag{15}
 \end{align*}
$$
## 各技師における制約（行）
勤務希望$F_{request}$を叶える  
$$
x_{i,j,k}=\tau\qquad (i, j, k)\in F_{request} \quad ,\tau\in\{1,0\}\tag{16}
$$
1ケ月における夜勤・日勤合計回数を$\epsilon$以内にする  
$$
\sum_{t\in T_r}\sum_{w=5}^7x_{ntw}\leq \epsilon \qquad n\in N_{night}\tag{17}
$$
連続勤務日数を$\iota$以内にする（デフォルトでは$\iota=12$）  
$$
\sum_{\phi=0}^{\iota+1}\sum_{w=1}^9x_{n\cdot (t-\phi)\cdot w}\leq\iota \qquad n\in N_r,t\in T_r \tag{18}
$$
1ケ月に休日を$\mu$回取得する  
$$
\sum_{t\in T_r}x_{n \cdot t \cdot w}=\mu \qquad n\in N_r \quad ,w = 10\tag{19}
$$
休診日における休日を$\rho$回以上取得する  
$$
\sum_{t \in T_{closed}}x_{n \cdot t \cdot w} \geq \rho \qquad n \in N_{both} \quad , w = 11 \tag{20}
$$
2連休数を$\nu_2$回取得する  
$$
\begin{align*}
&\sum_{t = 1}^{T_r -1}{h_d}_{n \cdot t }=\nu_2 \qquad & n \in N_{both} \quad ,w = 10 \tag{21} \\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w} -1 \leq {h_d}_{n \cdot t}  \qquad  & n \in N_{both}, t \in T_r \tag{22}\\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w} \geqq 2 \cdot {h_d}_{n \cdot t} \qquad & n \in N_{both}, t \in T_r \tag{23}  
\end{align*}
$$
3連休数を$\nu_3$回取得する  
$$
\begin{align*}
&\sum_{t = 1}^{T_r -2}{h_t}_{n \cdot t}=\nu_3 \qquad & n \in N_{both} \quad, w = 10\tag{24} \\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w}+x_{n \cdot (t+2) \cdot w} -2 \leq {h_t}_{n \cdot t}  \qquad  & n \in N_{both}, t \in T_r & \tag{25}\\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w}+x_{n \cdot (t+2) \cdot w} \geqq 3 \cdot {h_t}_{n \cdot t} \qquad & n \in N_{both}, t \in T_r &\tag{26} 
\end{align*}
$$
4連休数を$\nu_4$回取得する  
$$
\begin{align*}
&\sum_{t = 1}^{T_r -3}{h_q}_{n \cdot t}=\nu_4 & n \in N_{both} \quad, w = 10 \tag{27} \\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w} & \\
&+x_{n \cdot (t+2) \cdot w}+x_{n \cdot (t+3) \cdot w} -3 \leq {h_q}_{n \cdot t}  \qquad  & n \in N{both}r, t \in T_r & \tag{28}\\
&x_{n \cdot t \cdot w}+x_{n \cdot (t+1) \cdot w} & \\
&+x_{n \cdot (t+2) \cdot w} +x_{n \cdot (t+3) \cdot w}\geqq 4 \cdot {h_q}_{n \cdot t} \qquad & n \in N_{both}, t \in T_r & \tag{29}
\end{align*}
$$

夜勤間隔(1~4日)を求める
$$
\begin{align*}
\sum_{w = 4}^{6}x_{n \cdot t  \cdot w} + \sum_{w=4}^{6}x_{x \cdot t + \phi \cdot w} -1 \leq {i_\phi}_{n \cdot t} \qquad &n \in N_{night} \\
&,t \in T_r \backslash \{1,2, \dots , k-\phi \} \\
&,\phi = \{2, 3,4\} \tag{30} \\
\sum_{w = 4}^{6}x_{n \cdot t  \cdot w} + \sum_{w=4}^{6}x_{x \cdot t + \phi \cdot w}  \geq 2 \cdot {i_\phi}_{n \cdot t} \qquad 
&n \in N_{night} \\
&,t \in T_r \backslash \{1,2, \dots , k-\phi\} \\
&,\phi = \{2,3,4\}\tag{31} \\
\end{align*}
$$

夜勤・休日日勤回数との偏差を求める  
$$
\begin{align*}
&MeanWorks- \sum_{t \in T_r}\sum_{w \in W}x_{n \cdot t \cdot w} \geqq -d_n &\qquad n \in N_r \\
&MeanWorks- \sum_{t \in T_r}\sum_{w \in W}x_{n \cdot t \cdot w} \leqq d_n &\qquad n \in N_r \\
&d_n \geqq 0 \tag{32}
\end{align*}
$$


## 入力データ(.dat)について  

### $N.dat$
作成月に所属するスタッフのUIDを格納。  
ETやASも含まれている  



### $Nrdeptcore.dat$

スケジュールの対象となるスタッフUIDとその所属モダリティ，各モダリティスキルを格納。  
uid,  所属, RT,  MR, TV, KS, NM, XP, CT, XO, AG, MG, MT  



### $skill.dat$

夜勤や休日日勤が対応可能なスタッフUIDと各夜勤勤務スキルを格納  
uid,　アンギオ，　MR，　CT，　FR，　夜勤対応，　休日日勤対応  
　

### $alpah.dat$  
勤務集合$W$に対応した必要人数を格納  
各行がそれぞれの勤務，2列目以降が1日から月末までの必要人数を記載  
A日：アンギオ日勤  
M日：MRI日勤  
C日：CT日勤  
F日：フリー日勤  
A夜：アンギオ夜勤  
M夜：MRI夜勤  
C夜：CT夜勤  
明：夜勤明け  
日勤：通常診療の日勤  
他勤：出張や他病院への応援業務  
休日：必ず取得しなければならない休み  
休暇：年休・半休・夏休・特休  



### $beta.dat$  

各モダリティにおける最低限必要な正規スタッフ人数を格納  
各行がそれぞれのモダリティ，2列目移行に1日から月末までの最低限必要な正規スタッフ人数を記載  



### $gamma.dat$  

各モダリティにおける責任者クラスの必要人数を格納
各行がそれぞれのモダリティ，2列目移行に1日から月末までの最低限必要な責任者クラスの人数を記載  



### $configvar.dat$  

勤務表作成における必要変数を格納  
1列目に変数名，　2列目に値  



### $previous.dat$  

スケジュールの対象となるスタッフの先月分の勤務データを格納  
uid,　日付，　勤務名  
※勤務名はデータ量の関係で数値に変換してから出力する可能性あり。その際は変換テーブルを用いる。  



### $request.dat$

スケジュールの対象となるスタッフの作成月の勤務希望データを格納  
uid，　日付，　希望勤務  
※勤務名はデータ量の関係で数値に変換してから出力する可能性あり。その際は変換テーブルを用いる。  



### $modalityconstants.dat$  

作成月の各モダリティにおける必要人数のデータを格納  
各行の先頭列にモダリティ名，2列目移行に1日から月末までの必要人数を記載  
※勤務表作成には使用しないが，修正などに用いる。



### $staffinfo.dat$

N.datに格納さ入れているUIDと対応した職員番号と氏名が格納されている  



### $tshift.dat$  

作成した勤務表データを格納  
データはASやET，ダミーのデータを含んでいる  
各行にUID, 職員ID，氏名，日付，勤務の順に値が入っている  
ただし，ダミーのデータは職員ID，氏名はブランクとなっている