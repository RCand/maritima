from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
# from scipy.stats import rayleigh # Se podria utilizar tambien esta. Tiene formula: rayleigh.pdf(r) = r * exp(-r**2/2)

__author__ = "Riccardo Candeago, Ugr, E.T.S.I.C.C.P., aa. 2015/16"

### PARAMETROS A FIJAR ###
umbral_exced_alt = 0.05  # Probabilidad de EXCEDENCIA para fitting de Reileight a la CDF.
##########################

def crea_estado(eta, t, sensor):
    '''
    Dada una serie temporal de elevaiones, esta funcion crea el estado de mar.

    Parameters
    ----------
        eta : np.array() or list
            Elevaciones respecto al nivel medio (fiajdo a zero).
        t : np.array() or list
            Tiempos correspondentes a las elevaciones.
        sensor : int
            Numero del sensor.
    Returns
    ---------
        h : np.array()
            Vector de las alturas de las olas del estado de mar.
        T : np.array()
            Vector de los periodos de las olas del estado de mar.
    Notes
    ---------
        * Un periodo es el intervalo de tiempo entre dos cruces (eta[j] * eta[j - 1] <= 0)
        descendientes (eta[j - 1] >= eta[j]) por zero en el grafico eta-tiempo.
        Por eso se utiliza la condicion::
            j>0 and eta[j] * eta[j - 1] <= 0 and eta[j - 1] >= eta[j]
        (j>0 porque hay un indice j-1 depues, y j-1 = 0 como minimo ( corrisponde a j>=1))

         * Como primera aproximacion de la posicion del cruce descendiente, se utiliza una interpolacion
         lineal entre el punto precedente y sucesivo al cruce.
         Desarollando la formula (recta entre los puntos de coordinadas (eta, tiempo)
         A(eta[j-1], t[j-1]) y B(eta[j], t[j]), antecedente y sucesivo respectivamente), se halla::
            tiempo_cruce = t[j]-Ts*(-eta[j])/(eta[j-1]-eta[j])

        * Se hace el grafico elevaciones - tiempo con los cruces.
    '''
    h = []
    T = []

    #  Tiempos donde eta es zero mas el tiempo[0] y tiempo[-1]
    Ts = t[1]-t[0]
    t_zero = []

    for j in range(len(eta)):  # N numero de estados de mar
        if j > 0 and eta[j] * eta[j - 1] <= 0 and eta[j - 1] >= eta[j]:
            t_zero.append(t[j]-Ts*(-eta[j])/(eta[j-1]-eta[j]))  # Con interpolacion linear

    # Grafico tiempo vs. altura de ola con los cruces.
    tag = 'Elevaciones \nSensorWG%s' % (sensor)
    plt.plot(t, eta, label=tag)
    plt.plot(t_zero, np.full((len(t_zero), 1), 0), 'ro')
    plt.title("Elevaciones - tiempo \nSensorWG%s" % (sensor))
    plt.xlabel('Tiempo (s)')  # Etiqueta del eje x
    plt.ylabel('Eta (cm)')  # Etiqueta del eje y
    plt.grid()
    # Salva el grafico en la carpeta donde se trabaja en formato .pdf (se puede cambiar el formato).
    fig_name_sigma = 'Eta_tiempo_WG%s.pdf' % (sensor)
    plt.savefig(fig_name_sigma)
    plt.show()

    N = len(t_zero) - 1  # numero de periodos

    for l in range(N):
        # Busca los indeces (find() de MATLAB)
        t_ini = t_zero[l]
        t_fin = t_zero[l + 1]

        '''
        ## Metodo 1
        posiciones = []
        for i, tiempo in enumerate(t):
            if tiempo >= t_ini and tiempo < t_fin:  # mat_type['fecha'][i]>= t_ini and mat_type['fecha'][i]< t_fin:
                posiciones.append(i)

        # Anade a la lista
        h.append(max(eta[posiciones]) - min(eta[posiciones]))
        T.append(t_fin - t_ini)
        '''

        ## Metodo 2
        mascara_booleana = (t >= t_ini) & (t < t_fin)
        # El indice es relativo a la mascara creada.
        indice_max = eta[mascara_booleana].argmax()
        indice_min = eta[mascara_booleana].argmin()
        # Indice abosluto
        indice_max_abs = indice_max + len(eta[t < t_ini])
        indice_min_abs = indice_min + len(eta[t < t_ini])
        # Anade a la lista
        h.append(eta[indice_max_abs] - eta[indice_min_abs])
        T.append(t_fin - t_ini)

    # Conversion en array de NumPy
    h = np.array(h)
    T = np.array(T)

    return h, T

