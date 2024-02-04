#Algoritmo GRASP 

#CARGAMOS LAS LIBRERIAS
import pandas as pd
import funciones as f
import time
import random
from collections import defaultdict
import matplotlib.pyplot as plt

#DATOS NECESARIOS EN EL SCRIPT

##SEMILLA DE ALEATORIEDAD
random.seed(4)

##CARGAMOS LOS DATOS NECESARIOS
pd.set_option("display.max_columns", 5) #Para que se muestren mas columnas en el dataframe
archivo = 'distancia entre ciudades, localización y población.xlsx'

##DATAFRAME CON LAS DISTANCIAS ENTRE LOCALIZACIONES
df = pd.read_excel(archivo, sheet_name='Distancia entre capitales')

##DATAFRAME CON LA LOCALIZACIÓN DE LAS CIUDADES, SUS POBLACIONES, ...
dl = pd.read_excel(archivo, sheet_name='Localización de ciudades')

df=df.set_index(df.columns[0])
dl=dl.set_index(dl.columns[0])

##LISTA DE CIUDADES
cities = list(df.columns)

##CREACIÓN MATRIZ DE DISTANCIAS
distance_matrix = defaultdict(dict)
for ka in cities:
    for kb in cities:
        distance_matrix[ka][kb] = df.loc[ka,kb]

##CREACIÓN DE LISTA DE POBLACIONES
poblation_dict = defaultdict(dict)
for ka in cities:
        poblacion_localidad=dl.loc[ka,"Población Provincia"]
        poblation_dict[ka]=poblacion_localidad

##CREACIÓN DE LISTA DE POBLACIONES PONDERADAS
poblationPond_dict = defaultdict(dict)
for ka in cities:
        poblacion_localidad=dl.loc[ka,"Población Ponderada"]
        poblationPond_dict[ka]=poblacion_localidad   

    
tienen_centro={}##CONTIENE LAS CIUDADES QUE DISPONEN DE CENTRO LOGISTICO

#------------------------------------------------------------------------------------------------------
#PARAMETROS DE ALGORTIMO GRASP
itgrasp=3000

#ARGUMENTOS FASE CONSTRUCTIVA GRASP
availablecities=[]##CIUDADES DISPONIBLES
candidatos=[]##CANDIDATOS ENTRE LAS CIUDADES DISPONIBLES
candidatosOrdenados=[]#LISTA DE CANDIDATOS ORDENADOS
LoC=[]##LISTA DE CANDIDATOS RESTRINGIDA
tamanoLoC=15##TAMAÑO DE LA LISTA DE CANDIDATOS RESTRINGIDA
alpha=0.4##VALOR ALPHA
#------------------------------------------------------------------------------------------------------
#SOLUCIONES
listOfSolutionsCompeltas=[]##LISTA DE SOLUCIONES COMPLETADAS EN CADA ITERACIÓN CON PARAMETROS DE INTERES
listOfSol=[]#L#ISTA DE SOLUCIONES COMPLETADAS EN CADA ITERACIÓN

##Sol=dict("Ciudad":[NCL,Asignación]) SOLUCIÓN DEL SCRIPT
sol = defaultdict(dict)
for ka in cities:
    sol[ka] = [0,None]
    
mejorsol=[]##MEJOR SOLUCIÓN OBTENIDA


listOfNCL=[]##Nº CENTROS DE LA SOLUCIÓN POR CADA ITERACIÓN
nclSol=0##Nº CENTROS DE LA SOLUCIÓN
mejorncl=[]##Nº CENTROS MÍNIMO ENCONTRADO

minSol=[]##MINIMA SOLUCIÓN DEL VALOR Z OBJETIVO DEFINIDO POR CADA ITERACIÓN
minSolAux=0##MINIMA SOLUCIÓN DEL VALOR Z DATO AUXILIAR
minz = []##MINIMA SOLUCIÓN DEL VALOR Z OBJETIVO DEFINIDO POR CADA ITERACIÓN PARA EL USO DE GRÁFICAS
minzaux = 0##MINIMA SOLUCIÓN DEL VALOR Z OBJETIVO DEFINIDO POR CADA ITERACIÓN
registro_z = []##LISTA DE VALOR Z POR CADA ITERACIÓN

