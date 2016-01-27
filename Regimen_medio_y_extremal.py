from __future__ import division
# (hacer ctrl + clic sobre el nombre del modulo para ver el codigo)
import numpy as np
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
umbral_wei = 0.01  # Probabilidad de EXCEDENCIA para fitting de Weibull a la CDF.
umbral_GEV = 0.01  # Probabilidad de EXCEDENCIA para fitting de GEV a la CDF.
umbral_picos = 5.  # Umbral sobre el cual los picos vienen representados en el grafico
umbral_maquinaria = 1.5  # Umbral sobre el cual la maquinaria no puede trabajar.
K_s = 0.9944  # Coeficiente de asomeramiento.
K_R = 0.9096  # Coeficiente de refraccion.
##########################

# Lectura archivo .dat y creacion array
# path = 'WANA_T_2020013 Motril 2 mod.dat'  # Path para el archivo .dat
path = 'SIMAR_1052048.dat'
datos = np.fromfile(path, sep="\n")
'''
Para crear el array con el que se trabajará, se utiliza np.fromfile(file, dtype=float, count=-1, sep='').
Ya tenemos el *file*, que es dado del path, el *dtype* en este caso es ya *float* por default (numeros reales),
*count* es -1 por default, en el sentido que carga hasta el indice -1 (o sea el ultimo),
el *sep* es el separador, en este caso "\n", el "línea nueva".
'''

'''
 LISTA DE PARAMETROS

 Hm0    : Altura significante Espectral                  (m)
 Tm02   : Periodo Medio Espectral Momentos 0 y 2         (s)
 Tp     : Periodo de pico espectral                      (s)
 DirM   : Direccion Media de PROCEDENCIA del Oleaje      (0=N,90=E)

 Hm0_V  : Mar de viento: Altura Signifcante Espectral    (m)
 DirM_V : Mar de Viento: Direccion Media de PROCEDENCIA  (0=N,90=E)

 Hm0_F1 : Mar de Fondo 1: Altura Significante Espectral  (m)
 Tm02_F1: Mar de Fondo 1: Periodo Medio Espectral        (s)
 DirM_F1: Mar de Fondo 1: Direccion Media de PROCEDENCIA (0=N,90=E)

 Hm0_F2 : Mar de Fondo 2: Hm0                            (m)
 Tm02_F2: Mar de Fondo 2: Periodo Medio Espectral        (s)
 DirM_F2: Mar de Fondo 2: Direccion Media de PROCEDENCIA (0=N,90=E)

 VelV   : Velocidad Media del Viento                     (m/s)
 DirV   : Direccion Media de PROCEDENCIA del Viento      (0=N,90=E)
'''

# Fechas  AA MM DD HH. Para crear el formato datetime se necesitan numeros int, no float, y por eso se
# hace la conversion con el metodo .astype(int)
AA = datos[0::18].astype(int)
MM = datos[1::18].astype(int)
DD = datos[2::18].astype(int)
HH = datos[3::18].astype(int)

# Se crea el array t, utilizando datetime. El formato es: 1996-01-14 06:00:00
# Transformo la lista en array de NumPy porque la necesito para hacer la mascara booleana
# en Hm0[(t >= t_ini) & (t < t_fin) & (t_fin <= t_ultimo)]
t = np.array([datetime(AA[i], MM[i], DD[i], HH[i]) for i in range(len(AA))])

# Cargar otros parametros.
Hm0_sin_alfa = datos[4::18]

# Factor alfa, que multiplica las alturas ola.
alfa = ((23 + 16 + 16 + 9 + 27) / 5) ** (1 / 7)
# alfa = 1
# Multiplicamos por alfa las alturas de ola.
Hm0 = alfa * Hm0_sin_alfa

DirM = datos[7::18]
VelV = datos[16::18]
DirV = datos[17::18]

