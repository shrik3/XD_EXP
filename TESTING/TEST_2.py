import src.wlxk as xk

parser = xk.EXP_PARSER("15130188004","hj098acwl")










list  = parser.TraverseAll()

for i in list:
    print(i.name+' '+i.tag + '周次:'+i.week)

