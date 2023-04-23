import numpy as np
from sklearn.cluster import KMeans
from row import *
from cols import *
from utils import *
from operator import itemgetter
from functools import cmp_to_key


class DATA:
    def __init__(self, src=None, rows=None):
        self.rows = []
        self.cols = None
        if src or rows:
            if isinstance(src, str):
                csv(src, self.add)
            else:
                self.cols = Col(src.cols.names)
                for row in rows:
                    self.add(row)

    def add(self, t):
        if self.cols:
            t = t if isinstance(t, Row) else Row(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Col(t)

    def stats(self, cols=None, nPlaces=2, what='mid'):
        stats_dict = dict(sorted({col.txt: rnd(getattr(col, what)(), nPlaces) for col in cols or self.cols.y}.items()))
        stats_dict["N"] = len(self.rows)
        return stats_dict

    def dist(self, row1, row2, cols=None):
        n, d = 0, 0
        for col in cols or self.cols.x:
            n = n + 1
            d = d + col.dist(row1.cells[col.at], row2.cells[col.at]) ** options['p']
        return (d / n) ** (1 / options['p'])

    def clone(data, ts={}):
        data1 = DATA()
        data1.add(data.cols.names)
        for _, t in enumerate(ts or {}):
            data1.add(t)
        return data1

    def half(self, rows=None, cols=None, above=None):
        def gap(row1, row2):
            return self.dist(row1, row2, cols)

        def project(row):
            return {'row': row, 'dist': cosine(gap(row, A), gap(row, B), c)}

        rows = rows or self.rows
        some = many(rows, options['Halves'])
        A = above if above and options['Reuse'] else any(some)
        tmp = sorted([{'row': r, 'dist': gap(r, A)} for r in some], key=lambda x: x['dist'])
        far = tmp[int((len(tmp) - 1) * options['Far'])]
        B = far['row']
        c = far['dist']
        left, right = [], []
        for n, tmp in enumerate(sorted(map(project, rows), key=lambda x: x['dist'])):
            if (n + 1) <= (len(rows) / 2):
                left.append(tmp["row"])
            else:
                right.append(tmp["row"])
        evals = 1 if options['Reuse'] and above else 2
        return left, right, A, B, c, evals

    def better(self, row1, row2):
        s1, s2, ys = 0, 0, self.cols.y
        for col in ys:
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 = s1 - math.exp(col.w * (x - y) / len(ys))
            s2 = s2 - math.exp(col.w * (y - x) / len(ys))
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
        return DATA.clone(self, best), DATA.clone(self, rest), evals

    def sway2(self):

        data = self
        def worker(rows, worse, evals0=None, above=None):
            if len(rows) <= len(data.rows) ** options['min']:
                return rows, many(worse, options['rest'] * len(rows)), evals0
            else:
                l, r, A, B, evals = self.kmeans(rows)
                if self.perform_boolean_domination(B, A):
                    l, r, A, B = r, l, B, A
                for row in r:
                    worse.append(row)
                return worker(l, worse, evals + evals0, A)

        best, rest, evals = worker(data.rows, [], 0)
        return DATA.clone(self, best), DATA.clone(self, rest), evals

    def kmeans(self, rows=None):

        left = []
        right = []
        A = None
        B = None

        def min_dist(center, row, A):
            if not A:
                A = row
            ACenterDist = self.dist(A, center)
            ARowDist = self.dist(A, row)
            if ACenterDist > ARowDist:
                return row
            else:
                return A

        if not rows:
            rows = self.rows
        row_set = np.array([each_row.cells for each_row in rows])
        kmeans = KMeans(n_clusters=2, random_state=Seed, n_init=10)
        kmeans.fit(row_set)
        leftside_cluster = Row(kmeans.cluster_centers_[0])
        rightside_cluster = Row(kmeans.cluster_centers_[1])

        for key, key_value in enumerate(kmeans.labels_):
            if key_value == 0:
                A = min_dist(leftside_cluster, rows[key], A)
                left.append(rows[key])
            else:
                B = min_dist(rightside_cluster, rows[key], B)
                right.append(rows[key])

        return left, right, A, B, 1

    def betters(self, n):
        key = cmp_to_key(lambda row1, row2: -1 if self.better(row1, row2) else 1)
        tmp = sorted(self.rows, key=key)
        if n is None:
            return tmp
        else:
            return tmp[1:n], tmp[n + 1:]

    def boolean_domination(self, rows1, rows2, ys=None):
        if isinstance(rows1, Row):
            rows1 = [rows1]
            rows2 = [rows2]
        if not ys:
            ys = self.cols.y

        dominates = False
        for col in ys:
            for row1, row2 in zip(rows1, rows2):
                x = col.norm(row1.cells[col.at]) * col.w * -1
                y = col.norm(row2.cells[col.at]) * col.w * -1
                if x > y:
                    return False
                elif x < y:
                    dominates = True
        return dominates

    def perform_boolean_domination(self, row1, row2, ys=None):
        row1_boolean_dom = self.boolean_domination(row1, row2, ys=ys)
        row2_boolean_dom = self.boolean_domination(row2, row1, ys=ys)
        if row1_boolean_dom and not row2_boolean_dom:
            return True
        else:
            return False