from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

k = np.linspace(0.0001, 0.5, 600)
g = 9.81
h = 1
sigma = 0.36
umbral_alt = 0.95
Hs = 13

# Inversa de la cdf de Rayleight
def rayleight_cdf_inv(y, Hs):
    '''
    Funcion inversa de la cdf de Rayleight

    Su formula es::
        x = Hs * np.sqrt(-np.log(y)/2)

    Parameters
    ----------
        y : float
            Cuantil o probabilidad de NO EXCEDENCIA.
        Hs : float
            Altura de ola significante.
    Returns
    __________
        x : float
            Altura correspondiente al cuantil o probabilidad de EXCEDENCIA.
    '''
    x = Hs * np.sqrt(-np.log(y)/2)
    return x

# Imprimir a pantalla la altura y el umbral de EXCEDENCIA.
print("Con un umbral de {0}, curva de Rayleight, se obtiene una altura de {1} m "\
        .format(umbral_alt, rayleight_cdf_inv(1-umbral_alt, Hs)))

def k2s(k):
    s = (g*k*np.tanh(h*k))**(1/2)
    return s

# Inversion
s = k2s(k)
a = np.argsort(s)
s2k = interp1d(s[a], k[a])
# plt.plot(s, k, 'o', xnew, ynew, '-')
# plt.show()

print("k={0}, kh={1}, para sigma={2}, con interpolacion linear".format(s2k(sigma), s2k(sigma)*h, sigma))
k_dado = 0.088
print("dado k={0}, sigma={1}, T={2}".format(k_dado, k2s(k_dado), 2*np.pi/k2s(k_dado)))
plt.plot(k, k2s(k))
plt.plot(k, sigma*np.ones(len(k)))
plt.show()

# Celeridad de una ola progresiva
def c(s, k):
    return s/k

# Celeridad de grupo
def cg(c, k, h):
    c_g = c/2*(1 + (2*k*h)/(np.sinh(2*k*h)))
    return c_g

c_g1 = cg(12.11, 0.052, 20)
c_g2 = cg(7.89, 0.080, 7)
print(cg(12.11, 0.052, 20))

# Da la presion maxima dinamica (en m c.d.a.) a la amplitud maxima
def p2A(p, k, h, z):
    A = p * np.cosh(k*h)/np.cosh(k*(z+h))
    return A

print(p2A(0.45, 0.052, 20, -15))

# Coeficiente de asomeramiento
def fK_s(c_g1, c_g2):
    return np.sqrt(c_g1/c_g2)

print(fK_s(c_g1, c_g2))