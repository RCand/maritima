from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
# Hay que descargar t_tide de [https://github.com/moflaher/ttide_py] porque no esta en la repository oficial.
from ttide.t_tide import t_tide

__author__ = "Riccardo Candeago, Ugr, E.T.S.I.C.C.P., aa. 2015/16"

'''
Hacer un analisi armonico:
determinar amplitudes y fases.

Asi puedo conocer elevacion en todos tiempos (en un punto fijo).
'''

# Lectura archivo .dat y creacion array
path = 'APSevilla.dat'  # Path para el archivo .dat (en Windows, es del tipo 'C:/Users/User/Folder/Archivo.dat')
# Se crea el array de datos
datos = np.fromfile(path, sep="\n")
'''
Para crear el array con el que se trabajará, se utiliza np.fromfile(file, dtype=float, count=-1, sep='').
Ya tenemos el *file*, que es dado del path, el *dtype* en este caso es ya *float* por default (numeros reales),
*count* es -1 por default, en el sentido que carga hasta el indice -1 (o sea el ultimo),
el *sep* es el separador, en este caso "\n", el "línea nueva".
'''

t = datos[0::2]  # Tiempos.
h = datos[1::2]  # Elevaciones.

# Nivel medio.
h_medio = np.mean(h)
eta = h-h_medio

'''
# Matriz 4201 x 2 (no es utilizada)
datos_m = np.array([t, eta])
'''

# Analisis Armonico

# Latitudine
lat_v = 37+19/60+57/(60*60)
t_muestreo_en_horas = 1

'''
Desde t_tide.t_tide,
[https://github.com/moflaher/ttide_py/blob/master/ttide/t_tide.py]

Returns
-------
nameu=list of constituents used
fu=frequency of tidal constituents (cycles/hr)
tidecon=[fmaj,emaj,fmin,emin,finc,einc,pha,epha] for vector xin
       =[fmaj,emaj,pha,epha] for scalar (real) xin
   fmaj,fmin - constituent major and minor axes (same units as xin)
   emaj,emin - 95
confidence intervals for fmaj,fmin
   finc - ellipse orientations (degrees)
   einc - 95
confidence intervals for finc
   pha - constituent phases (degrees relative to Greenwich)
   epha - 95
confidence intervals for pha
xout=tidal prediction

Notes
------
Pawlowicz, R., B. Beardsley, and S. Lentz, "Classical Tidal
"Harmonic Analysis Including Error Estimates in MATLAB
using T_TIDE", Computers and Geosciences, 28, 929-937 (2002).
'''
nameu, fu, tideconout, pout = t_tide(eta,
                                     dt=t_muestreo_en_horas,
                                     shallownames=['M10'],
                                     stime=t[0],
                                     lat=lat_v)

# pout es una matriz de 1 columna
residuo = [eta[i]-pout[i][0] for i in range(len(pout))]
pout_v = [pout[i][0] for i in range(len(pout))]

# Tiempo en fecha
# 1 dia -> 86400 s
# Trabajo con fechas float: para la conversion necesito los segundos.
# El segundo 0 es la fecha 1/1/1970.
# Utilizar print(datetime.toordinal( date(1970,1,1) ) ) para encontrar la fecha absoluta, que es 719163.

seconds = (t-719163)*86400
time = [datetime.fromtimestamp(seconds[i]) for i in range(len(seconds))]

# Plot
plt.plot(time, eta, color='blue', label="Datos originales")
line, = plt.plot(time, pout_v, color='g', label="Analisis armonico")
line, = plt.plot(time, residuo, color='r',  label="Residuo")
plt.title('Plot')
plt.xlabel('Fecha ')
plt.ylabel('Metros')
plt.grid()
plt.legend()
plt.show()