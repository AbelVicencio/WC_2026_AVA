"""
Sorteo FIFA World Cup 2026 - Simulación Interactiva con NiceGUI

Este script implementa una aplicación web interactiva para simular el sorteo de la Copa Mundial de la FIFA 2026.
Utiliza la librería NiceGUI para el frontend y se integra con scripts de lógica de sorteo (`simular_bombos` y `simular_sorteo_func`)
para garantizar que se cumplan todas las restricciones geográficas y de bombos.

Características principales:
- Interfaz reactiva y visualmente atractiva.
- Simulación asíncrona para permitir animaciones sin bloquear el servidor.
- Visualización de banderas de países mediante FlagCDN.
- Registro en tiempo real de los eventos del sorteo.
"""

import asyncio
import random
import string
import pandas as pd
from nicegui import ui, app
from simular_bombos import df_bombos
from simular_sorteo_func import checker_validez_grupo, lookahead

# --- Configuración y Estilos ---
# Definimos estilos CSS en línea para mantener el código autocontenido y facilitar la personalización.
HEADER_STYLE = "font-size: 2em; font-weight: bold; color: #1976D2; text-align: center; margin-bottom: 20px;"
CARD_STYLE = "min-width: 220px; min-height: 260px; background-color: #f5f5f5; border-radius: 10px; padding: 10px; transition: all 0.3s ease;"
SLOT_STYLE = "padding: 4px; margin: 2px; border-bottom: 1px solid #ddd; font-size: 0.9em; width: 100%;"
HIGHLIGHT_STYLE = "background-color: #fff59d; transform: scale(1.05);"

