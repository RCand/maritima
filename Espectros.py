from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft

__author__ = "Riccardo Candeago, Ugr, E.T.S.I.C.C.P., aa. 2015/16"

def coeficientes(elev):
    """
    Da los coeficientes obtenidos de la transformada discreta de Fourier (discrete Fourier transform).
    [http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.fftpack.fft.html]

    Parameters
    ----------
    elev : array_like
        Array de las elevaciones del cual hay que hacer la transformada de Fourier.

    Returns
    -------
    coef : ndarray
        Array de los coeficientes.

    Notes
    -----
    The packing of the result is "standard": If ``A = fft(a, n)``, then
    ``A[0]`` contains the zero-frequency term, ``A[1:n/2]`` contains the
    positive-frequency terms, and ``A[n/2:]`` contains the negative-frequency
    terms, in order of decreasingly negative frequency. So for an 8-point
    transform, the frequencies of the result are [0, 1, 2, 3, -4, -3, -2, -1].

    """
    G = fft(elev)/N  # Vector de coeficientes

    # Frecuencias
    gn = G[2:N/2+1]  # Frecuencias positivas
    g_n = G[N/2+2:]  # Frecuencias negativas

    a0 = G[0]        # Valor medio = mean(eta)
    an = 2*gn.real   # Coefs. reales: los del coseno.
    bn = -2*gn.imag

    # Anado los dos vectores
    a_tot = np.append(a0**2, an**2+bn**2)

    coef = np.sqrt(a_tot.real)

    return coef

# Lectura archivo .dat y creacion array
path = 'datos.dat'  # Path para el archivo .dat (en Windows, es del tipo 'C:/Users/User/Folder/Archivo.dat')
# Se crea el array de datos
datos = np.fromfile(path, sep="\n")
'''
Para crear el array con el que se trabajará, se utiliza np.fromfile(file, dtype=float, count=-1, sep='').
Ya tenemos el *file*, que es dado del path, el *dtype* en este caso es ya *float* por default (numeros reales),
*count* es -1 por default, en el sentido que carga hasta el indice -1 (o sea el ultimo),
el *sep* es el separador, en este caso "\n", el "línea nueva".
'''

# Los datos se refieren a alturas de olas
t = datos[0::4]
eta_1 = datos[1::4]
eta_2 = datos[2::4]
eta_3 = datos[3::4]

# Periodo de mostreo Ts
Ts = t[1]-t[0]     # 40 Hz
N = len(eta_1)

# Costantes
T = N*Ts  # Tiempo de midura
Df = 1/T  # Resolucion espectral
rho = 1025  # densidad
g = 9.81    # gravedad

# vector de frecuencias
fn = np.arange(0.0, N/2*Df, Df)  # Original

# coeficientes
cn_1 = coeficientes(eta_1)
cn_2 = coeficientes(eta_2)
cn_3 = coeficientes(eta_3)

# Energias
En_1 = 0.5*rho*g*cn_1**2/Df
En_2 = 0.5*rho*g*cn_2**2/Df
En_3 = 0.5*rho*g*cn_3**2/Df

# Grafico tiempo vs. altura de ola
plt.plot(t, eta_1, label="eta_1 vs. tiempo")
plt.plot(t, eta_2, label="eta_2 vs. tiempo", color='g')
plt.plot(t, eta_3, label="eta_3 vs. tiempo", color='r')
plt.xlabel('Tiempo (s)')         #Etiqueta del eje x
plt.ylabel('eta (m)')            #Etiqueta del eje y
plt.grid()
plt.legend()
plt.show()

# TEST
'''
Una manera mas simple de hacer todo?
[http://docs.scipy.org/doc/numpy/reference/routines.fft.html]
'''
A = fft(eta_1)
Energy = np.abs(A)**2
plt.plot(Energy)
plt.show()

def plot_espectro(En, sensor):
    '''
    Funcion que hace el grafico del espectro del correspondiente sensor.
    :param En: np.array() or list
                Vector de las energias.
    :param sensor: int
                Numero del sensor.
    :return: Grafico del espectro.
    '''
    # Grafico eta
    plt.title("Espectro de energia  WG%s" % (sensor))
    plt.plot(fn, En)
    plt.xlabel('Frequencias (Hz)')            # Etiqueta del eje x
    plt.ylabel('Energia (Kg/s)')     # Etiqueta del eje y
    plt.grid()
    fig_name_sigma = 'Espectro_WG%s.pdf' % (sensor)
    plt.savefig(fig_name_sigma)
    plt.show()

plot_espectro(En_1, 1)
plot_espectro(En_2, 2)
plot_espectro(En_3, 3)