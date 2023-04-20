import sys

sys.path.append("../src")

from src.main import *
from src.utils import *
from src.num import *
from src.sym import *
from src.data import *

n = 0

def test_the():
    print(options.__repr__())

def test_rand():
    Seed = 1
    t=[]
    for i in range(1,1000+1):
        t.append(rint(0,100,1))
    u=[]
    for i in range(1,1000+1):
        u.append(rint(0,100,1))
    for k,v in enumerate(t):
        assert(v==u[k])

def test_some():
    options['Max'] = 32
    num1 = Num()
    for i in range(1,1000+1):
        num1.add(i)
    print(num1.has)

def test_num():
    num1, num2 = Num(), Num()
    for i in range(1,10**3+1):
        num1.add(rand(0,1))
    for i in range(1,10**3+1):
        num2.add(rand(0,1)**2)
    m1,m2 = rnd(num1.mid(),1), rnd(num2.mid(),1)
    d1,d2 = rnd(num1.div(),1), rnd(num2.div(),1)
    print(1, m1, d1)
    print(2, m2, d2)
    return m1 > m2 and .5 == rnd(m1,1)

def test_sym():
    sym = Sym()
    for x in ["a","a","a","a","b","b","c"]:
        sym.add(x)
    print(sym.mid(), rnd(sym.div()))
    return 1.379 == rnd(sym.div())

def no_of_chars_in_file(t):
    global n
    n += len(t)

def test_csv():
    csv(options['file'], no_of_chars_in_file)
    return n > 0

def test_data():
    data = DATA(options['file'])
    col=data.cols.x[2]
    print(col.lo,col.hi, col.mid(),col.div())
    print(data.stats(data.cols.y, 2, 'mid'))

def test_clone():
    data1 = DATA(options['file'])
    data2 = data1.clone(data1.rows)
    print(data1.stats(data1.cols.y, 2, 'mid'))
    print(data2.stats(data2.cols.y, 2, 'mid'))

def test_cliffs():
    assert(False == cliffsDelta( [8,7,6,2,5,8,7,3],[8,7,6,2,5,8,7,3]))
    assert(True  == cliffsDelta( [8,7,6,2,5,8,7,3], [9,9,7,8,10,9,6]))
    t1,t2=[],[]
    for i in range(1,1000+1):
        t1.append(rand(0,1))
    for i in range(1,1000+1):
        t2.append(rand(0,1)**.5)
    assert(False == cliffsDelta(t1,t1))
    assert(True  == cliffsDelta(t1,t2))
    diff,j=False,1.0
    while not diff:
        def function(x):
            return x*j
        t3=list(map(function, t1))
        diff=cliffsDelta(t1,t3)
        print(">",rnd(j),diff)
        j=j*1.025

def test_dist():
    data = DATA(options['file'])
    num  = Num()
    for row in data.rows:
        num.add(data.dist(row, data.rows[1]))
    print({'lo' : num.lo, 'hi' : num.hi, 'mid' : rnd(num.mid()), 'div' : rnd(num.div())})

def test_half():
    data = DATA(options['file'])
    left,right,A,B,c,_ = data.half()
    print(len(left),len(right))
    l,r = data.clone(left), data.clone(right)
    print("l",l.stats(l.cols.y, 2, 'mid'))
    print("r",r.stats(r.cols.y, 2, 'mid'))

def test_tree():
    data = DATA(options['file'])
    showTree(data.tree(),"mid",data.cols.y,1)
    return True

def test_sway():
    data = DATA(options['file'])
    best,rest,_ = data.sway()
    print("\nall ", data.stats(data.cols.y, 2, 'mid'))
    print("    ", data.stats(data.cols.y, 2, 'div'))
    print("\nbest",best.stats(best.cols.y, 2, 'mid'))
    print("    ", best.stats(best.cols.y, 2, 'div'))
    print("\nrest", rest.stats(rest.cols.y, 2, 'mid'))
    print("    ", rest.stats(rest.cols.y, 2, 'div'))
    return True

def test_bins():
    global b4
    data = DATA(options['file'])
    best,rest,_ = data.sway()
    print("all","","","",{'best':len(best.rows), 'rest':len(rest.rows)})

def test_xpln():
    data = DATA(options['file'])
    best,rest,evals = data.sway()
    xp = XPLN(best, rest)
    rule,most=  xp.xpln(data,best,rest)
    print("\n-----------\nexplain=", showRule(rule))
    select = selects(rule,data.rows)
    data_select = [s for s in select if s!=None]
    data1= data.clone(data_select)
    print("all               ",data.stats(data.cols.y, 2, 'mid'),data.stats(data.cols.y, 2, 'div'))
    print("sway with",evals,"evals",best.stats(best.cols.y, 2, 'mid'),best.stats(best.cols.y, 2, 'div'))
    print("xpln on",evals,"evals",data1.stats(data1.cols.y, 2, 'mid'),data1.stats(data1.cols.y, 2, 'div'))
    top,_ = data.betters(len(best.rows))
    top = data.clone(top)
    print("sort with",len(data.rows),"evals",top.stats(top.cols.y, 2, 'mid'),top.stats(top.cols.y, 2, 'div'))


if __name__ == '__main__':
    eg('the', 'show options', test_the)
    eg('rand', 'demo random number generation', test_rand)
    eg('some', 'demo of reservoir sampling', test_some)
    eg('nums', 'demo of NUM', test_num)
    eg('sym', 'demo SYMS', test_sym)
    eg('csv', 'reading csv files', test_csv)
    eg('data', 'showing DATA sets', test_data)
    eg('clone', 'replicate structure of a DATA', test_clone)
    eg('cliffs', 'start tests', test_cliffs)
    eg('dist', 'distance test', test_dist)
    eg('half', 'divide data in half', test_half)
    eg('tree', 'make snd show tree of clusters', test_tree)
    eg('sway', 'optimizing', test_sway)
    eg('bins', 'find deltas between best and rest', test_bins)
    eg('expln', 'explore explanation sets', test_xpln)
    main(options, help, egs)