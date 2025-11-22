import pandas as pd
import numpy as np
import random
import string
from pprint import pprint


from simular_bombos import asignar_bombos, generar_repechaje_uefa, generar_repechaje_fifa

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
df_bombos, bombo1, bombo2, bombo3, bombo4 = asignar_bombos(df_clasificados, random_state=42)



#Generamos esqueleto
grupos = list(string.ascii_uppercase[:12])  # A-L
asignaciones_sorteo = {}

#Generamos los bombos de cada grupo (slots)
bombos_slots = {}
for grupo in grupos:
    bombos_slots[grupo] = [f"{grupo}{i}" for i in range(1, 5)]

#Asignaciones de Anfitriones
anfitriones = {
    "MEX": "A1",
    "CAN": "B1",
    "USA": "D1"
}

for eq, slot in anfitriones.items():
    conf = df_bombos.loc[df_bombos['codigo'] == eq, 'confederacion'].iloc[0]
    grupo = slot[0]       # "A", "B", "D"
    
    asignaciones_sorteo[eq] = {
        "grupo": grupo,
        "slot": slot,
        "conf": conf
    }

#Retiramos las bolitas rojas de Anfitriones
bombos_slots['A'].remove("A1")
bombos_slots['B'].remove("B1")
bombos_slots['D'].remove("D1")

#Equipos restantes bombo 1
eq_restantes_bombo_1 = df_bombos[
    (~df_bombos['codigo'].isin(['MEX', 'USA', 'CAN'])) &
    (df_bombos['bombo'] == 1)
]

print("----BOMBO 1: CABEZAS DE GRUPO----")

for grupo in bombos_slots.keys():
    if grupo not in ('A', 'B', 'D'):
        # Selecciona equipo
        eq_sorteado = eq_restantes_bombo_1['codigo'].sample(1).iloc[0]  # Bolita país
        fila_eq = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] == eq_sorteado].iloc[0]
        conf = fila_eq['confederacion']  # Ajusta nombre si es distinto

        # Quitamos bolita del bombo de países
        eq_restantes_bombo_1 = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] != eq_sorteado]

        # Asignamos grupo y slot
        slot = grupo + "1"
        asignaciones_sorteo[eq_sorteado] = {
            "grupo": grupo,
            "slot": slot,
            "conf": conf
        }

        # Quitamos slot del bombo de grupos
        bombos_slots[grupo].remove(slot)

        print(f"{eq_sorteado} ({conf}) cabeza de Grupo {grupo} → slot {slot}")




grupos_dict = {g: [] for g in grupos}

for equipo, info in asignaciones_sorteo.items():
    grupos_dict[info["grupo"]].append({
        "codigo": equipo,
        "slot": info["slot"],
        "conf": info["conf"]
    })


def checker_validez_grupo(grupo, eq_sorteado, grupos_dict):
    #Confederacion del sorteado
    conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]

    #Equipos en grupo
    equipos_en_grupo = grupos_dict[grupo]

    #Extraer confederaciones ya asignadas
    confs = [e['conf'] for e in equipos_en_grupo]

    #Contamos apariciones de confederacion
    conf_counts = pd.Series(confs).value_counts()

    #-----Constraints FIFA------

    if conf_sorteado != 'UEFA':
        if conf_sorteado in conf_counts.index:
            print(f"Otro equipo de {conf_sorteado}. Reasignando...")
            return False
    else:
        #UEFA permite máximo 2
        if conf_counts.get('UEFA', 0) >= 2:
            print("Dos equipos de UEFA actuales. Reasignando...")
            return False
        
    return True


#Bombo 2:

print("----BOMBO 2----")


grupos = list(bombos_slots.keys())  # A→L

eq_bombo_2 = df_bombos[df_bombos['bombo'] == 2].copy()

for grupo_actual in grupos:
    if eq_bombo_2.empty:
        break  # No quedan equipos

    #Sacamos un equipo del bombo 2
    eq_sorteado = eq_bombo_2['codigo'].sample(1).iloc[0]
    eq_bombo_2 = eq_bombo_2[eq_bombo_2['codigo'] != eq_sorteado]

    #Intentar asignarlo al grupo_actual o siguiente grupo disponible
    grupo_asignado = None
    indice_actual = grupos.index(grupo_actual)
    grupos_circulares = grupos[indice_actual:] + grupos[:indice_actual]  # A→L circular desde actual

    for g in grupos_circulares:
        # Constraint: máximo 2 equipos en este grupo (bombo 2)
        if len(grupos_dict[g]) >= 2:
            continue

        # Constraint de confederación
        if checker_validez_grupo(g, eq_sorteado, grupos_dict):
            grupo_asignado = g
            break

    if grupo_asignado is None:
        raise ValueError(f"No hay grupo válido para {eq_sorteado}. Revisa constraints!")

    #Elegir slot aleatorio
    slot_sorteado = random.choice(bombos_slots[grupo_asignado])
    bombos_slots[grupo_asignado].remove(slot_sorteado)

    #Actualizar dicts
    conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]
    grupos_dict[grupo_asignado].append({
        "codigo": eq_sorteado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    })
    asignaciones_sorteo[eq_sorteado] = {
        "grupo": grupo_asignado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    }

    print(f"{eq_sorteado} → Grupo {grupo_asignado}, slot {slot_sorteado}")