ponderacion=0.75##PONDERACIÓN DEL CRITERIO DE LA POBLACIÓN EN LA FUNCIÓN FITNESS
#LA PONDERACIÓN DEL CIRTERIO DE LA DISTANCIA SERÁ 1-LA PONDERACIÓN ANTERIOR DEFINIDA
#------------------------------------------------------------------------------------------------------

#ALGORITMO PRINCIPAL SCRIPT
startime=time.time()

for n in range(itgrasp):  
    
    ###A LA HORA DE COMENZAR OTRA ITERACIÓN VACIAMOS LA SOLUCIÓN Y LAS VARIABLES NECESARIAS
    tienen_centro.clear()
    sol.clear()
    for c in cities:
          sol[c]=[0,None]
    availablecities= cities.copy()#DISPONEMOS DE TODAS LAS CIUDADES OTRA VEZ
    
    #------------------------------------------------------------------------------------------------------
    ##FASE CONSTRUCTIVA DE LA SOLUCIÓN INICIAL DEL GRASP
    i=0
    
    #LA PRIMERA ITERACIÓN DEBE SER ALEATORIA YA QUE SI NO HAY CENTROS NO PODEMOS REALIZAR LA FUNCIÓN FITNESS DADO QUE NO SE PODRÍA CALCULAR EL SEGUNDO CRITERIO 
    while(len(availablecities)!=0):
        if i==0:
            #Elección primer elemento
            inicio= random.choice(cities)          
            
            #Definimos el NCL (Nº de Centros Logísticos) y la asignación
            #Tomamos las ciudades a distancia menor de 300km
            cities_less300=f.less300(inicio,availablecities)
            #Suma de poblaciones de las ciudades tomadas/2,5millones
            ncl=round(f.poblations(cities_less300)/2500000+0.5)
            #ncl de la ciudad "inicio"
            sol[inicio]=[ncl,None]
            #Asignación de las ciudades tomadas a la ciudad "inicio"
            sol=f.asignaciones(sol,inicio,cities_less300)
            #Actualizamos la lsita de lista de ciudades con centros logísticos
            tienen_centro[inicio]=f.poblations(cities_less300)
            #Removemos las ciudades que han intervenido en este proceso
            for c in cities_less300:
                availablecities.remove(c) 
            """f.dibujar_grafica(sol, "Solucion "+str(i)+" de la fase constructiva")""" # Si se quiere ver como funciona la fase constructiva descomentar esta linea
        else:
            candidatos.clear()
            candidatos=f.fitness(availablecities,ponderacion, tienen_centro)#tomamos la calidad en base a la función fitness y ordenamos los candidatos de la lista de candidatos
            candidatosOrdenados.clear()
            
            candidatosOrdenados=(sorted(candidatos, key=lambda d: d['fitness']))   
            LoC.clear()
            #Realizamos el corte
            Cmin=candidatosOrdenados[0]["fitness"]
            Cmax=candidatosOrdenados[-1]["fitness"]
            Corte=alpha*(Cmax-Cmin)+Cmin
            
            #Creamos la lista de candidatos restringidos
            for sel in range(0,len(candidatosOrdenados)):
                #Creación lista de candidatos de tamaño tamanoLoC más aquello candidatos con la misma distancia que el último añadido (empates)
                if   (sel<tamanoLoC or candidatosOrdenados[sel]['fitness']==candidatosOrdenados[tamanoLoC-1]['fitness']):
                    if candidatosOrdenados[sel]['fitness']<=Corte:
                        LoC.append(candidatosOrdenados[sel])
                        
            #Asignamos una equiponderación a cada elemento
            auxP=0
            for c in range(0,len(LoC)):
                auxP+=(1/len(LoC))
                LoC[c]['ProbabAcum']=auxP
            
            #Generación número aleatorio entre 0 y 1 para sorteo del candidato
            numAleat=random.random()
            for c in range(0,len(LoC)):
                if numAleat<LoC[c]['ProbabAcum']:
                    elegido=LoC[c]['candidato']
                    break
                
            #Ciudad tomada = "elegido"
            #Definimos el NCL y la asignación
            #Ciudades a distancia menor de 300km
            cities_less300=f.less300(elegido, availablecities)
            #Suma de poblaciones/2,5millones
            ncl=round(f.poblations(cities_less300)/2500000+0.5)
            
            #ncl "elegido"
            sol[elegido]=[ncl,None]
            tienen_centro[elegido]=f.poblations(cities_less300)
            #Asignación ciudad "inicio"
            sol=f.asignaciones(sol,elegido,cities_less300)
           
            #Removemos las ciudades asignadas
            for c in cities_less300:
                availablecities.remove(c)
            """f.dibujar_grafica(sol, "Solucion "+str(i)+" de la fase constructiva")""" # Si se quiere ver como funciona la fase constructiva descomentar esta linea
                
        i+=1
    
    ##FASE CONSTRUCTIVA FINALIZADA
    #------------------------------------------------------------------------------------------------------
    
    """f.dibujar_grafica(sol, "Solucion de la fase constructiva")""" # Si se quiere ver como funciona la fase constructiva descomentar esta linea         
    #BUSQEUDA EXHAUSTIVA
    
    #1.VECINDARIO
    
    #REASIGNAMOS LAS CIUDADES DE LA SOLUCIÓN EN BUSCA DE LOGRAR UNA REDUCCIÓN DE LA DISTANCIA PONDERADA    
    
    ciudades_sin_centro=[]#Tomamos las ciudades que no tienen ningún centro logístico para tratar de reasignarlas
    for c in cities:
        if c not in list(tienen_centro.keys()):
            b=sol[c][1]
            ciudades_sin_centro.append({"ciudad":c,"poblacion":poblationPond_dict[c]})   
            
    ciudadesOrdenada=(sorted(ciudades_sin_centro, key=lambda d: d['poblacion']))    
    reasignadas=[]
    
    for temp in ciudadesOrdenada:#Tratamos de reasignar las ciudades en el orden establecido
        
        ciudad=temp["ciudad"]
        ciudadAsignada=sol[ciudad][1]
        dist_Actual=distance_matrix[ciudad][ciudadAsignada]
        menores=[]
        for t in list(tienen_centro.keys()):      
            poblacionActual=tienen_centro[t]            
            if dist_Actual>distance_matrix[ciudad][t] and ((poblacionActual+poblation_dict[ciudad])<=2500000*sol[t][0]):
                menores.append({"cambio":t,"distancia":distance_matrix[ciudad][t]})
        
        menoresOrdenada=(sorted(menores, key=lambda d: d['distancia']))#Lista con ciudades que pueden abastecer a la ciudad analizada que estan a menor distancia de su asignación actual
        
        if len(menoresOrdenada)!=1:
            #Distancia que suman todas las posibilidades
            suma_distancias=0
            for c in range(0,len(menoresOrdenada)):
                suma_distancias+=menoresOrdenada[c]['distancia']
            #Calculamos las probabilidades de reasignar a una ciudad según la distancia entre ambas ciudades
            auxP=0
            for c in range(0,len(menoresOrdenada)):
                auxP+=(1-menoresOrdenada[c]['distancia']/suma_distancias)
                menoresOrdenada[c]['ProbabAcum']=auxP
        elif len(menoresOrdenada)!=0:
            menoresOrdenada[0]['ProbabAcum']=1
        
        #También probamos con equiponderación pero no lograbamos mejores resultados
        """
        #Así se daría a cada ciudad la misma probabilidad
        auxP=0
        for c in range(0,len(menoresOrdenada)):
            auxP+=(1/len(menoresOrdenada))
            menoresOrdenada[c]['ProbabAcum']=auxP"""
        
        #Tomamos la ciudad a la que se reasignara
        reasignacion=None
        numAleat=random.random()
        for c in range(0,len(menoresOrdenada)):
            if numAleat<menoresOrdenada[c]['ProbabAcum']:
                reasignacion=menoresOrdenada[c]['cambio']
                break  
        
        #Se realiza la reasignación
        if reasignacion!=None:
            poblacionActual_Antigua=tienen_centro[ciudadAsignada] 
            poblacionActual_Reasignar=tienen_centro[reasignacion] 
            tienen_centro[sol[ciudad][1]]=poblacionActual_Antigua-poblation_dict[ciudad]
            sol[ciudad][1]=reasignacion
            tienen_centro[reasignacion]=poblacionActual_Reasignar+poblation_dict[ciudad]        
            """f.dibujar_grafica(sol, "Solucion tras reasignar "+str(temp['ciudad'])) """# Si se quiere ver como funciona la fase constructiva descomentar esta linea
    
            
    #2.VECINDARIO
    
    #ANALIZAMOS SI ALGUNA DE LOS CENTROS LOGÍSTICOS NO ES NECESARIO EN LA SOLUCIÓN (TRAS LA REASIGNACIÓN DE LAS CIUDADES SE PUEDE DAR EL CASO DE QUE ALGUN CENTRO NO SEA NECESARIO)
    
    for t in list(tienen_centro.keys()):
        if sol[t][0]*2500000>tienen_centro[t]:
            if (sol[t][0]-1)*2500000>=tienen_centro[t]:
                sol[t][0]-=1
    
    
    
    #ACTUALIZACIZACIÓN DE LA INFORMACIÓN A ESTUDIAR
    SumNCL=f.sumar_centros(sol)
    DistPond=+f.distanciaSol(sol)
    Z=SumNCL+DistPond/1000
    
    if (n==0):
        minSolAux=SumNCL
        minzaux=Z
    
    elif (minSolAux>SumNCL):
        minSolAux=SumNCL
    elif(minzaux>Z):
        minzaux=Z    
        
    minSol.append(minSolAux)
    minz.append(minzaux)
    registro_z.append(Z)
    listOfSol.append(sol)
    listOfNCL.append(SumNCL)
    listOfSolutionsCompeltas.append({"Solution": sol.copy(),"fobj": Z, "minobj": minSolAux, "itgrasp": n, "NCL":SumNCL, "DistPond":DistPond})

