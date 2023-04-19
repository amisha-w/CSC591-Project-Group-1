import sys, re, math, copy, json, sys
sys.path.append("../src")
from constants import *
from pathlib import Path
from sym import Sym
from num import Num
from operator import itemgetter
import random

Seed = 937162211
def diffs(nums1,nums2):
  def fun(k,nums):
        return cliffsDelta(nums.has,nums2[k].has),nums.txt
  return kap(nums1, fun)

def delta(i, other):
    e, y, z = 1E-32, i, other
    return abs(y.mu - z.mu) / ((e + y.sd ** 2 / y.n + z.sd ** 2 / z.n) ** .5)

def bootstrap(y0, z0):
    x, y, z, yhat, zhat = Num(), Num(), Num(), [], []
    for y1 in y0:
        x.add(y1)
        y.add(y1)
    for z1 in z0:
        x.add(z1)
        z.add(z1)
    xmu, ymu, zmu = x.mu, y.mu, z.mu
    for y1 in y0:
        yhat.append(y1 - ymu + xmu)
    for z1 in z0:
        zhat.append(z1 - zmu + xmu)
    tobs = delta(y, z)
    n = 0
    for _ in range(options['bootstrap']):

        if delta(Num(t=samples(yhat)), Num(t=samples(zhat))) > tobs:
            n += 1
    return n / options['bootstrap'] >= options['conf']

def RX(t,s):
    t = sorted(t)
    return {'name' : s or "", 'rank':0, 'n':len(t), 'show':"", 'has':t}

def div(t):
    t= t.get('has', t)
    return (t[ len(t)*9//10 ] - t[ len(t)*1//10 ])/2.56

def mid(t):
    t= t.get('has', t)
    n = len(t)//2
    return (t[n] +t[n+1])/2 if len(t)%2==0 else t[n+1]

def merge(rx1,rx2) :
    rx3 = RX([], rx1['name'])
    for _,t in enumerate([rx1['has'],rx2['has']]):
        for _,x in enumerate(t): 
            rx3['has'].append(x)
    rx3['has'] = sorted(rx3['has'])
    rx3['n'] = len(rx3['has'])
    return rx3

def samples(t,n=0):
    u= []
    n = n or len(t)
    for i in range(n): 
        u.append(t[random.randrange(len(t))]) 
    return u

def gaussian(mu,sd):
    mu,sd = mu or 0, sd or 1
    sq,pi,log,cos,r = math.sqrt,math.pi,math.log,math.cos,random.random
    return  mu + sd * sq(-2*log(r())) * cos(2*pi*r())

def cliffsDelta(ns1,ns2):
    if len(ns1) > 256:
        ns1 = many(ns1,256)
    if len(ns2) > 256:
        ns2 = many(ns2,256)
    if len(ns1) > 10*len(ns2):
        ns1 = many(ns1,10*len(ns2))
    if len(ns2) > 10*len(ns1):
        ns2 = many(ns2,10*len(ns1))
    n,gt,lt = 0,0,0
    for x in ns1:
        for y in ns2:
            n = n + 1
            if x > y:
                gt = gt + 1
            if x < y:
                lt = lt + 1
    return abs(lt - gt)/n > options['cliffs']

def showTree(node, what, cols, nPlaces, lvl = 0):
  if node:
    print('|.. ' * lvl + '[' + str(len(node['data'].rows)) + ']' + '  ', end = '')
    if not node.get('left') or lvl==0:
        print(node['data'].stats())
    else:
        print('')
    showTree(node.get('left'), what,cols, nPlaces, lvl+1)
    showTree(node.get('right'), what,cols,nPlaces, lvl+1)

def bins(cols,rowss):
    out = []
    for col in cols:
        ranges = {}
        for y,rows in rowss.items():
            for row in rows:
                x = row.cells[col.at]
                if x != '?':
                    k = int(bin(col,x))
                    if not k in ranges:
                        ranges[k] = range_fun(col.at,col.txt,x)
                    extend(ranges[k], x, y)
        ranges = list(dict(sorted(ranges.items())).values())
        r = ranges if isinstance(col, Sym) else mergeAny(ranges)
        out.append(r)
    return out

def bin(col,x):
    if x=='?' or isinstance(col, Sym):
        return x
    tmp = (col.hi - col.lo)/(options['bins'] - 1)
    return  1 if col.hi == col.lo else math.floor(x/tmp + .5)*tmp

# def coerce(s):
#     if s == 'true':
#         return True
#     elif s == 'false':
#         return False
#     elif s.isdigit():
#         return int(s)
#     elif '.' in s and s.replace('.', '').isdigit():
#         return float(s)
#     else:
#         return s
    
def coerce(s):
    bool_s = s.lower()
    for t in [int, float]:
        try:
            return t(s)
        except ValueError:
            pass
    if bool_s in ["true", "false"]:
        return bool_s == "true"
    return s

def eg(key, str, fun):
    egs[key] = fun
    global help
    help = help + '  -g '+ key + '\t' + str + '\n'

def rint(lo,hi, mSeed = None):
    return math.floor(0.5 + rand(lo,hi, mSeed))


def rand(lo, hi, mSeed = None):
    lo, hi = lo or 0, hi or 1
    global Seed
    Seed = 1 if mSeed else (16807 * Seed) % 2147483647
    return lo + (hi-lo) * Seed / 2147483647

def rnd(n, nPlaces = 3):
    mult = 10**nPlaces
    return math.floor(n * mult + 0.5) / mult

def csv(file, fun):
    t = []
    with open(file, 'r', encoding='utf-8') as file:
        for _, line in enumerate(file):
            row = list(map(coerce, line.strip().split(',')))
            t.append(row)
            fun(row)

def kap(t, fun):
    u = {}
    what = enumerate(t)
    if type(t) == dict:
        what = t.items()
    for k, v in what:
        v, k = fun(k, v)
        if not k:
            u[len(u)] = v
        else:
            u[k] = v
    return u

def dict_kap(t, fun):
    u = {}
    for k,v in t.items():
        v, k = fun(k,v) 
        u[k or len(u)] = v
    return u

def cosine(a,b,c):
    if c==0:
        return 0
    return (a**2 + c**2 - b**2) / (2*c)

def any(t):
    return t[rint(0, len(t) - 1)]

def many(t, n):
    arr = []
    for index in range(1, n + 1):
        arr.append(any(t))
    return arr

def show(node, what, cols, nPlaces, lvl = 0):
  if node:
    print('|..' * lvl, end = '')
    if not node.get('left'):
        print(node['data'].rows[-1].cells[-1])
    else:
        print(int(rnd(100*node['c'], 0)))
    show(node.get('left'), what,cols, nPlaces, lvl+1)
    show(node.get('right'), what,cols,nPlaces, lvl+1)

def deepcopy(t):
    return copy.deepcopy(t)

def oo(t):
    d = t.__dict__
    d['a'] = t.__class__.__name__
    d['id'] = id(t)
    d = dict(sorted(d.items()))
    print(d)

def merge(col1,col2):
  new = deepcopy(col1)
  if isinstance(col1, Sym):
      for n in col2.has:
        new.add(n)
  else:
    for n in col2.has:
        new.add(new,n)
    new.lo = min(col1.lo, col2.lo)
    new.hi = max(col1.hi, col2.hi) 
  return new

def range_fun(at,txt,lo,hi=None):
    return {'at':at,'txt':txt,'lo':lo,'hi':lo or hi or lo,'y':Sym()}

def extend(range,n,s):
    range['lo'] = min(n, range['lo'])
    range['hi'] = max(n, range['hi'])
    range['y'].add(s)

def value(has,nB = None, nR = None, sGoal = None):
    sGoal,nB,nR = sGoal or True, nB or 1, nR or 1
    b,r = 0,0
    for x,n in has.items():
        if x==sGoal:
            b = b + n
        else:
            r = r + n
    b,r = b/(nB+1/float("inf")), r/(nR+1/float("inf"))
    return b**2/(b+r)

def merge2(col1,col2):
  new = merge(col1,col2)
  if new.div() <= (col1.div()*col1.n + col2.div()*col2.n)/new.n:
    return new

def mergeAny(ranges0):
    def noGaps(t):
        for j in range(1,len(t)):
            t[j]['lo'] = t[j-1]['hi']
        t[0]['lo']  = float("-inf")
        t[len(t)-1]['hi'] =  float("inf")
        return t

    ranges1,j = [],0
    while j <= len(ranges0)-1:
        left = ranges0[j]
        right = None if j == len(ranges0)-1 else ranges0[j+1]
        if right:
            y = merge2(left['y'], right['y'])
            if y:
                j = j+1
                left['hi'], left['y'] = right['hi'], y
        ranges1.append(left)
        j = j+1
    return noGaps(ranges0) if len(ranges0)==len(ranges1) else mergeAny(ranges1)

# def firstN(sortedRanges,scoreFun):
#     print("")
#     def function(r):
#         print(r['range']['txt'],r['range']['lo'],r['range']['hi'],rnd(r['val']),r['range']['y'].has)
#     _ = list(map(function, sortedRanges))
#     print()
#     first = sortedRanges[0]['val']
#     def useful(range):
#         if range['val']>.05 and range['val']> first/10:
#             return range
#     sortedRanges = [x for x in sortedRanges if useful(x)]
#     most,out = -1, -1
#     for n in range(1,len(sortedRanges)+1):
#         slice = sortedRanges[0:n]
#         slice_range = [x['range'] for x in slice]
#         tmp,rule = scoreFun(slice_range)
#         if tmp and tmp > most:
#             out,most = rule,tmp
#     return out,most
def firstN(self, sorted_ranges, scoreFun):
    first = sorted_ranges[0]['val']

    def useful(range):
        if range['val'] > 0.05 and range['val'] > first / 10:
            return range
    sorted_ranges = [s for s in sorted_ranges if useful(s)]
    most = -1
    out = -1
    for n in range(len(sorted_ranges)):
        tmp, rule = scoreFun([r['range'] for r in sorted_ranges[:n+1]])
        if tmp is not None and tmp > most:
            out, most = rule, tmp
    return out, most


def prune(rule, maxSize):
    n=0
    for txt,ranges in rule.items():
        n = n+1
        if len(ranges) == maxSize[txt]:
            n=n+1
            rule[txt] = None
    if n > 0:
        return rule

def stats_average(data_array):
    res = {}
    for x in data_array:
        for k,v in x.stats().items():
            res[k] = res.get(k,0) + v
    for k,v in res.items():
        res[k] /= 20
    return res