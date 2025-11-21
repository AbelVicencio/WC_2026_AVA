import pandas as pd
import numpy as np
import random
import string

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


df_bombos, bombo1, bombo2, bombo3, bombo4 = asignar_bombos(df_clasificados, df_power_ranking, random_state=42)

grupos = list(string.ascii_uppercase[:12])  # A-L
bombos_slots = {}

for grupo in grupos:
    bombos_slots[grupo] = [f"{grupo}{i}" for i in range(2, 5)]

# Creamos un diccionario para guardar la asignación final
asignaciones_bombo2 = {}

# Convertimos bombo2['codigo'] en lista de países
paises_bombo2 = bombo2['codigo'].tolist()

# Iteramos sobre los grupos A-L en orden
for grupo in grupos:
    if not paises_bombo2:  # Si ya no quedan países, terminamos
        break
    
    # Sacamos un país aleatorio del bombo2
    pais_sacado = random.choice(paises_bombo2)
    
    # Sacamos un slot disponible del grupo
    slot_sacado = bombos_slots[grupo].pop(0)  # Tomamos el primero
    
    # Guardamos asignación
    asignaciones_bombo2[pais_sacado] = slot_sacado
    
    # Eliminamos el país del bombo2
    paises_bombo2.remove(pais_sacado)

# Convertimos a DataFrame
df_bombo2_asignado = pd.DataFrame({
    'codigo': list(asignaciones_bombo2.keys()),
    'grupo_id': list(asignaciones_bombo2.values())
})

print(df_bombo2_asignado)