# No hace falta de estos parametros
# Tm02 = datos[5::18]
# Tp = datos[6::18]
# Hm0_V = datos[8::18]
# DirM_V = datos[9::18]
# Hm0_F1 = datos[10::18]
# Tm02_F1 = datos[11::18]
# DirM_F1 = datos[12::18]
# Hm0_F2 = datos[13::18]
# Tm02_F2 = datos[14::18]
# DirM_F2 = datos[15::18]

# Encontrar todos los picos (maximos relativos) de la serie.
'''
Se utiliza scipy.signal.argrelextrema,
[http://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.signal.argrelextrema.html]

argrelextrema(data, comparator, axis=0, order=1, mode='clip')

order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
Aqui he puesto order=5 para que los *plateaux* sean considerados picos.

Example
---------
>>> import numpy as np
>>> from scipy.signal import argrelextrema

>>> x = np.random.random(12)

>>> # for local maxima
>>> argrelextrema(x, np.greater)

>>> # for local minima
>>> argrelextrema(x, np.less)

de [http://stackoverflow.com/questions/4624970/finding-local-maxima-minima-with-numpy-in-a-1d-numpy-array]
'''
# Para los maximos locales
indice_picos = argrelextrema(Hm0, np.greater, order=5)
H_picos = Hm0[indice_picos]
# Para encontrar la fecha correspondiente
t_picos = t[indice_picos]

# Para los minimos locales
indice_minimos = argrelextrema(Hm0, np.less, order=5)
H_minimos = Hm0[indice_minimos]
t_minimos = t[indice_minimos]

# Numero de anos: final (el elemento [-1] es el ultimo) menos el inicial
numoyears = AA[-1] - AA[0]

# Se crean dos listas que van a contener los maximos annuales y su fecha.
H_annuales = []
t_annuales = []

for n in range(numoyears):
    '''
    Para cada ano se hace la busqueda de los maximos y de su respectiva fecha.
    Se han encotrado tres metodos para hacerlo, los tres validos, solo que el seguno utiliza meno codigo (hay un bucle for
    de menos) y el tercero aun meno.

    Parameters
    ----------
    numoyears : int
        numero de anos considerados. El ano empieza el 1 de Octubre y se acaba el 30 de Septiembre.


    Returns
    ----------
    H_annuales : list
        lista de las alturas maximas annuales.

    t_annuales : list
        lista de las fechas correspondientes a las alturas maximas annuales.
    '''
    t_ini = datetime(AA[0] + n, 10, 1)  # Date(AA[0]+n,10,1). El ano empieza el 1 Octubre.
    t_fin = datetime(AA[0] + n + 1, 10, 1)  # Date(AA[0]+n+1,10,1)
    t_primero = datetime(AA[0], MM[0], DD[0])  # El primer anio ha de ser completo. Pues t_ini >= t_primero.
    t_ultimo = datetime(AA[-1], MM[-1], DD[-1])  # Controlar que el ultimo anio sea completo. Por eso t_fin <= t_ultimo.
    t_pico_ultimo = t_picos[-1]  # La fecha del ultimo pico

    '''
    ## Metodo 1
    posiciones = []
    tiempoMask = []
    # Busca los indeces (find() de matlab)
    for i, tiempo in enumerate(t):
        if tiempo >= t_ini and tiempo < t_fin and t_fin <= t_ultimo:  # mat_type['fecha'][i]>= t_ini and mat_type['fecha'][i]< t_fin:
            posiciones.append(i)
            tiempoMask.append(tiempo)  # Se hace una "mascara", asi que obtenemos los tiempos correctos.
    # Busqueda del Hm0 maximo y para hacer el diagrama (punto rojo en el valor extremal).
    Hm0_max = max(Hm0[posiciones])

    # Busca el indice donde se ha encontrado el Hm0 maximo, PERO es el indice que va de 0 hasta len(posiciones).
    indice_max = np.argmax(Hm0[posiciones])
    H_annuales.append(Hm0_max)  # Anade a H_annuales el valor de Hm0 maximo encontrado.
    # Anade el istante corrispondiente al valor Hm0 maximo.
    t_annuales.append(tiempoMask[indice_max])
    '''

    ## Metodo 2
    # Se crea una mascara booleana (True y False).
    # Las condiciones son:
    # * t >= t_ini
    # * t < t_fin
    # * t_fin <= t_ultimo -> Controlar que el ultimo ano sea completo.
    mascara_booleana = (t >= t_ini) & (t < t_fin) & (t_ini >= t_primero) & (t_fin <= t_ultimo)
    # El indice es relativo a la mascara creada.
    indice_max = Hm0[mascara_booleana].argmax()

    # El indice absoluto es el relativo mas la suma de los indices anteriores
    indice_abs = indice_max + len(Hm0[t < t_ini])
    # Se anaden los valores a los arrays H_annuales y t_annuales.
    H_annuales.append(Hm0[indice_abs])
    t_annuales.append(t[indice_abs])


    '''
    ## Metodo 3 - con los picos relativos (AUN NO FUNCIONA)
    # Se crea una mascara booleana (True y False).
    # Las condiciones son:
    # * t_picos >= t_ini
    # * t_picos < t_fin
    # * t_pico_ultimo <= t_ultimo -> Controlar que el ultimo ano sea completo.

    mascara_booleana = (t_picos >= t_ini) & (t_picos < t_fin) & (t_pico_ultimo <= t_ultimo)
    # Se anaden los valores a los arrays H_annuales y t_annuales, despues de buscar el maximo con .max().
    H_annuales.append(H_picos[mascara_booleana].max())
    t_annuales.append(t_picos[(H_picos == H_annuales[n]) & (mascara_booleana)])
    '''

