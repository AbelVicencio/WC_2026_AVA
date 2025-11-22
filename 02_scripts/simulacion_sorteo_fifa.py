import pandas as pd
from simular_bombos import df_bombos  
from simular_sorteo_func import sortear_bombo_1, sortear_bombo_n


def main():
    # --- BOMBO 1 ---
    grupos_dict, asignaciones_sorteo, bombos_slots = sortear_bombo_1(df_bombos)

    # --- BOMBOS 2, 3, 4 ---
    for n_bombo in range(2, 5):  # bombos 2, 3, 4
        grupos_dict, asignaciones_sorteo, bombos_slots = sortear_bombo_n(
            n_bombo,
            df_bombos,
            bombos_slots,
            grupos_dict,
            asignaciones_sorteo
        )

    # --- Crear tabla final ---
    filas = []
    for grupo, equipos in grupos_dict.items():
        for eq in equipos:
            filas.append({
                "Grupo": grupo,
                "Equipo": eq["codigo"],
                "Slot": eq["slot"],
                "Confederacion": eq["conf"]
            })

    df_tabla = pd.DataFrame(filas)

    # --- Mostrar por grupo ---
    for grupo in sorted(df_tabla['Grupo'].unique()):
        print(f"\n--- Grupo {grupo} ---")
        tabla = (
            df_tabla[df_tabla['Grupo'] == grupo]
            .sort_values(by="Slot")
            .drop(columns=["Grupo"])
            .reset_index(drop=True)
        )
        print(tabla)

if __name__ == "__main__":
    main()