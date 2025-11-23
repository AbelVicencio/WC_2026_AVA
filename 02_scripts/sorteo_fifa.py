import asyncio
import random
import string
import pandas as pd
from nicegui import ui, app
from simular_bombos import df_bombos
from simular_sorteo_func import checker_validez_grupo, lookahead

# --- Configuration & Styles ---
HEADER_STYLE = "font-size: 2em; font-weight: bold; color: #1976D2; text-align: center; margin-bottom: 20px;"
CARD_STYLE = "min-width: 220px; min-height: 260px; background-color: #f5f5f5; border-radius: 10px; padding: 10px; transition: all 0.3s ease;"
SLOT_STYLE = "padding: 4px; margin: 2px; border-bottom: 1px solid #ddd; font-size: 0.9em; width: 100%;"
HIGHLIGHT_STYLE = "background-color: #fff59d; transform: scale(1.05);"

# --- Data & Mappings ---
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

# --- State Management Class ---
class SorteoManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grupos = list(string.ascii_uppercase[:12])
        self.grupos_dict = {g: [] for g in self.grupos}
        self.bombos_slots = {g: [f"{g}{i}" for i in range(1, 5)] for g in self.grupos}
        self.asignaciones = {}
        self.current_bombo = 1
        self.processing = False
        self.logs = []
        self.finished = False

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 50:
            self.logs.pop(0)

