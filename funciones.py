import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import numpy as np
import six

pd.set_option("display.max_columns", 5) #Para que se muestren mas columnas en el dataframe
archivo = 'distancia entre ciudades, localización y población.xlsx'
df = pd.read_excel(archivo, sheet_name='Distancia entre capitales')
dl = pd.read_excel(archivo, sheet_name='Localización de ciudades')

df=df.set_index(df.columns[0])
dl=dl.set_index(dl.columns[0])

#Información necesaria
#Lista de ciudades
cities = list(df.columns)

#Creación matriz de distancias
distance_matrix = defaultdict(dict)
for ka in cities:
    for kb in cities:
        distance_matrix[ka][kb] = df.loc[ka,kb]

#Creación de lista de poblaciones
poblation_dict = defaultdict(dict)
for ka in cities:
        poblacion_localidad=dl.loc[ka,"Población Provincia"]
        poblation_dict[ka]=poblacion_localidad

#Creación lista poblaciones ponderadas
poblationPond_dict = defaultdict(dict)
for ka in cities:
        poblacion_localidad=dl.loc[ka,"Población Ponderada"]
        poblationPond_dict[ka]=poblacion_localidad   

availablecities=[]
candidatos=[]

"""


GUIA DE LAS FUNCIONES:
    
    
    sumar_centros -> a partir de una solución devuelve la cantidad de centros que tiene la solución
    distanciaSol -> a partir de una solución devuelve la distancia ponderada de la solución
    less300 -> a partir de una cuidad y una lista mira que cuidades se encuentra a una distancia factible(menos de 300 km)
    poblations -> a partir de una lista de cuidades devuelve la suma de la población de estas cuidades
    asignaciones -> a partir de una solución anterior, una lista de cuidades, y una cuidad temp, modifica la solución anterior asignandole a esa lista de cuidades los centros logísticos de la cuidad temp 
    distancia_min -> a partir de una cuidad c y un diccionario devuelve la minima distancia entre la capital c y las ciudades que contienen centros logísticos 
    fitness -> A partir de una lista con las cuidades disponibles, un valor de la ponderación y otro lista con las cuidades que tienen centro devueve una lista con diccionarios de los posibles candidatos
    dibujar_grafica -> a partir de una solución te da una gráfica
    data_frame_informacion -> a partir de una solución crea un dataframe con información interesante
    escribir_excel -> a partir de una solución te crea un excel con el formato establecido
    render_mpl_table -> a partir de un dataframe lo pasa a formato imagen
    
    
"""
def sumar_centros(x):#suma el numero total de centros logisticos asigandos en una solucion
    """
    Parameters:
        x -> diccionario de una solucion
    Return: La cantidad de centros que tiene esa solucion
    """
    ncl=0#numero de centros logisticos
    for c in cities:
        ncl += x[c][0]
    return ncl

def distanciaSol(x):
    """
    Parameters:
        x -> diccionario de una solucion
    Return: La distancia ponderada tiene esa solucion
    """
    distanciaTotal=0
    for a in list(x.keys()):
        b = x[a][1]
        distanciaTotal += distance_matrix[a][b]*poblationPond_dict[a]
        
    return distanciaTotal

def less300(temp, availablecities):
    """"
    Parameters:
        temp -> nombre de una cuidad
        availablecities -> lista con las cuidades disponibles
    Return: Devuelve ciudades que estan a distancia factible de dicha cuidad, es decir a menos de 300 km
    """
    ciudades=[]
    for c in availablecities:        
        if distance_matrix[temp][c]<=300:
            ciudades.append(c)
    return ciudades

def poblations(ciudades):
    """
    Parameters:
        cuidades -> lista con las cuidades las cuales se quiere ver la suma de estas cuidades
    Return: Devuelve la suma de las poblaciones de las ciudades de lista
    """
    poblacion=0
    for c in ciudades:
        poblacion+=poblation_dict[c]
    return poblacion