#Bombo 3:

print("----BOMBO 3----")

grupos = list(bombos_slots.keys())  # A→L

eq_bombo_3 = df_bombos[df_bombos['bombo'] == 3].copy()

for grupo_actual in grupos:
    if eq_bombo_3.empty:
        break  # No quedan equipos

    #Sacamos un equipo del bombo 3
    eq_sorteado = eq_bombo_3['codigo'].sample(1).iloc[0]
    eq_bombo_3 = eq_bombo_3[eq_bombo_3['codigo'] != eq_sorteado]

    #Intentar asignarlo al grupo_actual o siguiente grupo disponible
    grupo_asignado = None
    indice_actual = grupos.index(grupo_actual)
    grupos_circulares = grupos[indice_actual:] + grupos[:indice_actual]  # A→L circular desde actual

    for g in grupos_circulares:
        # Constraint: máximo 3 equipos en este grupo (bombo 3)
        if len(grupos_dict[g]) >= 3:
            continue

        # Constraint de confederación
        if checker_validez_grupo(g, eq_sorteado, grupos_dict):
            grupo_asignado = g
            break

    if grupo_asignado is None:
        raise ValueError(f"No hay grupo válido para {eq_sorteado}. Revisa constraints!")

    #Elegir slot aleatorio
    slot_sorteado = random.choice(bombos_slots[grupo_asignado])
    bombos_slots[grupo_asignado].remove(slot_sorteado)

    #Actualizar dicts
    conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]
    grupos_dict[grupo_asignado].append({
        "codigo": eq_sorteado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    })
    asignaciones_sorteo[eq_sorteado] = {
        "grupo": grupo_asignado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    }

    print(f"{eq_sorteado} → Grupo {grupo_asignado}, slot {slot_sorteado}")


#Bombo 4:

print("----BOMBO 4----")

grupos = list(bombos_slots.keys())  # A→L

eq_bombo_4 = df_bombos[df_bombos['bombo'] == 4].copy()

for grupo_actual in grupos:
    if eq_bombo_4.empty:
        break  # No quedan equipos

    #Sacamos un equipo del bombo 4
    eq_sorteado = eq_bombo_4['codigo'].sample(1).iloc[0]
    eq_bombo_4 = eq_bombo_4[eq_bombo_4['codigo'] != eq_sorteado]

    #Intentar asignarlo al grupo_actual o siguiente grupo disponible
    grupo_asignado = None
    indice_actual = grupos.index(grupo_actual)
    grupos_circulares = grupos[indice_actual:] + grupos[:indice_actual]  # A→L circular desde actual

    for g in grupos_circulares:
        # Constraint: máximo 4 equipos en este grupo (bombo 4)
        if len(grupos_dict[g]) >= 4:
            continue

        # Constraint de confederación
        if checker_validez_grupo(g, eq_sorteado, grupos_dict):
            grupo_asignado = g
            break

    if grupo_asignado is None:
        raise ValueError(f"No hay grupo válido para {eq_sorteado}. Revisa constraints!")

    #Elegir slot aleatorio
    slot_sorteado = random.choice(bombos_slots[grupo_asignado])
    bombos_slots[grupo_asignado].remove(slot_sorteado)

    #Actualizar dicts
    conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]
    grupos_dict[grupo_asignado].append({
        "codigo": eq_sorteado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    })
    asignaciones_sorteo[eq_sorteado] = {
        "grupo": grupo_asignado,
        "slot": slot_sorteado,
        "conf": conf_sorteado
    }

    print(f"{eq_sorteado} → Grupo {grupo_asignado}, slot {slot_sorteado}")

# Crear lista de filas
filas = []
for grupo, equipos in grupos_dict.items():
    for eq in equipos:
        filas.append({
            "Grupo": grupo,
            "Equipo": eq["codigo"],
            "Slot": eq["slot"],
            "Confederacion": eq["conf"]
        })

# Convertir a DataFrame
df_tabla = pd.DataFrame(filas)

# Mostrar tabla
print(df_bombos)


print(bombos_slots)

