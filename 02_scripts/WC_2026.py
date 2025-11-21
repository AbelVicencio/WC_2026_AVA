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

def generar_repechaje_uefa(df, random_state = None):
    #Asignamos llave aleatoria a cada uno
    df_shuffle = df.sample(frac = 1, random_state = random_state)

    df_shuffle['llave'] = np.repeat([1,2,3,4], 4)
    #Definimos ganadores
    ganadores = df_shuffle.groupby('llave').sample(1, random_state = random_state)

    return ganadores


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

    # Ganadores de repechaje
    if clasificados_uefa is None:
        ganadores_uefa = generar_repechaje_uefa(df_repechaje_uefa, random_state=random_state)['codigo'].tolist()
    else:
        ganadores_uefa = clasificados_uefa

    if clasificados_fifa is None:
        ganadores_fifa = generar_repechaje_fifa(df_repechaje_fifa, random_state=random_state)['codigo'].tolist()
    else:
        ganadores_fifa = clasificados_fifa

    df_uefa_ganadores = df_repechaje_uefa[df_repechaje_uefa['codigo'].isin(ganadores_uefa)].copy()
    df_uefa_ganadores['repechaje'] = 1

    df_fifa_ganadores = df_repechaje_fifa[df_repechaje_fifa['codigo'].isin(ganadores_fifa)].copy()
    df_fifa_ganadores['repechaje'] = 1

    # Concatenamos repechajes al bombo 4
    bombo4 = pd.concat([bombo4, df_uefa_ganadores, df_fifa_ganadores]).reset_index(drop=True)
    bombo4['bombo'] = 4  # aseguramos que sigan siendo del bombo 4

    #Limpiamos cols
    columnas_base = ['codigo', 'confederacion', 'anfitrion', 'bombo']

    bombo1 = bombo1[columnas_base]
    bombo2 = bombo2[columnas_base]
    bombo3 = bombo3[columnas_base]

    # Para bombo4, incluimos 'repechaje'
    columnas_bombo4 = columnas_base + ['repechaje']
    bombo4 = bombo4[columnas_bombo4]

    # Concatenamos todos los bombos
    df_final = pd.concat([bombo1, bombo2, bombo3, bombo4]).reset_index(drop=True)

    df_final['repechaje'] = df_final['repechaje'].fillna(0).astype(int)
    df_final['anfitrion'] = df_final['anfitrion'].fillna(0).astype(int)



    return df_final, bombo1, bombo2, bombo3, bombo4



df_bombos, bombo1, bombo2, bombo3, bombo4 = asignar_bombos(df_clasificados, df_power_ranking, random_state=42)

print(df_bombos)