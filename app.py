import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import time
import re
from skills import AI_SKILLS

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y CONEXIÓN ---
@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
        
        # Única transformación necesaria: convertir escapes literales a saltos de línea reales
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Error de Autenticación: {e}")
        st.stop()

# Configuración inicial
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    client = get_gspread_client()
    SPREADSHEET_ID = st.secrets.get("SHEET_ID")
except Exception as e:
    st.error(f"⚠️ Error de configuración inicial: {e}")
    st.stop()

# --- 2. LISTA DE HOJAS Y MAPEO DE DEPARTAMENTOS ---
HOJAS_VALIDAS = [
    "H-PRINCIPAL", "GENERALES", "PNNA", "Hoja 2", "Hoja 1", 
    "PADULTO 19 A 60 AÐOS", "ADULTOS MAYOR", "PSALUD RESPIRATORIA", 
    "ITS-HIV-SIDA", "SANGRE SEGURA", "PREVENCION CANCER CUELLO UTERIN", 
    "PROMOCIËN DE SALUD", "ENDOCRINO-METABOLICO", "CARDIOVASCULAR", 
    "HEREDOMETABËLICAS", "SALUD BUCAL", "SALUD MENTAL", "SSR", 
    "VISITAS Y ABORDAJES", "SALUD RENAL", "NUTRICIËN", 
    "PREVEN ACCD Y HECHOS VIOLENTOS", "DERMATOLOG═A SANITARIA", "Hoja1", 
    "MUSCULOESQUELETICAS", "PREVEN ACCD Y HECHOS VIOLEN ", "ZOONOSIS", "Hoja25"
]

DEPT_SYMBOLS = {
    "PEDIATRIA": "PNNA", "PED": "PNNA", "PEDIAT": "PNNA", "NIÑOS": "PNNA",
    "ADULTO MAYOR": "ADULTOS MAYOR", "GERIATRIA": "ADULTOS MAYOR",
    "GENERAL": "GENERALES", "ODONTOLOGIA": "SALUD BUCAL", "ESTOMATITIS": "SALUD BUCAL"
}

def get_worksheet_activities(ws_name):
    """Obtiene los nombres de actividades con jerarquía (Columna A)."""
    if not ws_name or ws_name not in HOJAS_VALIDAS:
        return []
    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
        ws = sheet.worksheet(ws_name)
        rows = ws.col_values(1)[1:] # Saltar header
        
        hierarchy_list = []
        current_group = ""
        
        # Heurística de jerarquía: si el nombre es corto y genérico (Niño, Niña, Masculino, Femenino)
        # o si parece un ítem dependiente, le pegamos el contexto del grupo anterior.
        items_dependientes = ["NIÑO", "NIÑA", "MASCULINO", "FEMENINO", "FILA", "TOTAL"]
        
        for name in rows:
            name_clean = name.strip()
            if not name_clean: continue
            
            upper_name = name_clean.upper()
            
            # Si es un ítem genérico, usa el grupo actual como prefijo
            if any(x in upper_name for x in items_dependientes) and current_group:
                hierarchy_list.append(f"{current_group} > {name_clean}")
            else:
                current_group = name_clean
                hierarchy_list.append(name_clean)
                
        return hierarchy_list
    except Exception as e:
        print(f"Error cargando actividades de {ws_name}: {e}")
        return []

