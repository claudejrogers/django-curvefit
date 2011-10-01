import numpy as np

# Equations for the models
def boltzmann_eq(x, var0, var1, var2, var3):
    return var0 + ((var1 - var0) / (1 + np.exp((var2 - x) / var3)))

def expdecay_eq(x, var0, var1, var2):
    return var0 + var1 * np.exp(-var2 * x)

def gaussian_eq(x, var0, var1, var2, var3):
    return var0 + var1 * np.exp(-(x - var2) ** 2 / var3 ** 2)

def hill_eq(x, var0, var1, var2):
    return var0 / (1 + (var1 / x)** var2)

def ic50_eq(x, var0, var1, var2):
    return 1 - (var0 / (1 + (var1 / x) ** var2))

def mm_eq(x, var0, var1):
    return (var0 * x) / (var1 + x)

def modsin_eq(x, var0, var1, var2):
    return var0 * np.sin(np.pi * (x - var1) / var2)

# Equations for the partial derivatives of the models
def boltzmann_pd(x, var0, var1, var2, var3):
    d1 = 1 - (1 / (1 + np.exp((var2 - x) / var3)))
    d2 = 1 / (1 + np.exp((var2 - x) / var3))
    d3 = (((var0 - var1) * np.exp((var2 + x) / var3)) 
            / (var3 * (np.exp(var2/var3) + np.exp(x / var3)) ** 2))
    d4 = (((var1 - var0) * (var2 - x) * np.exp((var2 - x) / var3)) / 
            (var3 ** 2 * (np.exp((var2 - x) / var3) + 1) ** 2))
    return [d1, d2, d3, d4]

def expdecay_pd(x, var0, var1, var2):
    d1 = x ** 0.0
    d2 = np.exp(-var2 * x)
    d3 = -x * var1 * np.exp(-var2 * x)
    return [d1, d2, d3]

def gaussian_pd(x, var0, var1, var2, var3):
    d1 = x ** 0.0
    d2 = np.exp(-(x - var2) ** 2 / var3 ** 2)
    d3 = 2 * ((x - var2) / (var3 ** 2)) * var1 * np.exp(
        -(x - var2) ** 2 / var3 ** 2)
    d4 = 2 * ((x - var2) ** 2 / var3 ** 3) * var1 * np.exp(
        -(x - var2) ** 2/ var3 ** 2)
    return [d1, d2, d3, d4]

def hill_pd(x, var0, var1, var2):
    d1 = 1 / (1 + (var1 / x) ** var2)
    d2 = ((-var0 * var2 * var1 ** (var2 - 1)
            * x ** var2) / (var1 ** var2 + x ** var2) ** 2)
    d3 = ((var0 * (var1 * x) ** var2 * 
            np.log(x / var1)) / (var1 ** var2 + x ** var2) ** 2)
    return [d1, d2, d3]

def ic50_pd(x, var0, var1, var2):
    d1 = -(1 / (1 + (var1 / x) ** var2))
    d2 = ((var0 * var2 * (var1 / x) ** (var2 - 1))/
          (x * (1 + (var1 / x) ** var2) ** 2))
    d3 = (var0 * (var1 / x) ** var2 * np.log(var1 / x))/(1 + 
          (var1/x) ** var2) ** 2
    return [d1, d2, d3]

def mm_pd(x, var0, var1):
    d1 = x / (var1 + x)
    d2 = (-1) * (var0 * x) / (var1 + x) ** 2
    return [d1, d2]

def modsin_pd(x, var0, var1, var2):
    d1 = np.sin(np.pi * (x - var1) / var2)
    d2 = (-var0 * np.pi * np.cos(np.pi * (x - var1)  / var2)) / var2
    d3 = ((var0 * np.pi * (var1 - x) * np.cos(np.pi * 
          (x - var1) / var2)) / var2**2)
    return [d1, d2, d3]

