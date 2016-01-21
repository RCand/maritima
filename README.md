# ENGLISH VERSION BELOW
# Descripción general
Hay aquí unas herramientas utiles para:
  * el análisis de las mareas astronomicas (Analisis_armonico.py) y la predicción de las mismas.
  * la análisis espectral de una serie temporal de medidas de elevación (Espectro.py).  
  * la creación del estado de mar y el calculo de sus vaolers statisticos a partir de una serie temporal de medidas de elevación (Estado_de_mar.py).  
  * el análisis del régimen medio y extremal de un estado de mar (Regimen_medio_y_extremal.py). 

Estas herramientas han sido desarolladas a lo largo del curso de Ingeniería Marítima y Costera en la E.T.S.I.C.C.P. en la Universidad de Granada, en el año académico 2015/16.

## Descargar git
Es necesario descargar git para instalar los requirements.txt
[http://git-scm.com/downloads]

## Instalar los modulos necesarios
### Linux (Aconsejado)
En linux, abrir un terminal y escribir:
```
$ pip3 install -r requirements.txt
``` 
### Windows
Una manera de hacerlo es de abrir requirements.txt con un editor de texto y instalar manualmente todos los paquetes necesarios con su proprio IDE (p. ej. desde Pycharm).

Una otra manera (¡¡¡Aún no lo he verificado!!!) es de descargar pip para Windows,
(ver aquí: [http://stackoverflow.com/questions/4750806/how-do-i-install-pip-on-windows])

cambiar carpeta a la donde está el requirements y escribir en el prompt:
```
$ pip3 install -r requirements.txt
``` 

## Inserir datos y parametros
Para inerir los datos, hay que poner el archivo .dat en la misma carpeta donde hay el programa y poner el path como sigue:
```
# Lectura archivo .dat y creacion array
path = 'APSevilla.dat' 
```
Una alternativa (en Windows), es de inserir directamente el path del archivo

```
path = 'C:/Users/User/Folder/Archivo.dat'
```

```
datos = np.fromfile(path, sep="\n")
```
# Regimen_medio_y_extremal.py


# General description
Here you can find some tools useful for:
 * astronomical tides analysis (Analisis_armonico.py) and their prediction.
 * spectral analysis of a time-elevation series (Espectro.py).
 * sea state creation and significant statistical values calculation from a a time-elevation series (Estado_de_mar).
 * mean and extreme value analysis of a sea state (Regimen_medio_y_extremal.py).

These tools were developped during the Sea and Costal Engineering course at the E.T.S.I.C.C.P. in the University of Granada, during the academic year 2015/16.

## Git download.
Download git, it is necessary to install requirements.txt
[http://git-scm.com/downloads]

## Installing requested packages
### Linux (Suggested)
Open a terminal and type:
```
$ pip3 install -r requirements.txt
``` 
### Windows
One way is to open requirements.txt with a text editor and manually install all the necessary packages from your IDE (e.g. from Pycharm).

Another way (Still not verified!!!) is to download pip for Windows,
(look here: [http://stackoverflow.com/questions/4750806/how-do-i-install-pip-on-windows])

change directory to the one containing requirements.txt and then type on the prompt:
```
$ pip3 install -r requirements.txt
``` 

## Insert data and parameters 
In order to insert the data, you have to put the .dat file in the same folder where the .py program is and write the path as follows: 
```
# File .dat reading and array creation
path = 'APSevilla.dat' 
```
As an alternative (in Windows), you might directly insert the file's path.
```
path = 'C:/Users/User/Folder/Archivo.dat'
```

```
datos = np.fromfile(path, sep="\n")
```

# Extreme Values Analysis 

