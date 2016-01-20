# Analisis Extremal
## Instalar los modulos necesarios
En linux, abrir un terminal y escribir:
```
$ pip install -r requirements.txt
``` 

## Inerir datos y parametros
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
datos = np.fromfile(path, "\n")
```


# Extreme Values Analysis 
## Installing requested packages
In Linux, open a terminal and type:
```
$ pip install -r requirements.txt
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
datos = np.fromfile(path, "\n")
```


