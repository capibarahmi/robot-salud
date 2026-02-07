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

# --- 2. LISTA DE HOJAS REALES (Basado en Análisis previo) ---
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

# --- 3. EL CEREBRO IA ---
def procesar_imagen(imagen_bytes, model_id='gemini-2.0-flash'):
    # Selección dinámica de modelo para evitar problemas de cuota
    model = genai.GenerativeModel(model_id)
    
    system_instruction = f"""
    Eres un auditor médico experto. Tu objetivo es mapear reportes físicos hacia una estructura de Excel preexistente.
    
    REGLA DE ORO: NO PUEDES CAMBIAR LA ESTRUCTURA. Debes extraer nombres de actividades que ya existan en el reporte y asignarles un valor NUMÉRICO.

    1. CLASIFICACIÓN: 
       Escoge el nombre de la hoja destino EXACTO de esta lista: {HOJAS_VALIDAS}.
       - Si es pediatría/niños, usa 'PNNA'.
       - Si es adultos mayor, usa 'ADULTOS MAYOR'.
       - Si es general, usa 'GENERALES' o 'H-PRINCIPAL'.
       - Guíate por el título del reporte.

    2. EXTRACCIÓN:
       - Actividad: Nombre de la fila/concepto reportado.
       - Valor: El número total (o suma de días) para esa actividad. SOLO NÚMEROS.

    3. RETORNO: Retorna ÚNICAMENTE un JSON:
    {{
      "destino": "NOMBRE_EXACTO_DE_LA_HOJA",
      "datos": [
        {{"actividad": "Nombre Actividad", "valor": 10}},
        {{"actividad": "Vacunas Aplicadas", "valor": 5}}
      ]
    }}
    """

    try:
        response = model.generate_content([
            system_instruction, 
            {'mime_type': 'image/jpeg', 'data': imagen_bytes}
        ])
        raw_text = response.text.strip()
        raw_text = re.sub(r'```json\s*|\s*```', '', raw_text)
        return json.loads(raw_text)
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
        sheet = client.open_by_key(SPREADSHEET_ID)
        ws_name = datos_json.get("destino")
        if ws_name not in HOJAS_VALIDAS:
            return False, f"Hoja '{ws_name}' no reconocida."
            
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
            return False, f"No se encontró la columna para '{semana}' en {ws_name}."

        # 2. Encontrar las filas
        conceptos_hoja = ws.col_values(1)
        conceptos_limpios = [str(c).strip().upper() for c in conceptos_hoja]
        
        log_cambios = []
        for item in datos_json['datos']:
            act_buscada = str(item['actividad']).strip().upper()
            valor = item['valor']
            
            # Validación numérica
            try:
                valor_num = float(str(valor).replace(",", "."))
            except:
                continue
            
            row_index = -1
            try:
                row_index = conceptos_limpios.index(act_buscada) + 1
            except ValueError:
                # Coincidencia difusa simple
                for idx, c in enumerate(conceptos_limpios):
                    if act_buscada in c or c in act_buscada:
                        row_index = idx + 1
                        break
            
            if row_index != -1:
                ws.update_cell(row_index, col_index, valor_num)
                log_cambios.append({
                    'ws': ws_name, 'row': row_index, 'col': col_index, 
                    'act': act_buscada, 'val': valor_num
                })
        
        if log_cambios:
            st.session_state['last_update_log'] = log_cambios
            return True, f"Se actualizaron {len(log_cambios)} conceptos en {ws_name}."
        return False, "No se encontró ninguna actividad coincidente."
        
    except Exception as e:
        return False, f"Error: {e}"

def deshacer_actualizacion():
    if 'last_update_log' in st.session_state:
        try:
            sheet = client.open_by_key(SPREADSHEET_ID)
            for change in st.session_state['last_update_log']:
                ws = sheet.worksheet(change['ws'])
                ws.update_cell(change['row'], change['col'], "")
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
        ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
        help="Si uno da error de quota, intenta con otro."
    )
    
    # 2. Diagnóstico de API Key
    if "GEMINI_API_KEY" in st.secrets:
        k = st.secrets["GEMINI_API_KEY"]
        masked_key = f"{k[:10]}...{k[-4:]}" if len(k) > 15 else "***"
        st.caption(f"🔑 Key en uso: `{masked_key}`")
    
    st.markdown("---")
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
            res = procesar_imagen(img, model_id=modelo_sel)
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