# Se converten en array NumPy (para tener lo mas posible arrays NumPy en el codigo).
H_annuales = np.array(H_annuales)
t_annuales = np.array(t_annuales)

# Se imprimen a la pantalla los datos hallados.
print("-----------------------------------------------------")
print("Maximo annual (m) - Fecha (YYYY-MM-DD HH:MM:SS)")
for i, H_max_annual in enumerate(H_annuales):
    print("    %.4f        -      %s" % (H_max_annual, t_annuales[i]))
print("Numero de maximos=", len(H_annuales))
print("-----------------------------------------------------")


# Maximos annuales y relativos sobre umbral en el mismo array.
'''
Si quiero considerar los maximos annuales mas los picos arriba del umbral, considero el array H_max_ann_rel y
los tiempos t_max_ann_rel (maximo annuales y relativos).

En los picos relativos (maximos relativos), ya hay los maximos annuales, menos los que estan abajo del valor umbral.
Entonces anado al vector los picos relativos que estan arriba del umbral mas los maximos annuales que estan abajo del
umbral(H_annuales < umbral_picos).

Utilizar ese codice solo si hace falta. Si no es necesario comentarlo.
'''
# Uno las alturas maximas annuales y de los picos. Para la analisis no los necesito ordenados segun la fecha:
# despues se hace x.sort(), o sea, se ordenan despues segun altura.
H_max_ann_rel = np.append(H_picos[H_picos >= umbral_picos], H_annuales[H_annuales < umbral_picos])
# Uno los fechas de los maximos annuales y de los picos, y los ordeno. (fechas y alturas no se corresponden!)
t_max_ann_rel = np.append(t_picos[H_picos >= umbral_picos], t_annuales[H_annuales < umbral_picos])
t_max_ann_rel.sort()


# Se grafica la CDF (Cumulative Distribution Funcion).
'''
El procedimiento es lo mismo del ejemplo que se halla en la documentacion del modulo
statsmodels.distributions.empirical_distribution.ECDF a partir de la linea 172 hasta
el final (se puede ver el codigo haciendo ctrl+clic sobre el el nombre cuando se lo importa, o en el link abajo).
No hay las lineas rojas dadas par el codigo (arriba y abajo de la *step funcion*)
> lower, upper = _conf_set(F)
> plt.step(x, lower, 'r')
> plt.step(x, upper, 'r')
porque no eran necesarias.

[http://statsmodels.sourceforge.net/0.6.0/_modules/statsmodels/distributions/empirical_distribution.html#ECDF]
'''