def asignaciones(solAnterior,temp,ciudades):
    """
    Parameters:
        solAnterior -> solución anterior
        temp -> nombre de la ciudad con los centros logísticos
        cuidades -> lista con las cuidades que quieren ser asignadas a los centros logísticos de la cuidad temp
    Return: Asigna las ciudades tomadas a los centros logisticos de la ciudad temp    
    """
    solucion=dict(solAnterior)
    for c in ciudades:
        solucion[c][1]=temp
    return solucion

def distancia_min(c, tienen_centro):
    """
    Parameters:
        c -> nombre de una cuidad
        tienen_centro -> lista con diccionarios donde el primer elemento es la cuidad que tiene centro logistico y el segundo elemento las cuidades a las que abastece
    Return: La minima distancia entre la capital c y las ciudades que contienen centros logísticos 
    """
    distancias=[]
    for x in tienen_centro:
        distancias.append(distance_matrix[c][x])
    return min(distancias)

def fitness(availablecities, ponderacion, tienen_centro):
    """
    Parameters:
        availablecities -> lista con las cuidades disponibles
        ponderacion -> valor que le damos a la ponderacion del criterio de la población
        tienen_centro -> lista con diccionarios donde el primer elemento es la cuidad que tiene centro logistico y el segundo elemento las cuidades a las que abastece
    Return: Lista con diccionarios de los posibles candidatos
    """
    criterio_poblacion=defaultdict(dict)
    criterio_distancia_max=defaultdict(dict)
    
    for c in availablecities:
        criterio_poblacion[c]=poblationPond_dict[c]#se podría implementar la poblacion de los 300 que rodea
        criterio_distancia_max[c]=distancia_min(c, tienen_centro)
        
    criterio_poblacionOrdenado=sorted(criterio_poblacion, key=criterio_poblacion.get,reverse=True)
    criterio_distancia_maxOrdenado=sorted(criterio_distancia_max, key=criterio_distancia_max.get,reverse=True)  
    
    #Construcción lista de candidatos
    candidatos.clear()
    for c in availablecities:
        
        fit= criterio_poblacionOrdenado.index(c)*ponderacion+criterio_distancia_maxOrdenado.index(c)*(1-ponderacion)
        candidatos.append({"candidato": c,"fitness": fit})#ciudad y valor de la fitness 
    
    return candidatos

def factibilidad(sol):
    """
    Parameters:
        sol -> diccionario de una solucion
    Return: Devuelve si esa solución es factible o no
    """
    #CRITERIO DE DISTANCIA
    criterio_distancia=True
    for a in list(sol.keys()):
        b=sol[a][1]
        if distance_matrix[a][b]>300:
            criterio_distancia=False
    
    #CRITERIO DE ABASTECIMIENTO
    criterio_abastecimiento=True
    for a in list(sol.keys()):
      if sol[a][0]>0:      
          poblacion_a_cubrir=0
          for b in list(sol.keys()):
              if a==sol[b][1]:
                  poblacion_a_cubrir+=poblation_dict[b]
                  
          if sol[a][0]*2500000<poblacion_a_cubrir:
              print(a)
              print(sol[a][0]*2500000,poblacion_a_cubrir)
              criterio_abastecimiento=False
              
    if criterio_distancia & criterio_abastecimiento:
        return print("La solución es factible")
    else:
        return print("La solución NO es factible")