# --- Main Page ---
@ui.page('/')
def index():
    ui.colors(primary='#1976D2', secondary='#26A69A', accent='#9C27B0', positive='#21BA45')
    ui.add_head_html('<style>body { background-color: #e3f2fd; }</style>')

    # Local state for this session
    state = SorteoManager()
    group_cards = {} # Map group_name -> ui.card
    
    # UI References
    log_container = None
    draw_button = None

    # --- UI Helper Functions ---
    def refresh_groups_ui():
        for g in state.grupos:
            card = group_cards.get(g)
            if card:
                card.clear()
                with card:
                    ui.label(f"Grupo {g}").style("font-weight: bold; font-size: 1.2em; color: #333; margin-bottom: 5px;")
                    teams = state.grupos_dict[g]
                    
                    # Create a map of slot -> team
                    slot_map = {}
                    for t in teams:
                        slot_num = int(t['slot'][-1])
                        slot_map[slot_num] = t
                    
                    for i in range(1, 5):
                        team_data = slot_map.get(i)
                        
                        with ui.row().classes('items-center no-wrap').style(SLOT_STYLE):
                            # Slot Label
                            ui.label(f"{g}{i}").style("font-weight: bold; margin-right: 6px; min-width: 25px; color: #555;")
                            
                            if team_data:
                                code = team_data['codigo']
                                iso = FIFA_TO_ISO.get(code, '').lower()
                                
                                # Flag
                                if iso:
                                    ui.image(f"https://flagcdn.com/h24/{iso}.png").style("width: 24px; height: auto; margin-right: 8px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.2);")
                                else:
                                    ui.icon('flag', size='xs').style("margin-right: 8px; color: #ccc;")
                                
                                # Name & Conf
                                ui.label(f"{code}").style("font-weight: bold; color: #000; margin-right: 4px;")
                                ui.label(f"({team_data['conf']})").style("font-size: 0.8em; color: #666;")
                            else:
                                ui.label("---").style("color: #aaa;")

    def update_log_ui():
        if log_container:
            log_container.clear()
            with log_container:
                for msg in reversed(state.logs):
                    ui.label(msg).style("font-size: 0.8em; font-family: monospace;")

    async def highlight_group(group_name):
        if group_name in group_cards:
            card = group_cards[group_name]
            card.style(HIGHLIGHT_STYLE)
            await asyncio.sleep(0.5)
            card.style(CARD_STYLE)

    # --- Logic Functions (Closure over state) ---
    async def run_bombo_1():
        state.log("--- INICIANDO BOMBO 1 ---")
        update_log_ui()
        
        # 1. Asignar Anfitriones
        anfitriones = {"MEX": "A1", "CAN": "B1", "USA": "D1"}
        
        for eq, slot in anfitriones.items():
            await asyncio.sleep(0.5)
            conf = df_bombos.loc[df_bombos['codigo'] == eq, 'confederacion'].iloc[0]
            grupo = slot[0]
            
            state.asignaciones[eq] = {"grupo": grupo, "slot": slot, "conf": conf}
            state.grupos_dict[grupo].append({"codigo": eq, "slot": slot, "conf": conf})
            
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
        
        grupos_disponibles = [g for g in state.bombos_slots.keys() if g not in ('A', 'B', 'D')]
        
        for grupo in grupos_disponibles:
            await asyncio.sleep(0.5)
            eq_sorteado = eq_restantes_bombo_1['codigo'].sample(1).iloc[0]
            fila_eq = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] == eq_sorteado].iloc[0]
            conf = fila_eq['confederacion']
            
            eq_restantes_bombo_1 = eq_restantes_bombo_1[eq_restantes_bombo_1['codigo'] != eq_sorteado]
            
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
        state.log(f"--- INICIANDO BOMBO {n} ---")
        update_log_ui()
        
        eq_bombo = df_bombos[df_bombos['bombo'] == n].copy()
        grupos_orden = list(state.bombos_slots.keys())
        
        for _ in grupos_orden:
            if eq_bombo.empty: break
                
            await asyncio.sleep(0.8)
            
            eq_sorteado = eq_bombo['codigo'].sample(1).iloc[0]
            eq_bombo = eq_bombo[eq_bombo['codigo'] != eq_sorteado]
            
            state.log(f"Sorteando equipo: {eq_sorteado}...")
            update_log_ui()
            
            grupo_asignado = None
            
            for g in grupos_orden:
                if len(state.grupos_dict[g]) >= n: continue
                if not checker_validez_grupo(g, eq_sorteado, state.grupos_dict, verbose=False): continue
                
                remaining_teams = list(eq_bombo['codigo'])
                if not lookahead(g, eq_sorteado, remaining_teams, state.grupos_dict, state.bombos_slots, n):
                    continue
                    
                grupo_asignado = g
                break
                
            if grupo_asignado is None:
                state.log(f"ERROR CRÍTICO: No se encontró grupo para {eq_sorteado}")
                ui.notify(f"Error: No valid group for {eq_sorteado}", type='negative')
                return
                
            slot_sorteado = random.choice(state.bombos_slots[grupo_asignado])
            state.bombos_slots[grupo_asignado].remove(slot_sorteado)
            
            conf_sorteado = df_bombos.loc[df_bombos['codigo'] == eq_sorteado, 'confederacion'].iloc[0]
            
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

    # --- Layout Construction ---
    with ui.column().classes('w-full items-center'):
        ui.label('Sorteo FIFA World Cup 2026').style(HEADER_STYLE)
        
        with ui.row().classes('w-full justify-center q-mb-md'):
            draw_button = ui.button('Iniciar Sorteo', on_click=start_simulation).props('push color=primary icon=play_arrow')
            ui.button('Reiniciar', on_click=lambda: ui.navigate.reload()).props('outline color=secondary icon=refresh')

        # Groups Grid
        with ui.grid(columns=4).classes('w-full q-pa-md gap-4').style("max-width: 1400px;"):
            for g in state.grupos:
                with ui.card().style(CARD_STYLE) as card:
                    group_cards[g] = card
                    ui.label(f"Grupo {g}").style("font-weight: bold;")
        
        # Log Area
        with ui.expansion('Registro del Sorteo', icon='list', value=True).classes('w-full q-pa-md').style("max-width: 1400px; background-color: white; border-radius: 8px;"):
            log_container = ui.column().classes('w-full').style("max-height: 200px; overflow-y: auto;")

    refresh_groups_ui()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=5555, title="Sorteo FIFA 2026")