fig, ax = plt.subplots()
# Hay que hacer una copia con .copy() de H_annuales, porque si no lo hago, modifico H_annuales mismo.
# H_annuales me hace falta para el grafico tiempo vs. altura de ola.
# nota: con los arrays de NumPy, no es suficiente hacer una copia con x = H_annuales[:]

flag_box = False  # Se pone False por default. No comentar. Se utiliza en los textos del grafico ECDF.
######ELEGIR CUAL x UTILIZAR Y COMENTAR LAS OTRAS###########
# x = H_annuales.copy()  # Para analizar los maximos annuales
# x = H_max_ann_rel.copy()  # Para analizar Maximos annuales y relativos sobre umbral.
# x = H_picos[H_picos >= umbral_picos].copy()  # Para analizar todos los picos sobre el umbral
                                               # (no se consideran los maximos annuales abajo del umbral).
x = Hm0.copy()  # Para hacer el analisis de regimen medio. Poner tambien flag_box = True
flag_box = True  # Comentar si se hace el regimen extremal.
############################################################

# Me hara falta el maximo de x para dimensionar los graficos (anchura del x_w).
x_max = max(x)
cdf = ECDF(x)
x.sort()
F = cdf(x)
# funcion "escalera"
plt.step(x, F, label="ECDF")

# Limites del grafico
plt.xlim(-0.1, x_max * 1.05)
plt.ylim(-0.1, 1.05)
plt.title("ECDF")
plt.xlabel("Alturas (m)")
plt.ylabel("Cuantiles")

# Se utiliza el metodo de la maxima verosimilitud para hacer el fitting (MLE maximum liklihood),
# en particular el metodo scipy.stats.rv_continuous.fit
'''
(leer las notas del link abajo)

Notes
-----
This fit is computed by maximizing a log-likelihood function, with
penalty applied for samples outside of range of the distribution. The
returned answer is not guaranteed to be the globally optimal MLE, it
may only be locally optimal, or the optimization may fail altogether.

[http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.stats.rv_continuous.fit.html#scipy.stats.rv_continuous.fit]
'''
# Weibull (exponweib)
'''
Se utiliza la scipy.stats.exponweib de SciPy.
[http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.stats.exponweib.html#scipy.stats.exponweib]

La funcion pdf (probability distribution funcion) es:
exponweib.pdf(x, a, c) =
    a * c * (1-exp(-x**c))**(a-1) * exp(-y**c)*x**(c-1)

The probability density above is defined in the “standardized” form.
To shift and/or scale the distribution use the loc and scale parameters.
Specifically, exponweib.pdf(x, a, c, loc, scale) is identically equivalent to exponweib.pdf(y, a, c)
/ scale with y = (x - loc) / scale.

Haciendo el integral de la pdf se puede hallar la expresion de la cdf.
(1 - exp( -y**c  ))**a + const

Pues ponemos:
* y = (x - loc) / scale
* c -> parametro de forma (shape)

(1 - exp( -( (x-loc)/scale )**shape  ))**a

Confrontamos con el documento "BANCO DE DATOS OCEANOGRAFICOS DE PUERTOS DEL ESTADO", AREA DE MEDIO FISICO, www.puertos.es"
(se pone el pedice _w para distinguirla de la GEV, que se vee mas adelante).
* a=a_w=1, parametro que es f0=1.
* A = scale_w, parametro de escala
* B = loc_w, parametro de centrado y "su valor ha de
ser menor que el menor de los valores justados". Aqui se pone floc=0.
* C = shape_w,  parametro de forma, "C es el parametro de forma y suele
moverse entre 0.5 y 3.5"
'''
a_w, shape_w, loc_w, scale_w = exponweib.fit(x, floc=0, f0=1)

