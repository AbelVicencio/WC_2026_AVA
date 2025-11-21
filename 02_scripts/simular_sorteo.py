import pandas as pd
import numpy as np
import random

from WC_2026 import asignar_bombos, generar_repechaje_uefa, generar_repechaje_fifa

#Importamos lista de selecciones clasificadas y dejamos slots para las de repechaje

df_clasificados = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Clasificados')

df_repechaje_uefa = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Repechaje_UEFA')

df_repechaje_fifa = pd.read_excel('01_datos_brutos/Clasificados_WC_26.xlsx', 
                                sheet_name='Repechaje_FIFA')

#Cargamos Power Ranking FIFA

df_power_ranking = pd.read_csv('01_datos_brutos/FIFA_PR_19_11_2025.csv').drop(columns=['Unnamed: 7'])

#Cargamos bombos
df_bombos, bombo1, bombo2, bombo3, bombo4 = asignar_bombos(df_clasificados, df_power_ranking, random_state=42)

def generar_sorteo_bombo1(bombo1, random_state = None):
    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Preasignaciones: hosts
    preasignaciones = {
        'MEX': 'A1',
        'CAN': 'B1',
        'USA': 'D1'
    }

     # Equipos restantes del bombo 1
    equipos_restantes = [eq for eq in bombo1['codigo'] if eq not in preasignaciones]

    # Grupos disponibles para asignar los equipos restantes
    # Los slots de los cabezas de serie ya están ocupados
    grupos_orden = ['C','E','F','G','H','I','J','K','L']  # solo los grupos que faltan
    slots_disponibles = [g+'1' for g in grupos_orden]  # todos les tocará "1" porque es Bombo 1
    
    for equipo in equipos_restantes:
        # "Sacamos una bolita" de los equipos: seleccion random
        elegido = equipo  # aquí ya está iterando, si quieres random dentro de equipos_restantes se hace otra vez
        # Sacamos una bolita de slots disponibles
        slot = slots_disponibles.pop(0)  # primera disponible según orden definido (C1, E1...)
        
        preasignaciones[elegido] = slot
        print(f"Equipo '{elegido}' asignado al grupo '{slot}'")

     # Convertimos a DataFrame
    df_cabezas = pd.DataFrame({
        'codigo': list(preasignaciones.keys()),
        'grupo_id': list(preasignaciones.values())
    })
    
    return df_cabezas


resultado_cabezas_step = generar_sorteo_bombo1(bombo1, random_state=41)
print("\nResultado final Bombo 1:")
print(resultado_cabezas_step)