# --- Datos y Mapeos ---
# Diccionario para mapear códigos FIFA (3 letras) a códigos ISO (2 letras) para obtener las banderas.
# Esto es necesario porque FlagCDN utiliza códigos ISO.
FIFA_TO_ISO = {
    'AFG': 'af', 'ALB': 'al', 'ALG': 'dz', 'ASA': 'as', 'AND': 'ad', 'ANG': 'ao', 'AIA': 'ai', 'ATG': 'ag',
    'ARG': 'ar', 'ARM': 'am', 'ARU': 'aw', 'AUS': 'au', 'AUT': 'at', 'AZE': 'az', 'BAH': 'bs', 'BHR': 'bh',
    'BAN': 'bd', 'BRB': 'bb', 'BLR': 'by', 'BEL': 'be', 'BLZ': 'bz', 'BEN': 'bj', 'BER': 'bm', 'BHU': 'bt',
    'BOL': 'bo', 'BIH': 'ba', 'BOT': 'bw', 'BRA': 'br', 'VGB': 'vg', 'BRU': 'bn', 'BUL': 'bg', 'BFA': 'bf',
    'BDI': 'bi', 'CAM': 'kh', 'CMR': 'cm', 'CAN': 'ca', 'CPV': 'cv', 'CAY': 'ky', 'CTA': 'cf', 'CHA': 'td',
    'CHI': 'cl', 'CHN': 'cn', 'TPE': 'tw', 'COL': 'co', 'COM': 'km', 'CGO': 'cg', 'COK': 'ck', 'CRC': 'cr',
    'CRO': 'hr', 'CUB': 'cu', 'CUW': 'cw', 'CYP': 'cy', 'CZE': 'cz', 'DEN': 'dk', 'DJI': 'dj', 'DMA': 'dm',
    'DOM': 'do', 'COD': 'cd', 'ECU': 'ec', 'EGY': 'eg', 'SLV': 'sv', 'ENG': 'gb-eng', 'EQG': 'gq', 'ERI': 'er',
    'EST': 'ee', 'ETH': 'et', 'FRO': 'fo', 'FIJ': 'fj', 'FIN': 'fi', 'FRA': 'fr', 'GAB': 'ga', 'GAM': 'gm',
    'GEO': 'ge', 'GER': 'de', 'GHA': 'gh', 'GIB': 'gi', 'GRE': 'gr', 'GRN': 'gd', 'GUM': 'gu', 'GUA': 'gt',
    'GUI': 'gn', 'GNB': 'gw', 'GUY': 'gy', 'HAI': 'ht', 'HON': 'hn', 'HKG': 'hk', 'HUN': 'hu', 'ISL': 'is',
    'IND': 'in', 'IDN': 'id', 'IRN': 'ir', 'IRQ': 'iq', 'ISR': 'il', 'ITA': 'it', 'CIV': 'ci', 'JAM': 'jm',
    'JPN': 'jp', 'JOR': 'jo', 'KAZ': 'kz', 'KEN': 'ke', 'PRK': 'kp', 'KOR': 'kr', 'KUW': 'kw', 'KGZ': 'kg',
    'LAO': 'la', 'LVA': 'lv', 'LBN': 'lb', 'LES': 'ls', 'LBR': 'lr', 'LBY': 'ly', 'LIE': 'li', 'LTU': 'lt',
    'LUX': 'lu', 'MAC': 'mo', 'MKD': 'mk', 'MAD': 'mg', 'MWI': 'mw', 'MAS': 'my', 'MDV': 'mv', 'MLI': 'ml',
    'MLT': 'mt', 'MTN': 'mr', 'MRI': 'mu', 'MEX': 'mx', 'MDA': 'md', 'MNG': 'mn', 'MNE': 'me', 'MSR': 'ms',
    'MAR': 'ma', 'MOZ': 'mz', 'MYA': 'mm', 'NAM': 'na', 'NEP': 'np', 'NED': 'nl', 'NCL': 'nc', 'NZL': 'nz',
    'NCA': 'ni', 'NIG': 'ne', 'NGA': 'ng', 'NIR': 'gb-nir', 'NOR': 'no', 'OMA': 'om', 'PAK': 'pk', 'PLE': 'ps',
    'PAN': 'pa', 'PNG': 'pg', 'PAR': 'py', 'PER': 'pe', 'PHI': 'ph', 'POL': 'pl', 'POR': 'pt', 'PUR': 'pr',
    'QAT': 'qa', 'IRL': 'ie', 'ROU': 'ro', 'RUS': 'ru', 'RWA': 'rw', 'SKN': 'kn', 'LCA': 'lc', 'VIN': 'vc',
    'SAM': 'ws', 'SMR': 'sm', 'STP': 'st', 'KSA': 'sa', 'SCO': 'gb-sct', 'SEN': 'sn', 'SRB': 'rs', 'SEY': 'sc',
    'SLE': 'sl', 'SIN': 'sg', 'SVK': 'sk', 'SVN': 'si', 'SOL': 'sb', 'SOM': 'so', 'RSA': 'za', 'ESP': 'es',
    'SRI': 'lk', 'SDN': 'sd', 'SUR': 'sr', 'SWE': 'se', 'SUI': 'ch', 'SYR': 'sy', 'TAH': 'pf', 'TJK': 'tj',
    'TAN': 'tz', 'THA': 'th', 'TLS': 'tl', 'TOG': 'tg', 'TGA': 'to', 'TRI': 'tt', 'TUN': 'tn', 'TUR': 'tr',
    'TKM': 'tm', 'TCA': 'tc', 'UGA': 'ug', 'UKR': 'ua', 'UAE': 'ae', 'USA': 'us', 'URU': 'uy', 'VIR': 'vi',
    'UZB': 'uz', 'VAN': 'vu', 'VEN': 've', 'VIE': 'vn', 'WAL': 'gb-wls', 'YEM': 'ye', 'ZAM': 'zm', 'ZIM': 'zw'
}

# --- Clase de Gestión de Estado ---
class SorteoManager:
    """
    Gestiona el estado completo de una sesión de sorteo.
    
    Mantiene la información sobre los grupos, los equipos asignados, los slots disponibles
    y el registro de eventos. Al encapsular el estado aquí, facilitamos el reinicio
    del sorteo sin necesidad de recargar la página completa.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia el estado a los valores iniciales para un nuevo sorteo."""
        self.grupos = list(string.ascii_uppercase[:12])  # Grupos A-L
        self.grupos_dict = {g: [] for g in self.grupos}  # Equipos en cada grupo
        # Slots disponibles (ej: A1, A2, A3, A4)
        self.bombos_slots = {g: [f"{g}{i}" for i in range(1, 5)] for g in self.grupos}
        self.asignaciones = {}
        self.current_bombo = 1
        self.processing = False  # Flag para evitar múltiples ejecuciones simultáneas
        self.logs = []
        self.finished = False

    def log(self, message):
        """Agrega un mensaje al registro de eventos."""
        self.logs.append(message)
        if len(self.logs) > 50:  # Mantenemos solo los últimos 50 mensajes
            self.logs.pop(0)