# pdf de Rayleight
def rayleight_pdf(x, Hs):
    '''
    Probability distribution funcion de Rayleight.

    Es de la forma::
        y = 4 * x / (Hs ** 2) * np.exp(-2 * (x ** 2) / (Hs ** 2))

    Parameters
    ----------
        x : float
            Altura.
        Hs : float
            Altura de ola significante.
    Returns
    __________
        y : float
            Cuantil o probabilidad de NO EXCEDENCIA correspondiente a la altura dada.
    '''
    y = 4 * x / (Hs ** 2) * np.exp(-2 * (x ** 2) / (Hs ** 2))
    return y

# cdf de Rayleight
def rayleight_cdf(x, Hs):
    '''
    Cumulative distribution funcion de Rayleight, hallada por integracion de la pdf.

    Es de la forma::
        y = 1 - np.exp(-2 * (x/Hs)**2)

    Parameters
    ----------
        x : float
            Altura de ola.
        Hs : float
            Altura de ola significante.
    Returns
    __________
        y : float
            Cuantil o probabilidad de NO EXCEDENCIA correspondiente a la altura dada.
    '''
    y = 1 - np.exp(-2 * (x/Hs)**2)
    return y

# Inversa de la cdf de Rayleight
def rayleight_cdf_inv(y, Hs):
    '''
    Funcion inversa de la cdf de Rayleight

    Su formula es::
        x = Hs * np.sqrt(-np.log(1 - y)/2)
    Parameters
    ----------
        y : float
            Cuantil o probabilidad de NO EXCEDENCIA.
        Hs : float
            Altura de ola significante.
    Returns
    __________
        x : float
            Altura correspondiente al cuantil o a la probabilidad de NO EXCEDENCIA.
    '''
    x = Hs * np.sqrt(-np.log(1 - y)/2)
    return x


