import os
import numpy as np
import matplotlib.pyplot as plt

from settings import MEDIA_ROOT


# I have numpy 2.0.0 on my machines. Comment this out if using earlier numpy
np.seterr(all='ignore')

class CurveFit:
    def __init__(self, model, var, xdata, ydata):
        self.model = model
        self.param = var
        self.var = var
        self.x = xdata
        self.y = ydata
        self.m = []
        self.d = []

    def equation(self):
        if self.model == "ic50":
            self.m = 1 - (self.var[0]/
                     (1 + (self.var[1]/self.x) ** self.var[2]))

    def derivatives(self):
        if self.model == "ic50":
            d1 = -(1/(1 + (self.var[1] / self.x) ** self.var[2]))
            d2 = ((self.var[0] * self.var[2]  * 
                  (self.var[1] / self.x) ** (self.var[2] - 1))/
                  (self.x * (1 + (self.var[1] / self.x) ** self.var[2]) ** 2))
            d3 = (self.var[0] * (self.var[1]/self.x) ** self.var[2] * 
                  np.log(self.var[1]/self.x))/(1 + 
                  (self.var[1]/self.x) ** self.var[2]) ** 2
            self.d = [d1, d2, d3]
            
    def get_f(self):
        self.equation()
        return self.y - self.m
        
    def get_jac(self):
        args = []
        self.derivatives()
        for i in self.d:
            args.append(i)
        jt = np.array(args)
        return -1 * jt.T
        
    def levenberg_marquardt(self):
        N = len(self.var)
        k = 0
        v = 2
        J = self.get_jac()
        f = self.get_f()
        a = np.dot(J.T, J)
        g = np.dot(J.T, f)
        mu = 1.0e-3 * max(np.diag(a))
        while np.linalg.norm(g, np.inf) >= 1.0e-15 and k < 200:
            k += 1
            muI = mu * np.eye(N)
            h = np.linalg.solve((a + muI), -g)
            self.param = [i for i in self.var]
            self.var += h
            if np.linalg.norm(self.var - self.param) <= 1.0e-20:
                return (k, self.var)
            f_new = self.get_f()
            dF1 = np.dot(f.T, f)
            dF2 = np.dot(f_new.T, f_new)
            
            dF = 0.5 * (dF1 - dF2)
            dL = 0.5 * np.dot(h.T, ((mu * h) - g))
            d = dF/dL
            if d > 0:
                J = self.get_jac()
                f = f_new
                a = np.dot(J.T, J)
                g = np.dot(J.T, f)
                mu *= max(1.0/3.0, (1 - (2 * d - 1) ** 3))
                v = 2
            else:
                self.var = self.param[:]
                mu *= v
                v *= 2
        return (k, self.var)
        
    def plot(self):
        plt.clf()
        # swap input data with data for a smooth curve
        xdata = [i for i in self.x]
        self.x = np.arange(min(xdata), max(xdata), 
                           (max(xdata) - min(xdata))/10000)
        self.equation()
        plt.plot(self.x, self.m, 'k', xdata, self.y, 'o', lw=2, ms=12, 
                 mec='k', mew=1, mfc='None')
        plt.xticks(size = 18)
        plt.yticks(size = 18)
        if self.model == "ic50":
            plt.xscale('log')
        plt.ylim((min(self.y) - max(self.y) * 0.2), 
                 (max(self.y) + max(self.y) * 0.2))
        plt.xlabel("xlab", fontsize=24)
        plt.ylabel("ylab", fontsize=24)
        plt.subplots_adjust(bottom=0.15)
        plotfile = os.path.join(MEDIA_ROOT, "temp.png")
        plt.savefig(plotfile, dpi=80)
        self.x = xdata