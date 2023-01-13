# from PyQt5.QtCore import QModelIndex, pyqtSignal, QObject


# from Event.memberSubject import memberUpdateGenerator
# from database.member import Members

# changelogで変化したもののみを変えようとおもった
# やってみたら、条件分岐が多くなり面倒くさくなった
# 処理速度どうなのか？、例外処理が大変、デバッグしづらいという判断になった


# class MemberChangeLog(Members, memberUpdateGenerator):

#     changeLog: list[dict[str:QModelIndex, str:str, str:str, str:str]]


#     def __init__(self):
#         super(MemberChangeLog, self).__init__()
#         self.changeLog = []

#     #memberUpdateGeneratorにとってはこれがexecuteみたいなもの
#     def updateMember(self, index: QModelIndex, value, fromClass):
#         print(
#             f'row:{index.row()}, column:{index.column()}, value:{value}, from:{fromClass}')
#         """
#         <<fromClass: Model4Kinmu>>
#         index.row() -> uid
#         index.column() -> day
#         value -> job
#         """
#         self.changeLog.append(
#             {'uid': index.row(), 'day': index.column(), 'job': value, 'fromClass': fromClass})
#         if fromClass == "Model4Kinmu":
#             self.members[self.changeLog[-1]['uid']
#                          ].jobPerDay[self.day_previous_next[int(self.changeLog[-1]['day'])]] = self.changeLog[-1]['job']
    
#     def getMembers(self):
#         return self.members
    # def getMembers(self):
    #     return self.members

    # def getChangedElem(self) -> dict[str:QModelIndex, str:str, str:str]:
    #     return self.changeLog[-1]

    # def getKinmuDFIndex(self):
    #     if self.changeLog[-1]['fromClass'] == "Model4Kinmu":
    #         row = list(self.members.keys()).index(int(self.changeLog[-1]['uid']))
    #         column = int(self.changeLog[-1]['day'])
    #     elif self.changeLog[-1]['fromClass'] == "Model4Yakin":
    #         row = 0
    #         column = 0
    #     return (row, column)

    # def getYakinDFIndex(self):
    #     row = 0
    #     column = 0
    #     return (row, column)
    
# 条件分岐を考えるのが嫌になりました
# 　　　　　　　　　　　　　　, , -―-、
# 　　　　　　　　　　　　　／　　　　 ヽ
# 　　　　　　　／￣￣／　　／i⌒ヽ､| 　　　　オエーー！！！！
# 　　　　　　/　　（゜）/ 　　 ／　/
# 　　　　　/　　　　 ト､., .. /　, ー-､
# 　　　　=彳　　　　　 ＼＼‘ﾟ。､｀ ヽ。、ｏ
# 　　　　/ 　 　　　　　　　＼＼ﾟ。､。、ｏ
# 　　　/ 　　　　　　　　　/⌒ ヽ ヽU　　ｏ
# 　　 /　　　　　　　　　│　　　`ヽU　∴ｌ
# 　　│　　　　　　　　　│　　　　　U　：l
# 　　　　　　　　　　　　　　　　　　　　|：!
# 　　　　　　　　　　　　　　　　　　　　Ｕ
    