# --- 3. EL CEREBRO IA ---
def procesar_imagen(imagen_bytes, model_id='gemini-2.0-flash', target_ws=None, known_activities=None, skill_name="EPI (Individual)"):
    model = genai.GenerativeModel(model_id)
    
    lista_actividades_str = "\n".join([f"- {a}" for a in known_activities[:300]]) if known_activities else "No disponible"
    
    # Seleccionar la instrucción según el skill
    base_instruction = AI_SKILLS.get(skill_name, AI_SKILLS["EPI (Individual)"])
    
    system_instruction = f"""
    {base_instruction}
    
    ESTRUCTURA DE FILAS DISPONIBLES EN {target_ws if target_ws else 'la hoja detectada'}:
    {lista_actividades_str}
    
    CONTEXTO ACTUAL:
    - Hoja Sugerida: {target_ws if target_ws else 'Auto-detectar'}
    - Sistema: {skill_name}
    """

    try:
        response = model.generate_content([
            system_instruction, 
            {'mime_type': 'image/jpeg', 'data': imagen_bytes}
        ])
        raw_text = response.text.strip()
        # Buscar el bloque JSON entre llaves { }
        match = re.search(r'({.*})', raw_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            # Si no hay llaves, intentar limpiar markdown como antes
            clean_text = re.sub(r'```json\s*|\s*```', '', raw_text)
            return json.loads(clean_text)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            st.error("🚨 **Límite de Quota Excedido (Error 429)**")
            st.warning("Esto sucede porque tu cuenta/proyecto gratuito no tiene más peticiones disponibles hoy.")
            st.info("💡 **Solución**: Intenta cambiar al modelo **Gemini 1.5 Flash** en la barra lateral, ya que suele tener cuotas independientes.")
        else:
            st.error(f"Error en {model_id}: {e}")
        return None

# --- 4. LÓGICA QUIRÚRGICA DE GUARDADO ---
def guardar_datos_quirurgico(datos_json, semana):
    try:
        # Forzar recarga del client si hay problema
        sheet = client.open_by_key(SPREADSHEET_ID)
        ws_name = datos_json.get("destino")
        
        if ws_name not in HOJAS_VALIDAS:
            return False, f"Hoja '{ws_name}' no reconocida en la lista de permitidas."
            
        ws = sheet.worksheet(ws_name)
        
        # 1. Encontrar la columna de la semana
        headers = ws.row_values(1)
        col_index = -1
        target_week = re.sub(r'[\s\n\r]', '', semana.upper())
        for i, h in enumerate(headers):
            h_clean = re.sub(r'[\s\n\r]', '', str(h).upper())
            if target_week in h_clean:
                col_index = i + 1
                break
        
        if col_index == -1:
            return False, f"No se encontró la columna '{semana}' en la hoja {ws_name}."

        # 2. Obtener todas las filas de una vez para comparar
        conceptos_hoja = ws.col_values(1)
        conceptos_limpios = [str(c).strip().upper() for c in conceptos_hoja]
        
        import unicodedata
        def normalize_text(text):
            if not text: return ""
            # Eliminar acentos y convertir a mayúsculas
            text = "".join(c for c in unicodedata.normalize('NFD', str(text)) if unicodedata.category(c) != 'Mn')
            # Dejar solo letras y números
            return re.sub(r'[^A-Z0-9]', '', text.upper())

        conceptos_norm = [normalize_text(c) for c in conceptos_hoja]
        
        log_cambios = []
        updates = [] 
        errores_mapeo = []
        
        for item in datos_json['datos']:
            act_raw = str(item['actividad']).strip()
            valor = item['valor']
            
            if " > " in act_raw:
                partes = act_raw.split(" > ")
                act_buscada = partes[-1].strip()
                parent_buscado = partes[-2].strip()
            else:
                act_buscada = act_raw
                parent_buscado = None

            try:
                valor_num = float(str(valor).replace(",", "."))
            except:
                continue
            
            row_index = -1
            act_norm = normalize_text(act_buscada)
            parent_norm = normalize_text(parent_buscado) if parent_buscado else None

            # 1. Intento de búsqueda con contexto de jerarquía
            for idx, c_norm in enumerate(conceptos_norm):
                if act_norm == c_norm or act_norm in c_norm:
                    if parent_norm:
                        # Buscar el padre en las 25 filas anteriores
                        rango_padres = conceptos_norm[max(0, idx-25):idx]
                        if any(parent_norm in p for p in rango_padres):
                            row_index = idx + 1
                            break
                    else:
                        row_index = idx + 1
                        break
            
            # 2. Fallback: Búsqueda difusa si no se encontró
            if row_index == -1:
                for idx, c_norm in enumerate(conceptos_norm):
                    if act_norm in c_norm or c_norm in act_norm:
                        row_index = idx + 1
                        break

            if row_index != -1:
                from gspread.utils import rowcol_to_a1
                range_name = rowcol_to_a1(row_index, col_index)
                updates.append({'range': range_name, 'values': [[valor_num]]})
                log_cambios.append({'ws': ws_name, 'range': range_name, 'act': act_buscada, 'val': valor_num})
            else:
                errores_mapeo.append(act_raw)
        
        if updates:
            ws.batch_update(updates)
            st.session_state['last_update_log'] = log_cambios
            if errores_mapeo:
                st.session_state['mapeo_warnings'] = errores_mapeo
            return True, f"✅ Éxito: {len(updates)} conceptos guardados."
            
        return False, "⚠️ No se encontraron filas que coincidan."
        
    except Exception as e:
        return False, f"❌ Error crítico de conexión: {str(e)}"

def deshacer_actualizacion():
    if 'last_update_log' in st.session_state:
        try:
            sheet = client.open_by_key(SPREADSHEET_ID)
            # Agrupar por hoja para eficiencia
            changes_by_ws = {}
            for change in st.session_state['last_update_log']:
                ws_name = change['ws']
                if ws_name not in changes_by_ws:
                    changes_by_ws[ws_name] = []
                changes_by_ws[ws_name].append({'range': change['range'], 'values': [[""]]})
            
            for ws_name, updates in changes_by_ws.items():
                ws = sheet.worksheet(ws_name)
                ws.batch_update(updates)
                
            del st.session_state['last_update_log']
            return True
        except Exception as e:
            st.error(f"Error al deshacer: {e}")
    return False

# --- 6. GESTIÓN DE CÁMARA Y CHAT (ESTADO) ---
if 'cam_active' not in st.session_state:
    st.session_state.cam_active = False
if 'captured_img' not in st.session_state:
    st.session_state.captured_img = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- 7. CORRECCIONES POR CHAT ---
def aplicar_correccion(user_input, current_data, model_id='gemini-2.0-flash'):
    from skills import CHAT_CORRECTION_SKILL
    model = genai.GenerativeModel(model_id)
    
    prompt = CHAT_CORRECTION_SKILL.format(
        current_data=json.dumps(current_data, indent=2),
        user_input=user_input
    )
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        match = re.search(r'({.*})', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(re.sub(r'```json\s*|\s*```', '', raw_text))
    except Exception as e:
        st.error(f"Error en corrección: {e}")
        return None

# --- 8. INTERFAZ ---
st.set_page_config(page_title="Capibara HMI | SIM", page_icon="🦦", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stSidebar { background-color: #161b22; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/plasticine/100/capybara.png", width=80)
    st.title("Capibara HMI")
    
    # 1. Selector de Modelo (Crisis de Quota fix)
    st.subheader("🤖 Cerebro AI")
    modelo_sel = st.selectbox(
        "Versión de Gemini",
        [
            "gemini-2.0-flash", 
            "gemini-1.5-flash",
            "gemini-3-flash-preview", 
            "gemini-3-pro-preview", 
            "gemini-3-pro-image-preview",
        ],
        help="Si uno da error de quota o 404, intenta con otro. Los modelos 'Gemini 3' son los más recientes."
    )
    
    st.markdown("---")
    st.subheader("💡 Sistema de Origen")
    skill_sel = st.radio(
        "Tipo de Reporte (Skill)",
        list(AI_SKILLS.keys()),
        help="EPI: Reporte individual de paciente. CUADERNOS: Sumatoria de diario de consulta."
    )
    
    # 2. Diagnóstico de API Key
    if "GEMINI_API_KEY" in st.secrets:
        k = st.secrets["GEMINI_API_KEY"]
        masked_key = f"{k[:10]}...{k[-4:]}" if len(k) > 15 else "***"
        st.caption(f"🔑 Key en uso: `{masked_key}`")
    
    # 3. Diagnóstico de Google Sheets
    st.markdown("---")
    st.subheader("📊 Conexión Sheets")
    try:
        if client:
            st.success("✅ Conectado a Google API")
            if SPREADSHEET_ID:
                # Intento rápido de abrir el sheet para verificar permisos
                client.open_by_key(SPREADSHEET_ID)
                st.success("✅ Sheet ID válido y accesible")
            else:
                st.error("❌ Falta SHEET_ID en Secrets")
        else:
            st.error("❌ No hay cliente gspread")
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        st.info("💡 Asegúrate que el correo del robot tenga permiso de EDITOR en tu Excel.")

    st.markdown("---")
    st.subheader("⚙️ Configuración de Carga")
    hoja_manual = st.selectbox(
        "Hoja Destino (Opcional)",
        ["AUTO-DETECTAR"] + HOJAS_VALIDAS,
        help="Si la seleccionas, la IA mapeará los datos EXTACTAMENTE a las filas de esa hoja."
    )
    
    activities_context = []
    selected_ws = None
    if hoja_manual != "AUTO-DETECTAR":
        selected_ws = hoja_manual
        with st.spinner(f"Cargando filas de {selected_ws}..."):
            activities_context = get_worksheet_activities(selected_ws)
            if activities_context:
                st.caption(f"✅ {len(activities_context)} filas cargadas para mapeo.")
            else:
                st.warning("⚠️ No se pudieron cargar las filas.")

    semana_sel = st.selectbox("Semana de Carga", ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"])
    
    if 'last_update_log' in st.session_state:
        if st.button("⏪ DESHACER CARGA"):
            if deshacer_actualizacion():
                st.success("Revertido.")
                st.rerun()

    st.markdown("---")
    with st.expander("🚨 ¿Sigue el error de Quota?"):
        st.write("""
        Si cambiaste de cuenta y sigue el error, es porque creaste la clave en el **mismo proyecto**.
        
        **Pasos para el Reset Real:**
        1. Ve a [Google AI Studio](https://aistudio.google.com/).
        2. Arriba a la izquierda, clic en el nombre del Proyecto -> **Create new project**.
        3. Ponle un nombre nuevo (ej: 'Robot SIM 2').
        4. Clic en **Get API Key** -> Selecciona el nuevo proyecto.
        5. Copia esa clave y pégala en los **Secrets** de Streamlit.
        """)

st.title("🦦 Auditoría Médica | SIM")
st.info(f"Modelo activo: **{modelo_sel}**")

col1, col2 = st.columns([1, 1])

with col1:
    tab1, tab2 = st.tabs(["📂 Subir Archivo", "📸 Cámara"])
    img = None
    
    with tab1:
        f_up = st.file_uploader("Selecciona imagen del reporte", type=['jpg','png','jpeg'])
        if f_up: 
            img = f_up.getvalue()
            st.session_state.captured_img = None # Limpiar captura de cámara si se sube archivo
            
    with tab2:
        if not st.session_state.cam_active:
            if st.button("📷 ACTIVAR CÁMARA", use_container_width=True):
                st.session_state.cam_active = True
                st.rerun()
        else:
            f_cam = st.camera_input("Capturar con cámara")
            if f_cam:
                st.session_state.captured_img = f_cam.getvalue()
                st.session_state.cam_active = False # Apagar cámara tras captura
                st.rerun()
            
            if st.button("🚫 DESACTIVAR CÁMARA", use_container_width=True):
                st.session_state.cam_active = False
                st.rerun()
        
    # Priorizar la imagen capturada si existe, de lo contrario la subida
    if st.session_state.captured_img:
        img = st.session_state.captured_img

if img:
    if st.button("🚀 ANALIZAR REPORTE", type="primary"):
        with st.spinner(f"Escaneando con {modelo_sel}..."):
            res = procesar_imagen(
                img, 
                model_id=modelo_sel, 
                target_ws=selected_ws, 
                known_activities=activities_context,
                skill_name=skill_sel
            )
            if res:
                st.session_state['current_res'] = res
                st.rerun() # Recargar para mostrar tabla persistente

if 'current_res' in st.session_state and img:
    res = st.session_state['current_res']
    st.success(f"📍 Hoja detectada: **{res['destino']}**")
    st.dataframe(pd.DataFrame(res['datos']), use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"📤 GUARDAR EN {res['destino']}", type="primary", use_container_width=True):
            with st.spinner("Guardando..."):
                exito, msj = guardar_datos_quirurgico(res, semana_sel)
                if exito:
                    st.success(msj)
                    if 'mapeo_warnings' in st.session_state:
                        with st.expander("⚠️ Algunos ítems no se encontraron"):
                            for w in st.session_state['mapeo_warnings']:
                                st.write(f"- {w}")
                            st.info("Estos ítems fueron ignorados porque no tienen una fila exacta en el Excel.")
                            del st.session_state['mapeo_warnings']
                    st.balloons()
                    del st.session_state['current_res']
                    st.session_state.captured_img = None # Limpiar tras guardado exitoso
                else:
                    st.error(msj)
                    st.info("💡 Intenta seleccionar la hoja manualmente en la izquierda para cargar las filas exactas.")
    with col_b:
        if st.button("🗑️ BORRAR SELECCIÓN", use_container_width=True):
            if 'current_res' in st.session_state: del st.session_state['current_res']
            if 'mapeo_warnings' in st.session_state: del st.session_state['mapeo_warnings']
            st.session_state.captured_img = None # Limpiar imagen capturada
            st.session_state.chat_history = [] # Limpiar chat
            st.rerun()

# --- PANEL DE CHAT PARA CORRECCIONES ---
if 'current_res' in st.session_state and img:
    st.markdown("---")
    st.subheader("💬 Asistente de Correcciones")
    
    # Contenedor de mensajes
    chat_container = st.container(height=300)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input de chat
    if prompt := st.chat_input("Ej: 'Cambia Femenino a 5' o 'Mueve a la hoja GENERALES'"):
        # Mostrar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Procesar con IA
        with st.spinner("Aplicando cambios..."):
            nuevo_res = aplicar_correccion(prompt, st.session_state['current_res'], model_id=modelo_sel)
            if nuevo_res:
                st.session_state['current_res'] = nuevo_res
                msj_ia = "✅ He aplicado los cambios a la tabla superior."
                st.session_state.chat_history.append({"role": "assistant", "content": msj_ia})
                st.rerun()
            else:
                st.error("No pude procesar esa corrección.")

if 'last_update_log' in st.session_state:
    st.markdown("---")
    if st.button("⏪ DESHACER ÚLTIMA CARGA EN SHEETS", type="secondary", use_container_width=True):
        if deshacer_actualizacion():
            st.success("✅ Datos borrados de la tabla correctamente.")
            st.rerun()
