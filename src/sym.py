import math

class Sym:
    def __init__(self, at=None, txt=None):
        self.at = at if at else 0
        self.txt = txt if txt else ""

        self.n = 0
        self.has = {}
        self.most = 0
        self.mode = None

    def add(self, x: str):
        '''
        Method for calculating count of x
        '''
        if x != "?":
            self.n += 1
            if x in self.has:
                self.has[x] = self.has[x] + 1
            else:
                self.has[x] = 1
            if self.has[x] > self.most:
                self.most = self.has[x]
                self.mode = x


    def mid(self):
        '''
        Method which returns mode value
        '''
        return self.mode

    def div(self):
        """
        Method which returns standard deviation value
        """
        def FUN(p):
            return p * math.log(p, 2)

        e = 0
        for key, val in self.has.items():
            e += FUN(val / self.n)

        return -e
    
    def rnd(self, x, n):
        return x

    def dist(self, s1, s2):
        if s1 == "?" and s2 == "?":
            return 1
        elif s1 == s2:
            return 0
        else:
            return 1