# Se crea vector de puntos en el eje x para el grafico.
# np.linspace(start, stop, num=50, endpoint=True, retstep=False)
x_w = np.linspace(0, x_max * 2, 300)

# Se evalua la CDF para los valores de x
y_w = exponweib.cdf(x_w, a_w, shape_w, loc=loc_w, scale=scale_w)

# Grafico de la ECDF
plt.plot(x_w, y_w, color="r", label="fitted CDF (Weibull)")

# Tabla con datos
props_w = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5}
textstr_w = "ECDF con Weibull \nParametro de forma={0}\nParametro de centrado = {1} \nParametro de escala = {2}"\
            .format(shape_w, loc_w, scale_w)
# Para modificar la posicion de la tabla, modficar los dos primeros parametros.
# En el caso del regimen medio, se desplaza la tabla con los datos.
if(flag_box == True):
    ax.text(0.4, 0.60, textstr_w, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props_w)
else:
    ax.text(0.05, 0.75, textstr_w, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props_w)

# Inversion de la funcion de Weibull (con interpolacion linear)
'''
La cdf es por su naturaleza monotona, pues invertible.
ver [http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.interpolate.interp1d.html]

Examples
--------
>>> import matplotlib.pyplot as plt
>>> from scipy import interpolate
>>> x = np.arange(0, 10)
>>> y = np.exp(-x/3.0)
>>> f = interpolate.interp1d(x, y)

>>> xnew = np.arange(0, 9, 0.1)
>>> ynew = f(xnew)   # use interpolation function returned by `interp1d`
>>> plt.plot(x, y, 'o', xnew, ynew, '-')
>>> plt.show()
'''
weibull_inv_il = interp1d(y_w, x_w)
# Imprime a la pantalla el resultado.
print("Con un umbral de {0}, curva de Weibull, se obtiene una altura de {1} m (interpolacion linear)"\
      .format(umbral_wei, weibull_inv_il(1 - umbral_wei)))

# Inversion de la funcion de Weibull (directamente de la formula )
def weibull_inv(y):
    '''
    Funcion inversa de weibull

    Parameters
    ----------
        y : float
            Cuantil o probabilidad de no EXCEDENCIA.

    Returns
    __________
        x : float
            Altura correspondiente al cuantil o probabilidad de NO EXCEDENCIA.
    '''
    x = scale_w * (-np.log(1 - y))**(1/shape_w) + loc_w
    return x
print("Con un umbral de {0}, curva de Weibull, se obtiene una altura de {1} m (inversion formula)"\
      .format(umbral_wei, weibull_inv(1-umbral_wei)))

# Aun no funciona: inversion con invweibull.cdf()
# print("Con un umbral de {0}, curva de Weibull, se obtiene una altura de {1} m (inversion formula)".format(umbral_wei,\
#       invweibull.cdf(1-umbral_wei, shape_w)))


# GEV
'''
Se utiliza scipy.stats.genextreme
[http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.stats.genextreme.html]

La pdf es:
genextreme.pdf(x, c) =
    exp(-exp(-x))*exp(-x),                    for c==0
    exp(-(1-c*x)**(1/c))*(1-c*x)**(1/c-1),    for x <= 1/c, c > 0

Integrando la pdf se obtiene la cdf:
    exp(-exp(-x)) + const,                    for c==0
    exp(-(1-c*x)**(1/c)) + const,             for x <= 1/c, c > 0


The probability density above is defined in the “standardized” form.
To shift and/or scale the distribution use the loc and scale parameters.
Specifically, genextreme.pdf(x, c, loc, scale) is identically equivalent
to genextreme.pdf(y, c) / scale with y = (x - loc) / scale.

Los parametros seran: c1, loc1 y scale.
'''
# fitting con GEV
c1, loc1, scale1 = genextreme.fit(x)