def dibujar_grafica(sol, titulo="Mejor solución"):
    """
    Parameters:
        sol -> diccionario de la solución a graficar
        titulo -> Titulo arriba de laa gráfica, por defecto será mejor solución
    """
    plt.figure()
    dic={}
    for i in sol.keys():
        ka, va = (float(dl['Lon ETRS89'][i]),float(dl['Lat ETRS89'][i]))
        plt.annotate(i, (ka, va), size=8)
        if sol[i][1]!=None:
            plt.arrow(float(dl['Lon ETRS89'][sol[i][1]]),float(dl['Lat ETRS89'][sol[i][1]]), 
                      float(dl['Lon ETRS89'][i])-float(dl['Lon ETRS89'][sol[i][1]]),
                      float(dl['Lat ETRS89'][i])-float(dl['Lat ETRS89'][sol[i][1]]), head_width=0.15) 
        
        if sol[i][0]==0:
            if sol[i][1]!=None:
                if sol[i][1] not in list(dic.keys()):
                    dic[sol[i][1]] = [i]
                else:
                    dic[sol[i][1]].append(i)
            
    for i in dic.keys():
        ejex = []
        ejey = []
        for j in dic[i]:
            ejex.append(float(dl['Lon ETRS89'][i]))
            ejex.append(float(dl['Lon ETRS89'][j]))
            ejey.append(float(dl['Lat ETRS89'][i]))
            ejey.append(float(dl['Lat ETRS89'][j]))
        plt.plot(ejex,ejey,label=i)
        
    
    plt.legend(prop={"size":8})
    plt.title(titulo)
    plt.show()

def data_frame_informacion(sol):
    """
    Parameters:
        sol -> el diccionario de una solución
    Return: Devuelve un dataframe con el numero de centros, la capacidad a repartir, lo que queda por repartir y el porcentaje de ocupacion
    """
    dic_pob={} 
    for i in sol.keys():
        if sol[i][0]==0:
            if sol[i][1] not in list(dic_pob.keys()):
                dic_pob[sol[i][1]] = [float(dl['Población Provincia'][i])]
            else:
                dic_pob[sol[i][1]].append(float(dl['Población Provincia'][i]))
               
    numero_centros = [] 
    capacidad_repartir=[]
    queda_repartir=[]
    porcentaje_ocupacion = []
    for i in dic_pob.keys():
        numero_centros.append(sol[i][0])
        capacidad_repartir.append(sol[i][0]*2500000)
        queda_repartir.append(sol[i][0]*2500000-float(dl['Población Provincia'][i])-sum(dic_pob[i]))
        porcentaje_ocupacion.append(str(round((float(dl['Población Provincia'][i])+sum(dic_pob[i]))/(sol[i][0]*2500000)*100,5))+"%")
        
    df2 = pd.DataFrame({"Cuidad":list(dic_pob.keys()),
                        "Números de centros":numero_centros,
                        "Capacidad a repartir":capacidad_repartir,
                        "Queda por repartir":queda_repartir,
                        "Porcentaje de ocupación":porcentaje_ocupacion}, index=dic_pob.keys())
    return df2

def escribir_excel(sol):
    """
    Parameters:
        datos1 -> excel con la información de la hoja1
        datos2 -> excel con la información de la hoja2
        dict_sol -> diccionario con la solución
    Return: Devuelve el excel con la solución
    """
    
    nombres = []
    num_Centros = []
    asignacion = []
    distancia_ponderada = []
    total_centros = 0
    total_distancia = 0
    for i in sol.keys():
        nombres.append(i)
        num_Centros.append(sol[i][0])
        asignacion.append(sol[i][1])
        distancia_ponderada.append(df[i][sol[i][1]] * dl["Población Ponderada"][i])
        total_centros += sol[i][0]
        total_distancia += df[i][sol[i][1]] * dl["Población Ponderada"][i]
     
    #Escribimos el número de centros y la distancia total
    nombres.append("")
    num_Centros.append(total_centros)
    asignacion.append("")
    distancia_ponderada.append(total_distancia)
    
    df_excel = pd.DataFrame({"Provincia" : nombres,
                       "numCentros Logísticos" : num_Centros,
                       "Centro Logístico Asignado" : asignacion,
                       "Distancia*población Ponderada" : distancia_ponderada})
    
    
    df_excel.to_excel("Solution_Grupo1.xlsx",index=False, encoding="latin1")
    
    return "El excel se ha generado correctamente"

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], Edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    """
    Parameters:
        data -> dataframe con la información
    Return: Devuelve el dataframe como imagen
    """
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(Edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax



