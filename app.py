import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import time
import re

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
def procesar_imagen(imagen_bytes, model_id='gemini-2.0-flash', target_ws=None, known_activities=None):
    model = genai.GenerativeModel(model_id)
    
    lista_actividades_str = "\n".join([f"- {a}" for a in known_activities[:300]]) if known_activities else "No disponible"
    
    # Inyectamos lógica clínica específica
    system_instruction = f"""
    Eres un auditor médico experto para el Sistema SIM. Extrae datos de reportes físicos y mapéalos a las filas del Excel.

    EQUIVALENCIAS DE PESTAÑA (HOJA):
    - Si el reporte es de PEDIATRÍA, NIÑOS o PEDIAT -> Pestaña 'PNNA'
    - Si el reporte es de ADULTO MAYOR o GERIATRÍA -> Pestaña 'ADULTOS MAYOR'
    - Si el reporte es GENERAL o ADULTO -> Pestaña 'H-PRINCIPAL' o 'GENERALES'
    - Otros: {HOJAS_VALIDAS}

    ESTRUCTURA DE FILAS DISPONIBLES EN {target_ws if target_ws else 'la hoja detectada'}:
    {lista_actividades_str}

    REGLAS CLÍNICAS OBLIGATORIAS:
    1. NUTRICIÓN: Si NO se menciona "obeso", "desnutrido" o "bajo peso", suma +1 a "NORMAL" en el grupo Nutrición.
    2. ENFERMERÍA: Suma +1 a "Consulta por Enfermería" (según edad: Lactante, Escolar, etc.) POR CADA PACIENTE.
    3. AMBIGÜEDAD: Usa el formato 'Grupo > Ítem' (ej: 'Violencia Física > Niño') si el ítem existe en varios grupos.
    4. MULTIPLECIDAD: Un reporte puede marcar celdas en varios grupos (Morbilidad, Nutrición, Enfermería).

    RETORNO JSON:
    {{
      "destino": "NOMBRE_EXACTO_DE_LA_PESTAÑA",
      "datos": [
        {{"actividad": "Nombre Exacto o Jerarquía", "valor": 1}},
        {{"actividad": "Consulta por Enfermería Escolar", "valor": 1}}
      ]
    }}
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
        
        log_cambios = []
        updates = [] # Para batch update
        
        for item in datos_json['datos']:
            act_raw = str(item['actividad']).strip().upper()
            valor = item['valor']
            
            # Si el item tiene jerarquía (A > B), nos quedamos con la parte B para buscar, 
            # pero validamos el contexto.
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
            # Búsqueda con contexto de jerarquía
            for idx, c in enumerate(conceptos_limpios):
                # Coincidencia exacta o parcial del nombre del item
                if act_buscada == c or act_buscada in c:
                    # Si hay un padre, verificamos que el padre esté en las filas anteriores
                    if parent_buscado:
                        # Buscamos el padre en las últimas 15 filas hacia arriba
                        rango_busqueda_padre = conceptos_limpios[max(0, idx-15):idx]
                        if any(parent_buscado in p for p in rango_busqueda_padre):
                            row_index = idx + 1
                            break
                    else:
                        row_index = idx + 1
                        break
            
            if row_index != -1:
                # Usar formato A1 para batch update: Col1=A, Col2=B, etc.
                col_letter = chr(64 + col_index) if col_index <= 26 else "AA" # Simplificado para HMI
                range_name = f"{col_letter}{row_index}"
                updates.append({'range': range_name, 'values': [[valor_num]]})
                
                log_cambios.append({
                    'ws': ws_name, 'range': range_name, 
                    'act': act_buscada, 'val': valor_num
                })
        
        if updates:
            # Ejecutar todos los cambios en un solo llamado para evitar error 429
            ws.batch_update(updates)
            st.session_state['last_update_log'] = log_cambios
            return True, f"✅ Éxito: {len(updates)} conceptos guardados en {ws_name}."
            
        return False, "⚠️ No se encontraron filas que coincidan con el reporte."
        
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

# --- 5. INTERFAZ ---
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
            "gemini-3-flash-preview", 
            "gemini-3-pro-preview", 
            "gemini-3-pro-image-preview",
            "gemini-2.0-flash", 
            "gemini-1.5-flash"
        ],
        help="Si uno da error de quota o 404, intenta con otro. Los modelos 'Gemini 3' son los más recientes."
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
        f = st.file_uploader("Selecciona imagen del reporte", type=['jpg','png','jpeg'])
        if f: img = f.getvalue()
    with tab2:
        f = st.camera_input("Capturar con cámara")
        if f: img = f.getvalue()

if img:
    if st.button("🚀 ANALIZAR REPORTE", type="primary"):
        with st.spinner(f"Escaneando con {modelo_sel}..."):
            res = procesar_imagen(
                img, 
                model_id=modelo_sel, 
                target_ws=selected_ws, 
                known_activities=activities_context
            )
            if res:
                st.session_state['current_res'] = res
                st.success(f"Hoja detectada: {res['destino']}")
                st.dataframe(pd.DataFrame(res['datos']), use_container_width=True)

if 'current_res' in st.session_state and img:
    res = st.session_state['current_res']
    if st.button(f"📤 GUARDAR EN {res['destino']}", type="primary"):
        with st.spinner("Guardando..."):
            exito, msj = guardar_datos_quirurgico(res, semana_sel)
            if exito:
                st.success(msj)
                st.balloons()
                del st.session_state['current_res']
            else:
                st.error(msj)