# Se crea vector de puntos en el eje x para el grafico
x_GEV = np.linspace(0, x_max * 2, 300)
# Se evalua la CDF para los valores de x
y_GEV = genextreme.cdf(x_GEV, c1, loc=loc1, scale=scale1)

# Inversion de la funcion GEV (ver arriba para explicaciones)
GEV_inv_il = interp1d(y_GEV, x_GEV)
# Imprimir a la pantalla los resultados.
print("Con un umbral de {0}, curva GEV, se obtiene una altura de {1} m"\
      .format(umbral_GEV, GEV_inv_il(1 - umbral_GEV)))

# Grafico de la CDF con GEV
ax.plot(x_GEV, y_GEV, color="black", label="fitted CDF (GEV)")

# Texto para el grafico
props_gev = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5}
textstr_gev = "ECDF con GEV \nParametro de forma={0}\nParametro de centrado = {1} \nParametro de escala = {2}"\
            .format(c1, loc1, scale1)
# Para modificar la posicion de la tabla, modficar los dos primeros parametros.
# En el caso del regimen medio, se desplaza la tabla con los datos.
if(flag_box == True):
    ax.text(0.4, 0.80, textstr_gev, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props_gev)
else:
    ax.text(0.05, 0.95, textstr_gev, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props_gev)

plt.legend(loc='lower right')
plt.grid()
plt.show()

# histograma maximos anuales.
plt.hist(x, bins=20)
plt.title("Histograma alturas")
plt.xlabel("Alturas (m)")
plt.ylabel("# Ocurrencias")
plt.show()

# histograma alturas Hm0 (normalizado) con pdf (probability distribution funcion) de Weibull y GEV

# Weibull
y_w = exponweib.pdf(x_w, a_w, shape_w, loc=loc_w, scale=scale_w)
plt.plot(x_w, y_w, color="r", label="fitted pdf (Weibull)")

# GEV
y_GEV = genextreme.pdf(x_GEV, c1, loc=loc1, scale=scale1)
plt.plot(x_GEV, y_GEV, color="black", label="fitted pdf (GEV)")


# Hallar numero de dias en los cuales no se puede trabajar con la maquinaria.
# Umbral sobre el cual no se puede trabajar propagado en profundidades indefinidas
umbral_maquinaria0 = umbral_maquinaria / (K_R * K_s)
# Buscar las alturas que estan sobre el umbral_maquinaria0 y ponerlas en H_sobre_umbral
# Se consideran solo anios completos (que empiezen el 1 enero y termine el 31 diciembre).
'''
Analizo los casos posibiles:
    * Fecha inicial. El anio ha que empezar el YYYY-01-01
    Tengo 2 casos:
        * La primera fecha es, p. ej., el 1958-01-05, que esta antes del 1958-10-01:
        mi tiempo inicial sera el 1958-01-05, o sea, el AA[0]-10-1
        * La primera fecha es, p. ej., el 1958-12-05, que esta despues del 1958-10-01:
        mi tiempo inicial sera el anio despues, el 1959-10-01, que esta despues del 1958-10-01, o sea, AA[1]-10-1
    * Fecha final. El anio ha que terminar el YYYY-09-30
    Tengo 2 casos:
        * La ultima fecha es, p. ej., el 2014-08-05, que esta antes del 1958-09-30:
        el anio no es completo. Mi tiempo final sera el 2013-09-30, o sea, el AA[-1]-1-03-30
        * La ultima fecha es, p. ej., el 2014-12-05, que esta despues del 1958-09-30:
        mi tiempo inicial sera el mismo anio, el 2014-09-30, o sea, AA[-11]-09-30

'''
# t == datetime(AA[0], 1, 1) es una mascara booleana. Se mira si por lo menos uno es True con .any()
if (t == datetime(AA[0], 1, 1)).any():
    t_ini_abs = t[t == datetime(AA[0], 1, 1)][0]
else:
    t_ini_abs = t[t == datetime(AA[0]+1, 1, 1)][0]

