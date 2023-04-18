import math, sys
sys.path.append("./src")
from constants import *


class Num:
    def __init__(self, at=0, txt=""):
        self.at = at
        self.txt = txt
        self.n = 0
        self.mu = 0
        self.m2 = 0
        self.lo = float('inf')
        self.hi = float('-inf')
        self.w = -1 if "-" in self.txt else 1
        self.has = {}

    def add(self, n):
        '''
        Addition method for n
        '''
        if n != "?":
            self.n = self.n + 1
            d = n - self.mu
            self.mu = self.mu + (d / self.n)
            self.m2 = self.m2 + (d * (n - self.mu))
            self.lo = min(n, self.lo)
            self.hi = max(n, self.hi)

    def mid(self):
        '''
        Method for calculating mean
        '''
        return self.mu

    def div(self):
        '''
        Method for calculating Standard Deviation
        '''
        return (self.m2 < 0 or self.n < 2) and 0 or (self.m2 / (self.n - 1)) ** 0.5

    def rnd(self,x,n) -> float:
        '''
        Helper method
        '''
        if x == '?':
            return x
        else:
            mult = math.pow(10, n)
            return math.floor(x * mult + 0.5)/mult

    def norm(self, n):
        return n if n == "?" else (n - self.lo) / (self.hi - self.lo + 1e-32)

    def dist(self, n1, n2):
        '''
        Method to calculate distance
        '''

        if n1=="?" and n2=="?":
            return 1

        n1,n2=self.norm(n1), self.norm(n2)

        if(n1=="?"): n1 = 1 if n2<0.5 else 0
        if(n2=="?"): n2 = 1 if n1<0.5 else 0
        return abs(n1 - n2)

