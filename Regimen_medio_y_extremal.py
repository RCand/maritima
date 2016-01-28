# coding: utf-8
from __future__ import division
# (hacer ctrl + clic sobre el nombre del modulo para ver el codigo)
import numpy as np
import pandas as pd
# Para el vector tiempo
from datetime import datetime
# Fitting ECDF
from statsmodels.distributions.empirical_distribution import ECDF
# Para inerpolar y hacer las funciones inversas.
from scipy.interpolate import interp1d
# ...con GEV (generalizada valores extremos) y Weibull
from scipy.stats import genextreme, exponweib
# # Inversa de weibull (no se utiliza, pero seria interesante).
# from scipy.stats import invweibull
# Para hacer la analisis de los maximos y minimos relativos
from scipy.signal import argrelextrema
# Para graficos
from matplotlib import pyplot as plt
# Rosa de vientos
from windrose import WindroseAxes, WindAxes

__author__ = "Riccardo Candeago, Ugr, E.T.S.I.C.C.P., aa. 2015/16"

### PARAMETROS A FIJAR ###
umbral_exced_wei = 0.01  # Probabilidad de EXCEDENCIA para fitting de Weibull a la CDF.
umbral_exced_GEV = 0.01  # Probabilidad de EXCEDENCIA para fitting de GEV a la CDF.
umbral_picos = 5.  # Umbral sobre el cual los picos vienen representados en el grafico
umbral_maquinaria = 0.  # Umbral sobre el cual la maquinaria no puede trabajar.
K_s = 0.9944  # Coeficiente de asomeramiento.
K_R = 0.9096  # Coeficiente de refraccion.
##########################

# Lectura archivo .dat y creacion dataframe
# path = 'WANA_T_2020013 Motril 2 mod.dat'  # Path para el archivo .dat
# na_values=[-99.9] porque los valores nulos tienen valor -99.9
path = 'SIMAR_1052048_wh.dat'
df = pd.read_table(path, delim_whitespace=True, parse_dates={'fecha': [0, 1, 2, 3]},\
                   keep_date_col=True, skiprows=78, skip_blank_lines=True,\
                   na_values=[-99.9])
# Poner la fecha como indice del dataframe
df = df.set_index('fecha')

# Eliminar las columnas AA,MM,DD,HH
df = df.drop(['AA', 'MM', 'DD', 'HH'], axis=1)

# Valores estatisticos del df
print(df.describe())

# Para los maximos locales
# Para acceder al valor de una columna del dataframe de pandas.
# argrelextrema(data, comparator, axis=0, order=1, mode='clip')
indice_picos = argrelextrema(df['Hm0'].values, np.greater)

# Serie (de Pandas) de los picos.
# Utilizo .iloc porque los indices son numeros interos (no son etiquetas).
s_picos = df['Hm0'].iloc[indice_picos]

# Para los minimos locales
indice_minimos = argrelextrema(df['Hm0'].values, np.greater)
# Serie (de Pandas) de los minimos.
s_minimos = df['Hm0'].iloc[indice_minimos]

# Range de fechas
###PROBLEMA: A-SEP: el anio termina el ultimo dia de septiembre.
# Crea un range de fechas que estan entro la fecha inicial y final de los datos.
rng = pd.date_range(start=df.index[0], end=df.index[-1], freq='A-SEP')
print("Range", rng)

# Pongo len(rng) - 1 porque evaluo n+1 en el bucle.
# lista de las fechas de los maximos annuales
t_annuales = []
# Busca el maximo de cada anio y pone su fecha en la lista t_annuales
for n in range(len(rng)-1):
    #### PROBLEMA:.loc note that contrary to usual python slices, both the start and the stop are included!)
    # Si el maximo anual fuese el 30 de septiembre, contaria en dos anios juntos, en realidad deberia entrar solo en uno
    # max_date = df['Hm0'].loc[rng[n]:rng[n+1]].argmax()
    # Si utilizo [start:stop], start esta INCLUIDO, stop NON INCLUIDO.
    max_date = df['Hm0'][rng[n]:rng[n+1]].argmax()
    t_annuales.append(max_date)

# Crea una serie de los maximos annuales y su relativa fecha, utilizada como indice.
sH_annuales = pd.Series(df['Hm0'].loc[t_annuales], index=t_annuales)

# Datos estatisticos sobre los maximos annuales
print(sH_annuales)
print(sH_annuales.describe())

# Plot Hm0
df['Hm0'].plot()
plt.xticks(rotation=30)
plt.show()