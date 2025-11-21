import pandas as pd
import numpy as np


#Importamos lista de selecciones clasificadas y dejamos slots para las de repechaje

df_clasificados = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Clasificados')

df_repechaje_uefa = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Repechaje_UEFA')

df_repechaje_fifa = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Repechaje_FIFA')

#Cargamos Power Ranking FIFA

df_power_ranking = pd.read_csv('01_datos_brutos/FIFA_PR_19_11_2025.csv').drop(columns=['Unnamed: 7'])

#Generamos los repechajes

def generar_repechaje_uefa(df, random_state=None):
    df_shuffle = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    df_shuffle['llave'] = np.repeat([1,2,3,4], 4)
    ganadores = df_shuffle.groupby('llave', group_keys=False).sample(1, random_state=random_state)
    return ganadores  # devuelve todas las columnas


def generar_repechaje_fifa(df, random_state = None):
    #Asignamos llaves
    df_shuffle = df.sample(frac = 1, random_state = random_state)
    df_shuffle['llave'] = np.repeat([1,2], 3)

    ganadores = df_shuffle.groupby('llave').sample(1, random_state = random_state)

    return ganadores


#Simulamos bombos

def asignar_bombos(df_clasificados, 
                   clasificados_uefa = None,
                   clasificados_fifa = None,
                   random_state = None):
    # Merge
    df_merged = pd.merge(df_clasificados, df_power_ranking[['codigo', 'puntos_totales']],
                          on='codigo', 
                          how='left')
    df_sorted = df_merged.sort_values(by='puntos_totales', ascending=False).reset_index(drop=True)

    # Bombo 1: anfitriones + mejores restantes hasta 12
    anfitriones=['MEX','USA','CAN']
    bombo1 = df_sorted[df_sorted['codigo'].isin(anfitriones)].copy()
    restantes = df_sorted[~df_sorted['codigo'].isin(anfitriones)]
    bombo1 = pd.concat([bombo1, restantes.head(12 - len(bombo1))])
    bombo1['bombo'] = 1

    # Actualizamos restantes
    restantes = restantes.drop(restantes.head(9).index)

    # Bombo 2
    bombo2 = restantes.head(12).copy()
    bombo2['bombo'] = 2
    restantes = restantes.drop(restantes.head(12).index)

    # Bombo 3
    bombo3 = restantes.head(12).copy()
    bombo3['bombo'] = 3
    restantes = restantes.drop(restantes.head(12).index)

    # Bombo 4 inicial
    bombo4 = restantes.copy()
    bombo4['bombo'] = 4
    bombo4['repechaje'] = 0

    # Ganadores de repechaje UEFA
    if clasificados_uefa is None:
        ganadores_uefa = generar_repechaje_uefa(df_repechaje_uefa, random_state=random_state)
    else:
        ganadores_uefa = df_repechaje_uefa[df_repechaje_uefa['codigo'].isin(clasificados_uefa)].copy()
    ganadores_uefa['repechaje'] = 1
    # Crear columna anfitrion si no existe
    if 'anfitrion' not in ganadores_uefa.columns:
        ganadores_uefa['anfitrion'] = 0

    # Ganadores de repechaje FIFA
    if clasificados_fifa is None:
        ganadores_fifa = generar_repechaje_fifa(df_repechaje_fifa, random_state=random_state)
    else:
        ganadores_fifa = df_repechaje_fifa[df_repechaje_fifa['codigo'].isin(clasificados_fifa)].copy()
    ganadores_fifa['repechaje'] = 1
    # Crear columna anfitrion si no existe
    if 'anfitrion' not in ganadores_fifa.columns:
        ganadores_fifa['anfitrion'] = 0

    # Concatenamos repechajes al bombo 4
    bombo4 = pd.concat([bombo4, ganadores_uefa, ganadores_fifa], ignore_index=True)
    bombo4['bombo'] = 4

    # Limpiamos columnas y aseguramos tipos
    columnas_base = ['codigo', 'confederacion', 'anfitrion', 'bombo']
    columnas_bombo4 = columnas_base + ['repechaje']
    bombo4 = bombo4[columnas_bombo4]

    bombo4['repechaje'] = bombo4['repechaje'].fillna(0).astype(int)
    bombo4['anfitrion'] = bombo4['anfitrion'].fillna(0).astype(int)

    # Concatenamos todos los bombos
    df_final = pd.concat([bombo1, bombo2, bombo3, bombo4]).reset_index(drop=True)

    return df_final, bombo1, bombo2, bombo3, bombo4


df_bombos, bombo1, bombo2, bombo3, bombo4 = asignar_bombos(df_clasificados, df_power_ranking, random_state=42)


print(generar_repechaje_uefa(df_repechaje_uefa, random_state=41))
print(generar_repechaje_fifa(df_repechaje_fifa, random_state=41))

print(bombo4)