def analisis_estado(h, t, sensor):  # alturas, periodos
    '''
    Hace una analisis de un estado de mar.
    Se hallan
        * Numero de olas
        * H y T maxima
        * H y T media
        * H y T minima
        * H_rms y T_rms (altura cuadratica media)
        * H_s  y T_s (altura significante)
        * Matriz ordenada (segun las alturas) de las alturas y periodos.
        * Altura correspondiente a una probabildad de EXCEDENCIA igual al umral_alt.

    Se hacen los graficos:
        * Histograma de alturas y de tiempos.
        * Histograma de alturas normalizado y *fittado* con pdf de Rayleight.

    Parameters
    ----------
        h : np.array() or list
            Alturas de las olas del estado de mar.
        t : np.array() or list
            Periodos de las olas del estado de mar.
    Notes
    ______
    Imprime a pantalla una matriz N X 3 del tipo, ordenada segun las alturas.
    # |  H  | T
     ---------
    0 | H[0]|T[0]

        * Para ordenar la matriz, se crea un array numpy del tipo Data Type Object.
    [http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html]

        * A partir de la matriz, se crea un archivo .csv y uno .txt
        (hecho en formato tabla de LaTeX) que se salva en la carpeta de trabajo
    '''

    matriz = [(i+1, h[i], t[i]) for i in range(len(h))]

    # Ordenar la matriz
    dtype = [('index', int), ('altura', float), ('periodo', float)]
    a = np.array(matriz, dtype=dtype)

    # Ordenar(de min a max)
    a_ord = np.sort(a, order='altura')

    # invertir la matriz
    a_ord[:] = a_ord[::-1]

    # Informaciones
    Nolas = len(h)

    Hmax = a_ord['altura'][0]
    Tmax = np.max(t)  # np.max(a_ord['periodo'])

    Hmean = np.mean(h)
    Tmean = np.mean(t)

    Hrms = np.sqrt(np.dot(h, h) / Nolas)
    Trms = np.sqrt(np.dot(t, t) / Nolas)

    Hs = np.mean(a_ord['altura'][0:Nolas / 3])
    Ts = np.mean(a_ord['periodo'][0:Nolas / 3])

    print("INFORMACIONES")
    print("--------------------")
    print("--------------------")
    print("Medidor numero %s" % sensor)
    print("--------------------")
    print("Martiz ordenada")
    print("matriz N X 3 del tipo \n # | H | T")
    for i in range(len(h)):
        print("%s | %.4f | %.4f" % (a_ord['index'][i], a_ord['altura'][i], a_ord['periodo'][i]))
    print("Numero de olas=", len(h_1))


    # Si hace falta, exportar los datos para ponerlos en formato .csv o LaTeX (en tabla)
    with open("output_WG%s.csv" % (sensor),"w") as text:
        # text.write("Numero & Altura H (cm) & Periodo T (s) \\\\ \n")  # Latex
        text.write("Numero,  Altura H (m),  Periodo T (s)  \n")
        for i in range(len(a_ord)):
            # Salvar matriz en file .txt para LaTeX
            # linea = "%s" % (a_ord['index'][i])+"&"+ "%s" % (a_ord['altura'][i])+"&"+"%s" % (a_ord['periodo'][i])+ "\\\\"+"\n"  # Latex
            linea = "%s" % (a_ord['index'][i])+","+ "%s" % (a_ord['altura'][i])+","+"%s" % (a_ord['periodo'][i])+ "\n"  # archivo .csv
            text.write(linea)
            print(a_ord[i,], '\n')


    print("--------------------")
    print("numero olas %s" % (Nolas))
    print("H maxima %s, periodo maximo, %s" % (Hmax, Tmax))
    print("H media %s, periodo medio, %s" % (Hmean, Tmean))
    print("H rms %s, periodo rms, %s" % (Hrms, Trms))
    print("H s %s, periodo s, %s" % (Hs, Ts))
    print("--------------------")
    print("--------------------")

    # Imprimir a pantalla la altura y el umbral de EXCEDENCIA.
    print("Con una probabilidad de EXCEDENCIA de {0}, curva de Rayleight, se obtiene una altura de {1} m "\
            .format(umbral_exced_alt, rayleight_cdf_inv(1-umbral_exced_alt, Hs)))

    # Histograma de alturas.
    plt.hist(h)
    plt.title("Histograma alturas sensor WG%s" % (sensor))
    plt.xlabel("Altura de ola (cm)")
    plt.ylabel("# Ocurrencias")
    # Se salva el grafico en la carpeta de trabajo en formado .pdf
    fig_name_sigma = 'H_alturas_WG%s.pdf' % (sensor)
    plt.savefig(fig_name_sigma)
    plt.show()

    # Histograma de los periodos.
    plt.hist(t)
    plt.title("Histograma periodos sensor WG%s" % (sensor))
    plt.xlabel("Periodos de las olas (s)")
    plt.ylabel("# Ocurrencias")
    fig_name_sigma = 'H_periodos_WG%s.pdf' % (sensor)
    plt.savefig(fig_name_sigma)
    plt.show()

    # Histograma de alturas normalizado
    HR = np.arange(0, Hmax +  Hmax / 7, 0.01)
    plt.hist(h, normed=True, bins=20)
    plt.plot(HR, rayleight_pdf(HR, Hs))
    '''
    Alternativa con scipy.stats, utilizando Rayleight.
    Hay que amejorarla.

    # k = (4/Hs**2)*np.exp(4/Hs**2)  # Pero no funciona.
    # k_ray = rayleigh.pdf(HR)*k
    # plt.plot(HR, k_ray)
    '''
    plt.title("Histograma de alturas normalizado con funcion de Rayleight sensor WG%s" % (sensor))
    plt.xlabel("Altura de ola (cm)")
    plt.ylabel("# Ocurrencias")
    fig_name_sigma = 'H_alturas_norm_rayl_WG%s.pdf' % (sensor)
    plt.savefig(fig_name_sigma)
    plt.show()

if __name__ == '__main__':
    # Lectura archivo .dat y creacion array
    path = 'datos.dat'  # Path para el archivo.dat
    # Se crea el array de datos
    datos = np.fromfile(path, sep="\n")
    '''
    Para crear el array con el que se trabajará, se utiliza np.fromfile(file, dtype=float, count=-1, sep='').
    Ya tenemos el *file*, que es dado del path, el *dtype* en este caso es ya *float* por default (numeros reales),
    *count* es -1 por default, en el sentido que carga hasta el indice -1 (o sea el ultimo),
    el *sep* es el separador, en este caso "\n", el "línea nueva".
    '''

    t = datos[0::4]  # Vector de los tiempos de medidura
    eta_1_sin_alfa = datos[1::4]  # Vector de las elevaciones del sensor 1
    eta_2_sin_alfa = datos[2::4]
    eta_3_sin_alfa = datos[3::4]

    # Factor alfa
    alfa = ((23+16+16+9+27)/5)**(1/7)

    # Multiplicamos por alfa
    eta_1 = alfa * eta_1_sin_alfa
    eta_2 = alfa * eta_2_sin_alfa
    eta_3 = alfa * eta_3_sin_alfa

    # Creacion estados de mar
    h_1, T_1 = crea_estado(eta_1, t, 1)
    h_2, T_2 = crea_estado(eta_2, t, 2)
    h_3, T_3 = crea_estado(eta_3, t, 3)

    # Analisis de los estados de mar
    analisis_estado(h_1, T_1, 1)
    analisis_estado(h_2, T_2, 2)
    analisis_estado(h_3, T_3, 3)