# --- Página Principal ---
@ui.page('/')
def index():
    """
    Define la estructura y lógica de la página principal de la aplicación.
    
    En NiceGUI, las funciones decoradas con @ui.page se ejecutan para cada nuevo cliente
    que se conecta. Esto significa que cada usuario tiene su propia instancia de `SorteoManager`
    y su propio estado visual.
    """
    ui.colors(primary='#1976D2', secondary='#26A69A', accent='#9C27B0', positive='#21BA45')
    ui.add_head_html('<style>body { background-color: #e3f2fd; }</style>')

    # Estado local para esta sesión
    state = SorteoManager()
    group_cards = {} # Mapa para acceder rápidamente a las tarjetas UI de cada grupo
    
    # Referencias a componentes UI que necesitan ser actualizados dinámicamente
    log_container = None
    draw_button = None

    # --- Funciones Auxiliares de UI ---
    def refresh_groups_ui():
        """
        Actualiza la visualización de todos los grupos.
        
        Recorre el estado actual (`state.grupos_dict`) y reconstruye el contenido
        de las tarjetas de grupo. Se llama después de cada asignación para reflejar los cambios.
        """
        for g in state.grupos:
            card = group_cards.get(g)
            if card:
                card.clear()
                with card:
                    # Título del Grupo
                    ui.label(f"Grupo {g}").style("font-weight: bold; font-size: 1.2em; color: #333; margin-bottom: 5px;")
                    teams = state.grupos_dict[g]
                    
                    # Mapeamos los equipos a sus slots (1, 2, 3, 4) para mostrarlos en orden
                    slot_map = {}
                    for t in teams:
                        slot_num = int(t['slot'][-1])
                        slot_map[slot_num] = t
                    
                    # Renderizamos los 4 slots del grupo
                    for i in range(1, 5):
                        team_data = slot_map.get(i)
                        
                        with ui.row().classes('items-center no-wrap').style(SLOT_STYLE):
                            # Etiqueta del Slot (ej: A1)
                            ui.label(f"{g}{i}").style("font-weight: bold; margin-right: 6px; min-width: 25px; color: #555;")
                            
                            if team_data:
                                code = team_data['codigo']
                                iso = FIFA_TO_ISO.get(code, '').lower()
                                
                                # Bandera
                                if iso:
                                    ui.image(f"https://flagcdn.com/h24/{iso}.png").style("width: 24px; height: auto; margin-right: 8px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.2);")
                                else:
                                    ui.icon('flag', size='xs').style("margin-right: 8px; color: #ccc;")
                                
                                # Nombre y Confederación
                                ui.label(f"{code}").style("font-weight: bold; color: #000; margin-right: 4px;")
                                ui.label(f"({team_data['conf']})").style("font-size: 0.8em; color: #666;")
                            else:
                                # Slot vacío
                                ui.label("---").style("color: #aaa;")

    def update_log_ui():
        """Actualiza el panel de registros con los últimos mensajes del sistema."""
        if log_container:
            log_container.clear()
            with log_container:
                for msg in reversed(state.logs):
                    ui.label(msg).style("font-size: 0.8em; font-family: monospace;")

    async def highlight_group(group_name):
        """
        Aplica un efecto visual temporal a un grupo para indicar actividad.
        
        Args:
            group_name (str): La letra del grupo a resaltar (ej: 'A').
        """
        if group_name in group_cards:
            card = group_cards[group_name]
            card.style(HIGHLIGHT_STYLE)
            await asyncio.sleep(0.5) # Mantiene el resaltado por 0.5 segundos
            card.style(CARD_STYLE)   # Restaura el estilo original

    # --- Funciones de Lógica del Sorteo (Clausuras sobre `state`) ---
    
    async def run_bombo_1():
        """
        Ejecuta la lógica de sorteo para el Bombo 1 (Cabezas de Serie).
        
        El Bombo 1 tiene reglas especiales:
        1. Los anfitriones (MEX, CAN, USA) se asignan a grupos predefinidos.
        2. El resto de cabezas de serie se asignan aleatoriamente a los grupos restantes.
        """
        state.log("--- INICIANDO BOMBO 1 ---")
        update_log_ui()
        
        # 1. Asignar Anfitriones (Regla fija)
        anfitriones = {"MEX": "A1", "CAN": "B1", "USA": "D1"}
        
        for eq, slot in anfitriones.items():
            await asyncio.sleep(0.5) # Pausa para animación
            conf = df_bombos.loc[df_bombos['codigo'] == eq, 'confederacion'].iloc[0]
            grupo = slot[0]
            
            # Actualizar estado
            state.asignaciones[eq] = {"grupo": grupo, "slot": slot, "conf": conf}
            state.grupos_dict[grupo].append({"codigo": eq, "slot": slot, "conf": conf})
            
            # Eliminar slot usado
            if slot in state.bombos_slots[grupo]:
                state.bombos_slots[grupo].remove(slot)
                
            state.log(f"ANFITRIÓN: {eq} asignado a {grupo} ({slot})")
            refresh_groups_ui()
            update_log_ui()
            await highlight_group(grupo)

        # 2. Resto del Bombo 1
        eq_restantes_bombo_1 = df_bombos[
            (~df_bombos['codigo'].isin(['MEX', 'USA', 'CAN'])) &
            (df_bombos['bombo'] == 1)
        ]
        
        # Grupos disponibles (excluyendo los de anfitriones)
        grupos_disponibles = [g for g in state.bombos_slots.keys() if g not in ('A', 'B', 'D')]
        
        for grupo in grupos_disponibles:
            await asyncio.sleep(0.5)
            # Selección aleatoria
            eq_sorteado = eq_restantes_bombo_1['codigo'].sample(1).iloc[0]
            fila_eq = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] == eq_sorteado].iloc[0]
            conf = fila_eq['confederacion']
            
            # Retirar del pool
            eq_restantes_bombo_1 = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] != eq_sorteado]
            
            # Asignar al slot 1 del grupo actual
            slot = grupo + "1"
            state.asignaciones[eq_sorteado] = {"grupo": grupo, "slot": slot, "conf": conf}
            state.grupos_dict[grupo].append({"codigo": eq_sorteado, "slot": slot, "conf": conf})
            
            if slot in state.bombos_slots[grupo]:
                state.bombos_slots[grupo].remove(slot)
                
            state.log(f"SORTEO: {eq_sorteado} cabeza de serie Grupo {grupo}")
            refresh_groups_ui()
            update_log_ui()
            await highlight_group(grupo)

    async def run_bombo_n(n):
        """
        Ejecuta la lógica de sorteo para los Bombos 2, 3 y 4.
        
        Args:
            n (int): Número de bombo a sortear.
            
        Lógica:
        1. Itera sobre los grupos en orden (A-L).
        2. Para cada grupo, extrae una bola (equipo) del bombo actual.
        3. Verifica restricciones geográficas y realiza 'lookahead' para evitar bloqueos.
        4. Asigna el equipo a un grupo válido y a un slot aleatorio dentro de ese grupo.
        """
        state.log(f"--- INICIANDO BOMBO {n} ---")
        update_log_ui()
        
        eq_bombo = df_bombos[df_bombos['bombo'] == n].copy()
        grupos_orden = list(state.bombos_slots.keys())
        
        # Intentamos llenar un cupo en cada grupo
        for _ in grupos_orden:
            if eq_bombo.empty: break
                
            await asyncio.sleep(0.8) # Pausa un poco más larga para suspense
            
            # Sacar equipo del bombo
            eq_sorteado = eq_bombo['codigo'].sample(1).iloc[0]
            eq_bombo = eq_bombo[eq_bombo['codigo'] != eq_sorteado]
            
            state.log(f"Sorteando equipo: {eq_sorteado}...")
            update_log_ui()
            
            grupo_asignado = None
            
            # Buscar grupo válido
            for g in grupos_orden:
                # 1. Verificar si el grupo ya está lleno para este nivel de bombo
                if len(state.grupos_dict[g]) >= n: continue
                
                # 2. Verificar restricciones de confederación (ej: no más de 1 de CONMEBOL)
                if not checker_validez_grupo(g, eq_sorteado, state.grupos_dict, verbose=False): continue
                
                # 3. Lookahead: Verificar si esta asignación bloquearía el sorteo futuro
                remaining_teams = list(eq_bombo['codigo'])
                if not lookahead(g, eq_sorteado, remaining_teams, state.grupos_dict, state.bombos_slots, n):
                    continue
                    
                grupo_asignado = g
                break
                
            if grupo_asignado is None:
                state.log(f"ERROR CRÍTICO: No se encontró grupo para {eq_sorteado}")
                ui.notify(f"Error: No valid group for {eq_sorteado}", type='negative')
                return
                
            # Asignar slot aleatorio dentro del grupo (ej: si quedan A2, A3, A4, elige uno al azar)
            slot_sorteado = random.choice(state.bombos_slots[grupo_asignado])
            state.bombos_slots[grupo_asignado].remove(slot_sorteado)
            
            conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]
            
            # Guardar asignación
            state.grupos_dict[grupo_asignado].append({
                "codigo": eq_sorteado,
                "slot": slot_sorteado,
                "conf": conf_sorteado
            })
            
            state.asignaciones[eq_sorteado] = {
                "grupo": grupo_asignado,
                "slot": slot_sorteado,
                "conf": conf_sorteado
            }
            
            state.log(f"-> Asignado a Grupo {grupo_asignado} (Slot {slot_sorteado})")
            refresh_groups_ui()
            update_log_ui()
            await highlight_group(grupo_asignado)

    async def start_simulation():
        """
        Orquesta el proceso completo de simulación.
        
        Se ejecuta al presionar el botón 'Iniciar Sorteo'.
        Ejecuta secuencialmente el sorteo de los bombos 1, 2, 3 y 4.
        """
        if state.processing: return
        state.processing = True
        if draw_button: draw_button.disable()
        state.reset()
        refresh_groups_ui()
        update_log_ui()
        
        try:
            await run_bombo_1()
            for n in range(2, 5):
                await run_bombo_n(n)
            state.log("--- SORTEO FINALIZADO ---")
            ui.notify("Sorteo Finalizado con Éxito", type='positive')
            state.finished = True
        except Exception as e:
            state.log(f"Error: {str(e)}")
            ui.notify(f"Error durante el sorteo: {e}", type='negative')
            raise e
        finally:
            state.processing = False
            if draw_button: draw_button.enable()
            update_log_ui()

    # --- Construcción del Layout ---
    with ui.column().classes('w-full items-center'):
        ui.label('Sorteo FIFA World Cup 2026').style(HEADER_STYLE)
        
        with ui.row().classes('w-full justify-center q-mb-md'):
            draw_button = ui.button('Iniciar Sorteo', on_click=start_simulation).props('push color=primary icon=play_arrow')
            ui.button('Reiniciar', on_click=lambda: ui.navigate.reload()).props('outline color=secondary icon=refresh')

        # Grid de Grupos
        with ui.grid(columns=4).classes('w-full q-pa-md gap-4').style("max-width: 1400px;"):
            for g in state.grupos:
                with ui.card().style(CARD_STYLE) as card:
                    group_cards[g] = card
                    ui.label(f"Grupo {g}").style("font-weight: bold;")
        
        # Área de Registros
        with ui.expansion('Registro del Sorteo', icon='list', value=True).classes('w-full q-pa-md').style("max-width: 1400px; background-color: white; border-radius: 8px;"):
            log_container = ui.column().classes('w-full').style("max-height: 200px; overflow-y: auto;")

    refresh_groups_ui()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=5555, title="Sorteo FIFA 2026")