if (t == datetime(AA[-1], 12, 31)).any():
    t_fin_abs = t[t == datetime(AA[-1], 12, 31)][0]
else:
    t_fin_abs = t[t == datetime(AA[-1]-1, 12, 31)][0]

t_sobre_umbral = t[(Hm0 >= umbral_maquinaria0) & (t >= t_ini_abs) & (t <= t_fin_abs)]
# Numero de dias. En un dia hay 8 medidas (una cada 3 horas), pero en la segunda parte de los datos uno cada hora.
# Elimino dal dato Datetime las horas y me quedo solo con YYYY-MM-DD.
t_sobre_umbral_sin_horas = np.array([datetime(dt.year, dt.month, dt.day) for i, dt in enumerate(t_sobre_umbral)])

# Numero de dias = numero de dias singulos (np.unique )que hai en la lista. Si aperece mas veces la misma fecha, se
# conta una sola vez.
'''
Ejemplo de np.unique()

>>> np.unique([1, 1, 2, 2, 3, 3])
array([1, 2, 3])
>>> a = np.array([[1, 1], [2, 3]])
>>> np.unique(a)
array([1, 2, 3])
'''
N_dias = len(np.unique(t_sobre_umbral_sin_horas))
# Numero total de anios
N_anios = t_fin_abs.year - t_ini_abs.year
# Numero medio de dias al anio en los cuales no se puede trabajar.
N_dias_no_trabajo = N_dias/N_anios

print("Con un umbral de altura de trabajo de la maquinaria de  {2} m,\
        \nel numero medio de dias al anio en los cuales no se puede trabajar es de {0}, o sea el {1:.1f}%"\
        .format(N_dias_no_trabajo, N_dias_no_trabajo/365.242*100, umbral_maquinaria))

# Histograma alturas maximas annuales.
plt.hist(Hm0, normed=True, bins=20, label="Alturas (m)")
plt.hist(H_annuales, normed=True, bins=20, label="Alturas maximas \nannuales (m)")
plt.title("Histograma alturas")
plt.xlabel("Alturas (m)")
plt.ylabel("# Ocurrencias")
plt.legend(loc='center right')
plt.show()

# Diagrama Alturas - tiempo.
# Grafico tiempo vs. altura de ola.
plt.plot(t, Hm0)
# Imprime a pantalla la recta umbral
plt.axhline(y=umbral_picos, color='g')
# Imprime a pantalla SOLO los picos que sodisfan la relacion H_picos >= umbral_picos
plt.plot(t_picos[H_picos >= umbral_picos], H_picos[H_picos >= umbral_picos], 'go')
plt.plot(t_annuales, H_annuales, 'ro')
plt.title("Maximos anuales detectados \n Altura significante - tiempo")
plt.xlabel('Tiempo (s)')  # Etiqueta del eje x
plt.ylabel('H_s (m)')  # Etiqueta del eje y
plt.grid()
# Salva el grafico en la carpeta donde se trabaja en formato .pdf (se puede cambiar el formato).
plt.savefig('altura_tiempo.pdf')
plt.show()

# Hist velocidad viento.
plt.hist(VelV)
plt.title("Histograma velocidad viento")
plt.xlabel("Velocidades (m/s)")
plt.ylabel("# Ocurrencias")
plt.show()

# Hist direcciones viento.
plt.hist(DirV)
plt.title("Histograma direcciones viento")
plt.xlabel("Direcciones (grados)")
plt.ylabel("# Ocurrencias")
plt.show()

# Crear variables de direccion y velocidad del viento.
ws = VelV  # wind speed
wd = DirV  # wind direction

# Velocidad y direccion del viento.
ax = WindroseAxes.from_ax()
ax.bar(wd, ws, normed=True)
ax.set_legend()
plt.title("Velocidad del viento")
plt.show()

# Altura olas rosa.
ax = WindroseAxes.from_ax()
ax.bar(DirM, Hm0, normed=True)
ax.set_legend()
plt.title("Altura del oleaje")
plt.show()