listordenada=[]
listordenada.clear()
listordenada=(sorted(listOfSolutionsCompeltas, key=lambda d: d['fobj']))    
mejorsol=listordenada[0]['Solution']
endtime = time.time()
#FIN DEL ALGORITMO
#------------------------------------------------------------------------------------------------------

#RESULTADOS
print("Solucion")
print(mejorsol)
print("El número de centros es: ",f.sumar_centros(mejorsol))
print("La distancia ponderada es: ",f.distanciaSol(mejorsol))

#FACTIBILIDAD DEL PROBLEMA
f.factibilidad(mejorsol)

tiempo = endtime - startime

print("El tiempo que tarda el algoritmo es: ", tiempo, " segundos") 
 
### ESCRIBIMOS LA MEJOR SOLUCION EN UN EXCEL 
f.escribir_excel(mejorsol)

### DIBUJAMOS LA MEJOR SOLUCION
f.dibujar_grafica(mejorsol, "Mejor solucion")

### DIBUJAMOS EL DATAFRAME CON LA INFORMACION
data_frame = f.data_frame_informacion(mejorsol)
f.render_mpl_table(data_frame)
  
### GRAFICAMOS LA EVOLUCION DE LA SOLUCION   
plt.figure()
plt.suptitle("Evolucion del numero de centro")
plt.plot(minSol[0:10])
plt.title("Distance")
plt.show() 

### GRAFICAMOS LA EVOLUCION DE Z  
plt.figure()
plt.suptitle("Evolucion de la función objetivo Z")
plt.plot(minz,'r')
plt.plot(registro_z, linewidth=0.20)
plt.title("Distance")
plt.show()  