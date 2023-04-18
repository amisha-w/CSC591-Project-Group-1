from row import *
import sys

sys.path.append("./src")
from cols import *
from utils import *


class DATA:
    def __init__(self, src):
        self.rows = []
        self.cols = None

        if type(src) == str:
            csv(src, self.add)
        else:
            for t in src:
                self.add(t)

    def add(self, t):
        '''
        Adds row
        '''
        if self.cols:
            if type(t) == list:
                t = Row(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Col(t)

    def clone(self, init={}):
        '''
        Returns clone of data
        '''
        data = DATA([self.cols.names])
        _ = list(map(data.add, init))
        return data

    def stats(self, what, cols, nPlaces):
        def fun(_, col):
            if what == 'mid':
                val = col.mid()
            else:
                val = col.div()
            return col.rnd(val, nPlaces), col.txt

        return kap(cols or self.cols.y, fun)

    def dist(self, row1, row2, cols=None):
        n, d = 0, 0
        c = cols or self.cols.x

        for col in c:
            n += 1
            d += col.dist(row1.cells[col.at], row2.cells[col.at]) ** options['p']

        return (d / n) ** (1 / options['p'])

    def around(self, row1, rows=None, cols=None):

        if rows is None: rows = self.rows

        def function(row2):
            return {"row": row2, "dist": self.dist(row1, row2, cols)}

        mapped = map(function, rows)
        return sorted(mapped, key=lambda x: x["dist"])

    def half(self, rows=None, cols=None, above=None):
        def gap(row1, row2):
            return self.dist(row1, row2, cols)

        def project(row):
            return {'row': row, 'dist': cosine(gap(row, A), gap(row, B), c)}

        def function(r):
            return {'row': r, 'dist': gap(r, A)}

        rows = rows or self.rows
        some = many(rows, options['Halves'])
        A = above if above and options['Reuse'] else any(some)
        tmp = sorted(list(map(function, some)), key=itemgetter('dist'))
        far = tmp[int(options['Far'] * len(rows)) // 1]
        B = far['row']
        c = far['dist']
        left, right = [], []
        for n, tmp in enumerate(sorted(list(map(project, rows)), key=itemgetter('dist'))):
            if n < len(rows) // 2:
                left.append(tmp['row'])
            else:
                right.append(tmp['row'])
        evals = 1 if options['Reuse'] and above else 2
        return left, right, A, B, c, evals

    def cluster(self, rows=None, min=None, cols=None, above=None):
        rows = rows or self.rows
        min = min or (len(rows) ** options['min'])
        cols = cols or self.cols.x
        node = {'data': self.clone(rows)}

        if len(rows) >= 2 * min:
            left, right, node['A'], node['B'], node['mid'], _ = self.half(rows, cols, above)
            node['left'] = self.cluster(left, min, cols, node['A'])
            node['right'] = self.cluster(right, min, cols, node['B'])
        return node

    def better(self, row1, row2):
        s1, s2, ys = 0, 0, self.cols.y
        for col in ys:
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 -= math.exp(col.w * (x - y) / len(ys))
            s2 -= math.exp(col.w * (y - x) / len(ys))
        return s1 / len(ys) < s2 / len(ys)

    def tree(self, rows=None, min=None, cols=None, above=None):
        rows = rows or self.rows
        min = min or len(rows) ** options['min']
        cols = cols or self.cols.x
        node = {'data': self.clone(rows)}
        if len(rows) >= 2 * min:
            left, right, node['A'], node['B'], _, _ = self.half(rows, cols, above)
            node['left'] = self.tree(left, min, cols, node['A'])
            node['right'] = self.tree(right, min, cols, node['B'])
        return node

    def sway(self):
        data = self

        def worker(rows, worse, evals0=None, above=None):
            if len(rows) <= len(data.rows) ** options['min']:
                return rows, many(worse, options['rest'] * len(rows)), evals0
            else:
                l, r, A, B, c, evals = self.half(rows, None, above)
                if self.better(B, A):
                    l, r, A, B = r, l, B, A
                for row in r:
                    worse.append(row)
                return worker(l, worse, evals + evals0, A)

        best, rest, evals = worker(data.rows, [], 0)
        return self.clone(best), self.clone(rest), evals

    def betters(self, n):
        tmp = sorted(self.rows, key=lambda row: self.better(row, self.rows[self.rows.index(row) - 1]))
        return n and tmp[0:n], tmp[n + 1:] or tmp

    def RULE(self, ranges, maxSize):
        t = {}
        for range in ranges:
            t[range['txt']] = t.get(range['txt']) or []
            t[range['txt']].append({'lo': range['lo'], 'hi': range['hi'], 'at': range['at']})
        return prune(t, maxSize)

    def showRule(self, rule):
        def pretty(range):
            return range['lo'] if range['lo'] == range['hi'] else [range['lo'], range['hi']]

        def merges(attr, ranges):
            return list(map(pretty, merge(sorted(ranges, key=itemgetter('lo'))))), attr

        def merge(t0):
            t, j = [], 1
            while j <= len(t0):
                left = t0[j - 1]
                if j < len(t0):
                    right = t0[j]
                else:
                    right = None
                if right and left['hi'] == right['lo']:
                    left['hi'] = right['hi']
                    j = j + 1
                t.append({'lo': left['lo'], 'hi': left['hi']})
                j = j + 1
            return t if len(t0) == len(t) else merge(t)

        return dict_kap(rule, merges)

    def xpln(self, best, rest):
        tmp, maxSizes = [], {}

        def v(has):
            return value(has, len(best.rows), len(rest.rows), "best")

        def score(ranges):
            rule = self.RULE(ranges, maxSizes)
            if rule:
                print(self.showRule(rule))
                bestr = self.selects(rule, best.rows)
                restr = self.selects(rule, rest.rows)
                if len(bestr) + len(restr) > 0:
                    return v({'best': len(bestr), 'rest': len(restr)}), rule

        for ranges in bins(self.cols.x, {'best': best.rows, 'rest': rest.rows}):
            maxSizes[ranges[0]['txt']] = len(ranges)
            print("")
            for range in ranges:
                print(range['txt'], range['lo'], range['hi'])
                tmp.append({'range': range, 'max': len(ranges), 'val': v(range['y'].has)})
        rule, most = firstN(sorted(tmp, key=itemgetter('val')), score)
        return rule, most

    def selects(self, rule, rows):
        def disjunction(ranges, row):
            for range in ranges:
                lo, hi, at = range['lo'], range['hi'], range['at']
                x = row.cells[at]
                if x == "?":
                    return True
                if lo == hi and lo == x:
                    return True
                if lo <= x and x < hi:
                    return True
            return False

        def conjunction(row):
            for ranges in rule.values():
                if not disjunction(ranges, row):
                    return False
            return True

        def function(r):
            if conjunction(r):
                return r

        return list(map(function, rows))