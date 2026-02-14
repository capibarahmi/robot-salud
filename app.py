import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import time
import re
import difflib
from skills import AI_SKILLS, TEXTO_DIRECTO_SKILL, IDENTIFICACION_SKILL
from sheet_maps import get_sheet_prompt, ALL_SHEETS, HOJAS_VALIDAS, get_all_sheets_combined_prompt, SHEET_ALIASES
from sync_generales import sync_generales

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

# Configuración inicial de las llaves
if 'api_key_pool' not in st.session_state:
    pool = []
    if "GEMINI_API_KEY" in st.secrets: pool.append(st.secrets["GEMINI_API_KEY"])
    if "GEMINI_API_KEY_2" in st.secrets: pool.append(st.secrets["GEMINI_API_KEY_2"])
    st.session_state['api_key_pool'] = pool
if 'current_key_index' not in st.session_state:
    st.session_state['current_key_index'] = 0

def configure_genai():
    if st.session_state['api_key_pool']:
        idx = st.session_state['current_key_index'] % len(st.session_state['api_key_pool'])
        key = st.session_state['api_key_pool'][idx]
        genai.configure(api_key=key)
        return True
    return False

try:
    configure_genai()
    client = get_gspread_client()
    SPREADSHEET_ID = st.secrets.get("SHEET_ID")
except Exception as e:
    st.error(f"⚠️ Error de configuración inicial: {e}")
    st.stop()

# --- 2. LISTA DE HOJAS Y MAPEO DE DEPARTAMENTOS ---
HOJAS_VALIDAS = [
    "PNNA", "PADULTO 19 A 60 AÐOS", "ADULTOS MAYOR", "PSALUD RESPIRATORIA", 
    "ITS-HIV-SIDA", "SANGRE SEGURA", "PREVENCION CANCER CUELLO UTERIN", 
    "PROMOCIËN DE SALUD", "ENDOCRINO-METABOLICO", "CARDIOVASCULAR", 
    "HEREDOMETABËLICAS", "SALUD BUCAL", "SALUD MENTAL", "SSR", 
    "VISITAS Y ABORDAJES", "SALUD RENAL", "NUTRICIËN", 
    # "PREVEN ACCD Y HECHOS VIOLENTOS" -> Corregido a nombre corto si necesario, pero mantenemos compatibilidad
    "PREVEN ACCD Y HECHOS VIOLENTOS", "DERMATOLOG═A SANITARIA", 
    "MUSCULOESQUELETICAS", "ZOONOSIS"
]

DEPT_SYMBOLS = {
    # PEDIATRÍA / NIÑOS → PNNA
    "PEDIATRIA": "PNNA", "PED": "PNNA", "PEDIAT": "PNNA", "NIÑOS": "PNNA",
    "LACTANTE": "PNNA", "PREESCOLAR": "PNNA", "ESCOLAR": "PNNA", 
    "ADOLESCENTE": "PNNA", "NIÑO": "PNNA", "NIÑA": "PNNA",
    "PRE-ESCOLAR": "PNNA", "INFANTIL": "PNNA", "NEONATO": "PNNA",
    
    # ADULTO MAYOR / GERIATRÍA
    "ADULTO MAYOR": "ADULTOS MAYOR", "GERIATRIA": "ADULTOS MAYOR",
    "GERIATRÍA": "ADULTOS MAYOR", "TERCERA EDAD": "ADULTOS MAYOR",
    "ADULTOS MAYORES": "ADULTOS MAYOR", ">60": "ADULTOS MAYOR",
    
    # TRAUMATOLOGÍA / MUSCULOESQUELÉTICAS
    "TRAUMATOLOGIA": "MUSCULOESQUELETICAS", "TRAUMA": "MUSCULOESQUELETICAS",
    "TRAUMATOLOGÍA": "MUSCULOESQUELETICAS", "ORTOPEDIA": "MUSCULOESQUELETICAS",
    "MUSCULOESQUELETICO": "MUSCULOESQUELETICAS", "ARTRITIS": "MUSCULOESQUELETICAS",
    "REUMATOLOGIA": "MUSCULOESQUELETICAS", "OSTEOPOROSIS": "MUSCULOESQUELETICAS",
    
    # ODONTOLOGÍA / SALUD BUCAL
    "ODONTOLOGIA": "SALUD BUCAL", "ODONTOLOGÍA": "SALUD BUCAL",
    "ESTOMATOLOGIA": "SALUD BUCAL", "DENTAL": "SALUD BUCAL",
    
    # ENDOCRINO / DIABETES
    "ENDOCRINO": "ENDOCRINO-METABOLICO", "DIABETES": "ENDOCRINO-METABOLICO",
    "ENDOCRINOLOGIA": "ENDOCRINO-METABOLICO", "TIROIDES": "ENDOCRINO-METABOLICO",
    "METABOLICO": "ENDOCRINO-METABOLICO",
    
    # RESPIRATORIO
    "RESPIRATORIA": "PSALUD RESPIRATORIA", "ASMA": "PSALUD RESPIRATORIA",
    "NEUMOLOGIA": "PSALUD RESPIRATORIA", "PULMONAR": "PSALUD RESPIRATORIA",
    "EPOC": "PSALUD RESPIRATORIA", "TUBERCULOSIS": "PSALUD RESPIRATORIA",
    
    # GINECOLOGÍA / SSR
    "GINECOLOGIA": "SSR", "GINECOLOGÍA": "SSR", "OBSTETRICIA": "SSR",
    "EMBARAZO": "SSR", "PRENATAL": "SSR", "PLANIFICACION": "SSR",
    "PLANIFICACIÓN FAMILIAR": "SSR", "MATERNO": "SSR",
    
    # CÁNCER
    "CANCER": "PREVENCION CANCER CUELLO UTERIN", "CÁNCER": "PREVENCION CANCER CUELLO UTERIN",
    "CITOLOGIA": "PREVENCION CANCER CUELLO UTERIN", "PAPANICOLAU": "PREVENCION CANCER CUELLO UTERIN",
    
    # CARDIOVASCULAR
    "CARDIOVASCULAR": "CARDIOVASCULAR", "CARDIOLOGIA": "CARDIOVASCULAR",
    "HIPERTENSION": "CARDIOVASCULAR", "CORAZON": "CARDIOVASCULAR",
    
    # SALUD MENTAL
    "PSIQUIATRIA": "SALUD MENTAL", "PSICOLOGIA": "SALUD MENTAL",
    "MENTAL": "SALUD MENTAL", "DEPRESION": "SALUD MENTAL",
    
    # DERMATOLOGÍA
    "DERMATOLOGIA": "DERMATOLOGÍA SANITARIA", "PIEL": "DERMATOLOGÍA SANITARIA",
    
    # ITS / VIH
    "VIH": "ITS-HIV-SIDA", "SIDA": "ITS-HIV-SIDA", "ITS": "ITS-HIV-SIDA",
    
    # NUTRICIÓN
    "NUTRICION": "NUTRICIÓN", "DESNUTRICION": "NUTRICIÓN", "OBESIDAD": "NUTRICIÓN",
    
    # RENAL
    "RENAL": "SALUD RENAL", "NEFROLOGIA": "SALUD RENAL", "RIÑON": "SALUD RENAL",
    
    # ZOONOSIS
    "RABIA": "ZOONOSIS", "MORDEDURA": "ZOONOSIS",

    # EXTRAS (Basado en análisis de historial de chat)
    "CDA": "SSR", "ARO": "SSR", "OBSTETRICIA": "SSR", "EMBARAZADAS": "SSR",
    "NEONATOLOGIA": "PNNA", "CIRUGIA PEDIATRICA": "PNNA", "PUERICULTURA": "PNNA",
    "GASTRO": "MEDICINA INTERNA (si existe) o GENERALES",
    "ENDOCRINOLOGIA": "ENDOCRINO-METABOLICO", "ENDOCRINOLOGÍA": "ENDOCRINO-METABOLICO",
    "ENDOCRINO": "ENDOCRINO-METABOLICO",
}

# Diccionario de correcciones manuales para items específicos que la IA suele fallar
# Clave: (Palabra clave de Sección, Palabra clave del Item) -> Valor exacto en Excel
CORRECCIONES_MAPEO = {
    # ============== LACTANTES Y PREESCOLARES ==============
    # SEXO
    ("LACTANTE", "MASCULINO"): "Masculino Lactantes y Pre-escolares",
    ("LACTANTE", "FEMENINO"): "Femenino Lactantes y Pre-escolares",
    ("PREESCOLAR", "MASCULINO"): "Masculino Lactantes y Pre-escolares",
    ("PREESCOLAR", "FEMENINO"): "Femenino Lactantes y Pre-escolares",
    
    # CONSULTAS LACTANTE (< 23 meses)
    ("LACTANTE", "1MES"): "A. 1rea Consulta < de 1 mes",
    ("LACTANTE", "< 1 MES"): "A. 1rea Consulta < de 1 mes",
    ("LACTANTE", "1-11"): "B. 1era. Consulta de 1 a 11 meses",
    ("LACTANTE", "12-23"): "C. 1era. Consulta de 12 a 23 meses",
    ("LACTANTE", "SUCESIVA"): "D. Consulta Sucesivas <  23 Meses",
    
    # CONSULTAS PREESCOLAR (2-6 años)
    ("PREESCOLAR", "2-3"): "A. 1era. Consulta de 2 a 3 años",
    ("PREESCOLAR", "2A3"): "A. 1era. Consulta de 2 a 3 años",
    ("PREESCOLAR", "4-6"): "B. 1era. Consulta de 4 a 6 años",
    ("PREESCOLAR", "4A6"): "B. 1era. Consulta de 4 a 6 años",
    ("PREESCOLAR", "SUCESIVA"): "D. Consultas Sucesivas de 2 a 6 años",
    
    # DIAGNÓSTICO LACTANTE/PREESCOLAR
    ("LACTANTE", "SANO"): "Lactantes Sanos",
    ("LACTANTE", "ENFERMO"): "Lactantes Enfermos",
    ("PREESCOLAR", "SANO"): "Pre-escolares Sanos",
    ("PREESCOLAR", "ENFERMO"): "Pre-escolares Enfermos",
    
    # PATOLOGÍAS LACTANTE/PREESCOLAR
    ("LACTANTE", "HEMAPOYETICA"): "Enf. de la Sangre y Org. Hematopoyético",
    ("LACTANTE", "HEMAPOYETICAS"): "Enf. de la Sangre y Org. Hematopoyético",
    ("LACTANTE", "ENDOCRINO"): "Enf. Endocrina, Nutricional y Metabólica",
    ("LACTANTE", "MENTAL"): "Enf. Trastorno Mental y Comportamiento",
    ("LACTANTE", "NERVIOSO"): "Enf. del Sistema Nervioso",
    ("LACTANTE", "OJO"): "Enf. del Ojo y sus Anexos",
    ("LACTANTE", "OIDO"): "Enf. del Oído y Apófisis Mastoides",
    ("LACTANTE", "CIRCULATORIO"): "Enf. del Sistema Circulatorio",
    ("LACTANTE", "RESPIRATORIO"): "Enf. del Sistema Respiratorio",
    ("LACTANTE", "DIGESTIVO"): "Enf. del Sistema Digestivo",
    ("LACTANTE", "PIEL"): "Enf. de la Piel y Tej. Conjuntivo",
    ("LACTANTE", "GENITOURINARIO"): "Enf. Genital y Urinaria",
    ("LACTANTE", "GENITURINARIO"): "Enf. Genital y Urinaria",
    
    # ============== ESCOLARES ==============
    # SEXO ESCOLAR
    ("ESCOLAR", "MASCULINO"): "Masculino Escolar",
    ("ESCOLAR", "FEMENINO"): "Femenino Escolar",
    
    # CONSULTAS ESCOLARES POR GRADO
    ("ESCOLAR", "SUCESIVA"): "D.- Consultas Sucesivas y Otros Grados",
    ("ESCOLAR", "PRIMERA"): "A.- 1era. Consulta 1er Grado", 
    ("ESCOLAR", "1ER GRADO"): "A.- 1era. Consulta 1er Grado",
    ("ESCOLAR", "1ER"): "A.- 1era. Consulta 1er Grado",
    ("ESCOLAR", "3ER GRADO"): "B.- 1era. Consulta 3er Grado",
    ("ESCOLAR", "3ER"): "B.- 1era. Consulta 3er Grado",
    ("ESCOLAR", "6TO GRADO"): "C.- 1era. Consulta 6to Grado",
    ("ESCOLAR", "6TO"): "C.- 1era. Consulta 6to Grado",
    
    # DIAGNÓSTICO ESCOLAR
    ("ESCOLAR", "SANO"): "Escolares Sanos",
    ("ESCOLAR", "ENFERMO"): "Escolares Enfermos",
    ("ESCOLAR", "ESCOLARES SANOS"): "Escolares Sanos",
    ("ESCOLAR", "ESCOLARES ENFERMOS"): "Escolares Enfermos",
    
    # PATOLOGÍAS ESCOLARES
    ("ESCOLAR", "HEMAPOYETICA"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ESCOLAR", "HEMAPOYETICAS"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ESCOLAR", "ENDOCRINO"): "Enf. Endocrina, Nutricional y Metabólica",
    ("ESCOLAR", "MENTAL"): "Enf. Trastorno Mental y Compotamiento",
    ("ESCOLAR", "NERVIOSO"): "Enf. del Sistema Nervioso",
    ("ESCOLAR", "OJO"): "Enf. del Ojo y Sus Anexos",
    ("ESCOLAR", "OIDO"): "Enf. del Oído y Apófisis Mastoides",
    ("ESCOLAR", "CIRCULATORIO"): "Enf. del Sistema Circulatorio",
    ("ESCOLAR", "RESPIRATORIO"): "Enf. Sistema Respiratorio",
    ("ESCOLAR", "DIGESTIVO"): "Enf. del Sistema Digestivo",
    ("ESCOLAR", "PIEL"): "Enf. de la Piel y Tej. Conjuntivo",
    ("ESCOLAR", "GENITOURINARIO"): "Enf. Genital y Urinaría",
    ("ESCOLAR", "GENITURINARIO"): "Enf. Genital y Urinaría",
    
    # ============== ADOLESCENTES (12-19 años) ==============
    # SEXO
    ("ADOLESCENTE", "MASCULINO"): "Total Masculino Adolescentes",
    ("ADOLESCENTE", "FEMENINO"): "Total Femenino Adolescentes",
    
    # CONSULTAS
    ("ADOLESCENTE", "PRIMERA"): "A. Primera Consulta Adolescentes",
    ("ADOLESCENTE", "SUCESIVA"): "D. Consulta Sucesiva Adolescentes",
    
    # DIAGNÓSTICO
    ("ADOLESCENTE", "SANO"): "Adolescentes Sano",
    ("ADOLESCENTE", "ENFERMO"): "Adolescentes Enfermo",
    
    # PATOLOGÍAS (mismas filas que otros grupos pero en sección Adolescentes)
    ("ADOLESCENTE", "HEMAPOYETICA"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ADOLESCENTE", "HEMAPOYETICAS"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ADOLESCENTE", "ENDOCRINO"): "Enf. Endocrina, Nutricional y Metabólica",
    ("ADOLESCENTE", "MENTAL"): "Enf. Trastorno Mental y Comportamiento",
    ("ADOLESCENTE", "NERVIOSO"): "Enf. del Sistema Nervioso",
    ("ADOLESCENTE", "OJO"): "Enf. del Ojo y sus Anexos",
    ("ADOLESCENTE", "OIDO"): "Enf. del Oído y Apófisis Mastoides",
    ("ADOLESCENTE", "CIRCULATORIO"): "Enf. del Sistema Circulatorio",
    ("ADOLESCENTE", "RESPIRATORIO"): "Enf. del Sistema Respiratorio",
    ("ADOLESCENTE", "DIGESTIVO"): "Enf. del Sistema Digestivo",
    ("ADOLESCENTE", "PIEL"): "Enf. de la Piel y Tej. Conjuntivo",
    ("ADOLESCENTE", "GENITOURINARIO"): "Enf. Genital y Urinaria",
    ("ADOLESCENTE", "GENITURINARIO"): "Enf. Genital y Urinaria",
    
    # ============== ADULTO MAYOR (60+ años) - HOJA: ADULTOS MAYOR ==============
    # SEXO
    ("ADULTO", "MASCULINO"): "Masculino",
    ("ADULTO", "FEMENINO"): "Femenino",
    ("3RA EDAD", "MASCULINO"): "Masculino",
    ("3RA EDAD", "FEMENINO"): "Femenino",
    ("60", "MASCULINO"): "Masculino",
    ("60", "FEMENINO"): "Femenino",
    
    # CONSULTAS
    ("ADULTO", "PRIMERA"): "Primera Consulta",
    ("ADULTO", "SUCESIVA"): "Consulta Sucesiva",
    ("3RA EDAD", "PRIMERA"): "Primera Consulta",
    ("3RA EDAD", "SUCESIVA"): "Consulta Sucesiva",
    
    # DIAGNÓSTICO
    ("ADULTO", "SANO"): "Adulto Sano",
    ("ADULTO", "ENFERMO"): "Adulto Enfermo",
    ("3RA EDAD", "SANO"): "Adulto Sano",
    ("3RA EDAD", "ENFERMO"): "Adulto Enfermo",
    
    # PATOLOGÍAS (para hojas sin grupo etario, usar fuzzy matching normal)
    ("ADULTO", "HEMAPOYETICA"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ADULTO", "HEMAPOYETICAS"): "Enf. de la Sangre y Org. Hematopoyético",
    ("ADULTO", "ENDOCRINO"): "Enf. Endocrina, Nutricional y Metabólica",
    ("ADULTO", "MENTAL"): "Enf. Trastorno Mental y Comportamiento",
    ("ADULTO", "NERVIOSO"): "Enf. del Sistema Nervioso",
    ("ADULTO", "OJO"): "Enf. del Ojo y sus Anexos",
    ("ADULTO", "OIDO"): "Enf. del Oído y Apófisis Mastoides",
    ("ADULTO", "CIRCULATORIO"): "Enf. del Sistema Circulatorio",
    ("ADULTO", "RESPIRATORIO"): "Enf. del Sistema Respiratorio",
    ("ADULTO", "DIGESTIVO"): "Enf. del Sistema Digestivo",
    ("ADULTO", "PIEL"): "Enf. de la Piel y Tej. Conjuntivo",
    ("ADULTO", "GENITOURINARIO"): "Enf. Genital y Urinaria",
    ("ADULTO", "GENITURINARIO"): "Enf. Genital y Urinaria",
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
        current_section = "" # Nivel 1: Programa/Atención principal
        current_group = ""   # Nivel 2: Sub-bloque (Riesgo, Diagnóstico, etc.)
        
        # Palabras que suelen definir una SECCIÓN PRINCIPAL
        KEYWORDS_SECCION = ["atención al", "programa de", "atención en", "atención integral", "atención médica", "actividad /establecimiento"]
        # Palabras que suelen definir un SUB-GRUPO
        KEYWORDS_GRUPO = ["riesgo", "estado nutricional", "diagnóstico", "nivel educativo", "patología", "clasificación"]
        # Items que SIEMPRE son hojas (leafs)
        items_leafs = ["MASCULINO", "FEMENINO", "NIÑO", "NIÑA", "TOTAL", "SÍ", "NO", "S/D"]

        for name in rows:
            name_clean = name.strip()
            if not name_clean: continue
            
            # Limpiar nombre para comparación
            norm_name = name_clean.lower()
            
            # Lógica de niveles
            es_seccion = any(k in norm_name for k in KEYWORDS_SECCION)
            es_grupo = any(k in norm_name for k in KEYWORDS_GRUPO)
            es_leaf = any(l in name_clean.upper() for l in items_leafs) or (len(name_clean) < 15 and ":" not in name_clean)

            if es_seccion:
                current_section = name_clean
                current_group = ""
                hierarchy_list.append(name_clean)
            elif es_grupo:
                current_group = name_clean
                if current_section:
                    hierarchy_list.append(f"{current_section} > {name_clean}")
                else:
                    hierarchy_list.append(name_clean)
            else:
                # Es un ítem final o sub-patología
                if current_section and current_group:
                    hierarchy_list.append(f"{current_section} > {current_group} > {name_clean}")
                elif current_section:
                    hierarchy_list.append(f"{current_section} > {name_clean}")
                else:
                    hierarchy_list.append(name_clean)
                
        return hierarchy_list
    except Exception as e:
        print(f"Error cargando actividades de {ws_name}: {e}")
        return []

# --- 3. EL CEREBRO IA ---
def procesar_imagen(imagen_bytes, model_id='gemini-2.0-flash', target_ws=None, known_activities=None, skill_name="EPI (Individual)", user_context=""):
    model = genai.GenerativeModel(model_id)
    
    lista_actividades_str = "\n".join([f"- {a}" for a in known_activities[:800]]) if known_activities else "No disponible"
    
    # Seleccionar la instrucción según el skill
    base_instruction = AI_SKILLS.get(skill_name, AI_SKILLS["EPI (Individual)"])
    # Inyectar filas dinámicas de la hoja destino
    sheet_rows_prompt = get_sheet_prompt(target_ws) if target_ws else ""
    base_instruction = base_instruction.replace("{SHEET_ROWS}", sheet_rows_prompt)
    
    # Incluir instrucciones del usuario si existen
    user_instructions_block = ""
    if user_context:
        user_instructions_block = f"""
    
    ⚠️ INSTRUCCIONES ESPECÍFICAS DEL USUARIO (PRIORIDAD ALTA):
    {user_context}
    """
    
    # Bloque de hoja obligatoria si el usuario la seleccionó
    sheet_enforcement = ""
    if target_ws:
        sheet_enforcement = f"""
    
    🔒 HOJA ASIGNADA POR EL USUARIO: "{target_ws}"
    ⚠️ OBLIGATORIO: Debes usar EXACTAMENTE esta hoja como "destino".
    NO auto-detectes otra hoja. El usuario ya eligió "{target_ws}".
    Si ves datos de otro departamento en la imagen, IGNÓRALOS.
    SOLO extrae datos que correspondan a "{target_ws}".
    """
    else:
        sheet_enforcement = """
    
    🔍 MODO AUTO-DETECTAR: El usuario NO seleccionó hoja.
    Detecta el departamento de la imagen y elige la hoja correcta.
    """
    
    system_instruction = f"""
    {base_instruction}
    {sheet_enforcement}
    {user_instructions_block}
    
    HOJAS TÉCNICAS VÁLIDAS EN GOOGLE SHEETS (Usa una de estas para 'destino'):
    {", ".join(HOJAS_VALIDAS)}
    
    ESTRUCTURA DE FILAS DISPONIBLES EN {target_ws if target_ws else 'la hoja detectada'}:
    {lista_actividades_str}
    
    CONTEXTO ACTUAL:
    - Hoja Asignada: {target_ws if target_ws else 'Auto-detectar'}

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
        if "429" in error_msg and len(st.session_state['api_key_pool']) > 1:
            st.warning("🔄 **Límite de cuota alcanzado. Rotando API Key automáticamente...**")
            st.session_state['current_key_index'] += 1
            configure_genai()
            # Reintentar una vez con la nueva llave
            return procesar_imagen(imagen_bytes, model_id, target_ws, known_activities, skill_name)
        
        if "429" in error_msg:
            st.error("🚨 **Límite de Quota Excedido (Error 429)**")
            st.warning("Esto significa que has usado todas las peticiones gratuitas permitidas para este modelo por ahora (suele ser un límite diario o de mensajes por minuto).")
            st.info("💡 **Solución**: Agrega una API Key adicional en la barra lateral o cambia el modelo.")
        else:
            st.error(f"Error en {model_id}: {e}")
        return None

# --- 3.B EL CEREBRO IA (TEXTO DIRECTO) ---
def procesar_texto(texto_usuario, model_id='gemini-2.0-flash', target_ws=None, known_activities=None, skill_name="TEXTO DIRECTO (Chat)", conversation_history=None):
    """Procesa texto pegado por el usuario usando un motor de DOS PASOS para máxima precisión."""
    model = genai.GenerativeModel(model_id)
    all_final_results = []
    
    # --- PASO 1: IDENTIFICACIÓN DE HOJAS ---
    detected_sheets = []
    if not target_ws:
        st.info("🔍 Paso 1/2: Identificando departamentos médicos...")
        id_instruction = IDENTIFICACION_SKILL.replace("{HOJAS_VALIDAS}", "\n".join([f"- {h}" for h in HOJAS_VALIDAS]))
        id_messages = [id_instruction, f"TEXTO A ANALIZAR:\n{texto_usuario}"]
        
        try:
            id_response = model.generate_content(id_messages)
            raw_id = id_response.text.strip()
            # Buscar lista JSON
            match = re.search(r'(\[.*\])', raw_id, re.DOTALL)
            if match:
                # FILTRO MEJORADO: Buscar coincidencias parciales o exactas
                detected_sheets = []
                # Normalizar lista de IA
                ia_sheets = [str(s).upper().strip() for s in json.loads(match.group(1).replace("'", '"'))]
                
                # 1. Búsqueda exacta
                for hoja in HOJAS_VALIDAS:
                    if hoja in ia_sheets:
                        detected_sheets.append(hoja)
                
                # 2. Búsqueda parcial (Si IA devuelve "HOJA PNNA" o "PNNA - SKILL")
                if not detected_sheets:
                    for s_ia in ia_sheets:
                        for hoja in HOJAS_VALIDAS:
                            if hoja in s_ia: # Ej: "PNNA" in "HOJA PNNA"
                                if hoja not in detected_sheets: detected_sheets.append(hoja)
            else:
                # Fallback manual estricto pero robusto
                norm_text = raw_id.upper()
                detected_sheets = [h for h in HOJAS_VALIDAS if h in norm_text]
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and len(st.session_state['api_key_pool']) > 1:
                st.warning("🔄 **Límite en Paso 1. Rotando API Key...**")
                st.session_state['current_key_index'] += 1
                configure_genai()
                return procesar_texto(texto_usuario, model_id, target_ws, known_activities, skill_name, conversation_history)
            
            st.error(f"Error en Paso 1 (Identificación): {e}")
            # Fallback al modo antiguo si falla la identificación
            detected_sheets = []
    else:
        detected_sheets = [target_ws]

    if not detected_sheets:
        st.warning("⚠️ No se detectaron departamentos específicos. Reintentando con visión global...")
        detected_sheets = [None] # Forzar un intento global

    # --- PASO 2: EXTRACCIÓN ENFOCADA (POR CADA HOJA) ---
    total_steps = len(detected_sheets)
    parsed_results_count = 0 
    
    # 0. MODO SEGURO (Check user preference)
    safe_mode = st.session_state.get('safe_mode_active', False)
    delay_time = 8 if safe_mode else 4 # Mucho más conservador (4s normal, 8s seguro)

    st.write(f"ℹ️ Procesando con delay de {delay_time}s entre hojas para estabilidad...")

    for i, current_sheet in enumerate(detected_sheets):
        # 1. RATE LIMITING RIGUROSO
        if i > 0: 
            time.sleep(delay_time)
        
        # 2. ROTACIÓN PROACTIVA (Más frecuente si hay pool)
        if len(st.session_state['api_key_pool']) > 1 and parsed_results_count > 0 and parsed_results_count % 2 == 0:
            st.toast("🔄 Rotando llave API...", icon="🛡️")
            st.session_state['current_key_index'] += 1
            configure_genai()
            
        parsed_results_count += 1
        if current_sheet:
            st.info(f"📊 Paso 2/2: Extrayendo datos técnicos para **{current_sheet}** ({i+1}/{total_steps})...")
        else:
            st.info("📊 Paso 2/2: Extrayendo datos (Modo Global)...")
            
        # Preparar prompt enfocado
        base_instruction = TEXTO_DIRECTO_SKILL
        if current_sheet:
            sheet_rows_prompt = get_sheet_prompt(current_sheet)
            sheet_enforcement = f"\n🔒 ENFOQUE EXCLUSIVO: Estás extrayendo datos ÚNICAMENTE para la hoja '{current_sheet}'."
        else:
            sheet_rows_prompt = get_all_sheets_combined_prompt()
            sheet_enforcement = ""

        # Inyectar filas
        instruction = base_instruction.replace("{SHEET_ROWS}", sheet_rows_prompt)
        
        system_instruction = f"""
        {instruction}
        {sheet_enforcement}
        
        CONTEXTO ACTUAL:
        - Hoja Objetivo: {current_sheet if current_sheet else 'Auto-detectar'}
        - Sistema: {skill_name}
        """
        
        # Construir mensajes
        messages = [system_instruction]
        if conversation_history:
            history_text = "\n\nHISTORIAL DE CONVERSACIÓN PREVIO:\n"
            for msg in conversation_history:
                role = "USUARIO" if msg['role'] == 'user' else "ASISTENTE"
                history_text += f"{role}: {msg['content']}\n"
            messages[0] += history_text
        
        messages.append(f"\n\nDATOS DEL USUARIO:\n{texto_usuario}")
        
        try:
            response = model.generate_content(messages)
            raw_text = response.text.strip()
            
            # Parsing JSON
            match_list = re.search(r'(\[.*\])', raw_text, re.DOTALL)
            match_obj = re.search(r'({.*})', raw_text, re.DOTALL)
            
            parsed_data = None
            if match_list:
                parsed_data = json.loads(match_list.group(1))
            elif match_obj:
                parsed_data = json.loads(match_obj.group(1))
            else:
                clean_text = re.sub(r'```json\s*|\s*```', '', raw_text)
                parsed_data = json.loads(clean_text)
            
            if isinstance(parsed_data, list):
                all_final_results.extend(parsed_data)
            else:
                all_final_results.append(parsed_data)
                
            # Pequeña pausa para evitar rate limit si hay muchas hojas
            if total_steps > 1:
                time.sleep(2) # Aumentar a 2 segundos por precaución
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and len(st.session_state['api_key_pool']) > 1:
                st.warning(f"🔄 **Límite en {current_sheet}. Rotando y reintentando...**")
                st.session_state['current_key_index'] += 1
                configure_genai()
                # Reintentar SOLO esta hoja llamando de nuevo al modelo (recursividad local no es ideal, pero funciona)
                model = genai.GenerativeModel(model_id) # Refrescar modelo con nueva key
                # Re-ejecutar este paso del bucle (una vez)
                try:
                    response = model.generate_content(messages)
                    # (repetir lógica de parseo simplificada)
                    raw_text = response.text.strip()
                    parsed_data = json.loads(re.search(r'({.*}|\[.*\])', raw_text, re.DOTALL).group(1))
                    if isinstance(parsed_data, list): all_final_results.extend(parsed_data)
                    else: all_final_results.append(parsed_data)
                    if isinstance(parsed_data, list): all_final_results.extend(parsed_data)
                    else: all_final_results.append(parsed_data)
                except Exception as e:
                    # Si falla, intentar una vez más con delay MUY largo (Backoff)
                    err_str = str(e)
                    if "429" in err_str or "quota" in err_str.lower():
                        wait_time = 25 # 25 segundos reales
                        st.warning(f"⚠️ Cuota Google excedida en {current_sheet}. Pausando {wait_time}s y rotando llave...")
                        time.sleep(wait_time)
                        
                        # Rotar llave si es posible
                        if len(st.session_state['api_key_pool']) > 1:
                            st.session_state['current_key_index'] += 1
                            configure_genai()
                        
                        try:
                             # Reintento único
                             response = model.generate_content(messages)
                             raw_text = response.text.strip()
                             parsed_data = json.loads(re.search(r'({.*}|\[.*\])', raw_text, re.DOTALL).group(1))
                             if isinstance(parsed_data, list): all_final_results.extend(parsed_data)
                             else: all_final_results.append(parsed_data)
                        except Exception as e2:
                             st.error(f"❌ Falla definitiva en {current_sheet}: {e2}")
                    else:
                        st.error(f"Falla crítica en {current_sheet}: {e}")
            else:
                st.error(f"Error extrayendo {current_sheet}: {e}")
            continue

    return all_final_results

# --- 4. LÓGICA QUIRÚRGICA DE GUARDADO ---
def guardar_datos_quirurgico(datos_json, semana, overwrite=False):
    try:
        # Forzar recarga del client si hay problema
        sheet = client.open_by_key(SPREADSHEET_ID)
        ws_name = datos_json.get("destino")
        
        # Normalización de destino (Uso de SHEET_ALIASES de sheet_maps)
        if ws_name:
            ws_name_norm = str(ws_name).upper().strip()
            if ws_name_norm in SHEET_ALIASES:
                ws_name = SHEET_ALIASES[ws_name_norm]
        
        if ws_name not in HOJAS_VALIDAS:
            # Fallback por keywords si no está en alias ni es exacto
            norm_target = str(ws_name).upper()
            if any(k in norm_target for k in ["ESCOLAR", "NIÑ", "LACTANTE", "ADOLESCENTE", "PEDIAT"]):
                ws_name = "PNNA"
            elif any(k in norm_target for k in ["GERIATRIA", "MAYOR"]):
                ws_name = "ADULTOS MAYOR"
            elif any(k in norm_target for k in ["MUJER", "SSR", "PLANIFICACION", "EMBARAZA"]):
                ws_name = "SSR"
        
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

        # 2. Reconstruir jerarquía de la hoja para match exacto
        conceptos_hoja = ws.col_values(1)
        
        # Usamos la misma lógica de get_worksheet_activities para reconstruir rutas finales
        rutas_excel = []
        c_sec = ""
        c_grp = ""
        # Palabras que definen una SECCIÓN o ENCABEZADO (Debe ser muy específico)
        KEYWORDS_SECCION = ["atención al", "programa de", "atención en", "atención integral", "atención médica", "actividad /establecimiento"]
        # Palabras que definen un SUB-GRUPO
        KEYWORDS_GRUPO = ["riesgo", "estado nutricional", "diagnóstico", "nivel educativo", "patología", "clasificación"]
        # Items que NO son encabezados aunque tengan palabras clave (Exclusiones)
        EXCLUDE_HEADER = ["MASCULINO", "FEMENINO", "SANO", "ENFERMO", "NORMAL", "DÉFICIT", "ZONA CRÍTICA", "LEVE", "MODERADA", "GRAVE"]

        for idx, val in enumerate(conceptos_hoja):
            val_clean = str(val).strip()
            if not val_clean: 
                rutas_excel.append("")
                continue
            
            norm = val_clean.lower()
            es_seccion = any(k in norm for k in KEYWORDS_SECCION)
            es_grupo = any(k in norm for k in KEYWORDS_GRUPO)
            
            if es_seccion:
                c_sec = val_clean
                c_grp = ""
                rutas_excel.append(val_clean)
            elif es_grupo:
                c_grp = val_clean
                ruta = f"{c_sec} > {val_clean}" if c_sec else val_clean
                rutas_excel.append(ruta)
            else:
                # Es un ítem final
                if c_sec and c_grp:
                    rutas_excel.append(f"{c_sec} > {c_grp} > {val_clean}")
                elif c_sec:
                    rutas_excel.append(f"{c_sec} > {val_clean}")
                else:
                    rutas_excel.append(val_clean)

        import unicodedata
        def normalize_path(text):
            if not text: return ""
            # Eliminar acentos, espacios extras y > para comparar rutas
            text = "".join(c for c in unicodedata.normalize('NFD', str(text)) if unicodedata.category(c) != 'Mn')
            return re.sub(r'[^A-Z0-9]', '', text.upper())

        rutas_norm = [normalize_path(r) for r in rutas_excel]
        
        log_cambios = []
        updates = [] 
        errores_mapeo = []
        
        for item in datos_json['datos']:
            act_raw = str(item['actividad']).strip()
            valor = item['valor']
            
            # Desglosar jerarquía completa
            partes = [p.strip() for p in act_raw.split(" > ")]
            act_buscada = partes[-1]
            ancestros_buscados = [normalize_path(p) for p in partes[:-1]]
            
            try:
                valor_num = float(str(valor).replace(",", "."))
                # Skip NaN and Infinity values (not JSON compliant)
                import math
                if math.isnan(valor_num) or math.isinf(valor_num):
                    continue
            except:
                continue
            
            row_index = -1
            act_path_norm = normalize_path(act_raw)
            
            # 0. PRE-CHECK: Correcciones Manuales (Diccionario)
            # Buscamos si hay alguna regla específica para esta combinación Sección-Item
            # IMPORTANTE: Buscar k_sec en TODO el path, no solo partes[0]
            act_path_upper = act_raw.upper()
            item_norm = normalize_path(partes[-1])
            
            for (k_sec, k_item), v_exact in CORRECCIONES_MAPEO.items():
                # Buscar k_sec en CUALQUIER parte del path (para detectar ESCOLAR, LACTANTE, etc.)
                # Y buscar k_item en el último segmento (el item específico)
                if k_sec in act_path_upper and k_item in item_norm:
                    # Buscar el índice de este valor exacto en rutas_excel
                    for idx_r, r_real in enumerate(rutas_excel):
                         if r_real.endswith(v_exact):
                             row_index = idx_r + 1
                             break
                    if row_index != -1: break

            # 1. Búsqueda por RUTA COMPLETA EXACTA (Blindaje contra grupos de edad)
            for idx, r_norm in enumerate(rutas_norm):
                if act_path_norm == r_norm:
                    row_index = idx + 1
                    break
            
            # 2. Fallback Intelligence: Fuzzy Match con Difflib (Para typos como "Hemapoyeticas")
            if row_index == -1:
                # Buscamos la ruta más parecida en todo el listado de rutas normalizadas
                matches = difflib.get_close_matches(act_path_norm, rutas_norm, n=1, cutoff=0.85)
                if matches:
                    best_match = matches[0]
                    row_index = rutas_norm.index(best_match) + 1
            
            # 3. Fallback: Búsqueda difusa del ítem final pero PROTEGIDA por sección (Contención)
            if row_index == -1:
                item_norm = normalize_path(partes[-1])
                seccion_norm = normalize_path(partes[0]) if partes else ""
                
                for idx, r_norm in enumerate(rutas_norm):
                    # Solo consideramos el fallback si la sección coincide (si se proveyó una)
                    if seccion_norm:
                        if item_norm in r_norm and seccion_norm in r_norm:
                            row_index = idx + 1
                            break
                    elif item_norm in r_norm: # Fallback general si no hay sección
                        row_index = idx + 1
                        break

            # 4. Fallback DIRECTO: Para hojas planas (MUSCULOESQUELETICAS, etc.)
            #    Buscar el último segmento directamente en los nombres de filas
            if row_index == -1:
                ultimo_item = partes[-1].strip()
                ultimo_item_norm = normalize_path(ultimo_item)
                
                # Buscar coincidencia EXACTA del último item con el nombre de fila
                for idx, concepto in enumerate(conceptos_hoja):
                    if normalize_path(concepto.strip()) == ultimo_item_norm:
                        row_index = idx + 1
                        break
                
                # Si no hay exacta, buscar fuzzy solo en el último item
                if row_index == -1:
                    matches = difflib.get_close_matches(
                        ultimo_item_norm, 
                        [normalize_path(c.strip()) for c in conceptos_hoja], 
                        n=1, cutoff=0.80
                    )
                    if matches:
                        for idx, concepto in enumerate(conceptos_hoja):
                            if normalize_path(concepto.strip()) == matches[0]:
                                row_index = idx + 1
                                break

            if row_index != -1:
                # --- NUEVA PROTECCIÓN: NO ESCRIBIR EN ENCABEZADOS DE SECCIÓN ---
                # Si la fila encontrada es un encabezado, intentamos redirigir al TOTAL
                nombre_fila_encontrada = conceptos_hoja[row_index - 1].strip()
                norm_fila = nombre_fila_encontrada.lower()
                
                # Criterio: Es header si tiene keyword de sección/grupo Y NO TIENE exclusiones de datos
                es_header_seccion = (any(k in norm_fila for k in KEYWORDS_SECCION) or any(k in norm_fila for k in KEYWORDS_GRUPO)) \
                                    and not any(e in nombre_fila_encontrada.upper() for e in EXCLUDE_HEADER) \
                                    and "total" not in norm_fila
                
                if es_header_seccion:
                    # Buscar un "Total" o "Masculino/Femenino" inmediatamente debajo o relacionado
                    print(f"⚠️ Redirigiendo desde encabezado '{nombre_fila_encontrada}'...")
                    
                    # Búsqueda local de un "Total" dentro del mismo bloque (próximas 8 filas)
                    nuevo_index = -1
                    for offset in range(1, 10):
                        if row_index + offset > len(conceptos_hoja): break
                        val_next = conceptos_hoja[row_index + offset - 1].strip().lower()
                        if "total" in val_next:
                            nuevo_index = row_index + offset
                            break
                    
                    if nuevo_index != -1:
                        row_index = nuevo_index
                    else:
                        errores_mapeo.append(f"{act_raw} (Es un encabezado y no hallé 'Total')")
                        continue
                # ---------------------------------------------------------------
            
                from gspread.utils import rowcol_to_a1
                
                # OPTIMIZACIÓN: Leer valores de la columna completa una sola vez si no se ha hecho
                if 'current_col_values' not in locals():
                    current_col_values = ws.col_values(col_index)
                
                # Obtener valor existente del array local (más rápido que ws.cell)
                existing_val = ""
                if row_index <= len(current_col_values):
                    existing_val = current_col_values[row_index - 1]
                
                try:
                    if existing_val and str(existing_val).strip() and not overwrite:
                        # Convertir a número y sumar (SOLO SI NO ES OVERWRITE)
                        existing_num = float(str(existing_val).replace(",", "."))
                        total_val = existing_num + valor_num
                    else:
                        # Modo Sobrescritura o celda vacía: Usar el valor nuevo directamente
                        total_val = valor_num
                except:
                    total_val = valor_num
                
                # Actualizar el array local para que si otro ítem cae en la misma fila, se sume correctamente
                if row_index <= len(current_col_values):
                    current_col_values[row_index - 1] = str(total_val)
                else:
                    # Si la fila es nueva, extender el array
                    while len(current_col_values) < row_index:
                        current_col_values.append("")
                    current_col_values[row_index - 1] = str(total_val)

                range_name = rowcol_to_a1(row_index, col_index)
                updates.append({'range': range_name, 'values': [[total_val]]})
                log_cambios.append({'ws': ws_name, 'range': range_name, 'act': act_buscada, 'val_orig': valor_num, 'val_total': total_val})
            else:
                errores_mapeo.append(act_raw)
        
        if updates:
            ws.batch_update(updates)
            # st.session_state['last_update_log'] = log_cambios # REMOVED: return log instead
            if errores_mapeo:
                st.session_state['mapeo_warnings'] = errores_mapeo
            return True, f"✅ Éxito: {len(updates)} conceptos guardados.", log_cambios
            
        return False, "⚠️ No se encontraron filas que coincidan.", []
        
    except Exception as e:
        return False, f"❌ Error crítico de conexión: {str(e)}", []

def deshacer_actualizacion():
    if 'global_undo_log' in st.session_state and st.session_state['global_undo_log']:
        try:
            sheet = client.open_by_key(SPREADSHEET_ID)
            # Agrupar por hoja para eficiencia
            changes_by_ws = {}
            for change in st.session_state['global_undo_log']:
                ws_name = change['ws']
                if ws_name not in changes_by_ws:
                    changes_by_ws[ws_name] = []
                
                # RESTAURAR VALOR ORIGINAL: (Total - Incremento)
                # Si era texto o vacío, restauramos "" si original era 0/vacío
                try:
                    val_restored = float(change['val_total']) - float(change['val_orig'])
                    # Si el resultado es 0.0, poner "" para limpiar la celda
                    if val_restored == 0: val_restored = ""
                except:
                    val_restored = ""
                    
                changes_by_ws[ws_name].append({'range': change['range'], 'values': [[val_restored]]})
            
            for ws_name, updates in changes_by_ws.items():
                ws = sheet.worksheet(ws_name)
                ws.batch_update(updates)
                
            st.session_state['global_undo_log'] = [] # Limpiar tras deshacer
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
if 'texto_chat_history' not in st.session_state:
    st.session_state.texto_chat_history = []
if 'texto_datos_acumulados' not in st.session_state:
    st.session_state.texto_datos_acumulados = None
if 'texto_multi_res' not in st.session_state:
    st.session_state.texto_multi_res = []

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
        error_msg = str(e)
        if "429" in error_msg and len(st.session_state['api_key_pool']) > 1:
            st.warning("🔄 **Cuota agotada en chat. Rotando llave...**")
            st.session_state['current_key_index'] += 1
            configure_genai()
            # Reintentar una vez con la nueva llave
            return aplicar_correccion(user_input, current_data, model_id)
            
        if "429" in error_msg:
            st.error("🚨 **Límite de Quota Excedido en el Chat (Error 429)**")
            st.warning("Has alcanzado el límite de mensajes gratuitos para este modelo hoy.")
            st.info("💡 **Solución**: Agrega otra API Key en el panel lateral o cambia el modelo.")
        else:
            st.error(f"Error en el asistente de corrección: {e}")
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
        "🤖 Seleccionar Cerebro AI",
        [
            "gemini-3-flash-preview", 
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-3-pro-preview",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash", 
        ],
        help="Modelos 3.0: Máxima inteligencia. Modelos 2.5: Balance ideal. Si uno da error de quota (429), prueba con otro."
    )
    
    st.markdown("---")
    st.subheader("💡 Sistema de Origen")
    skill_sel = st.radio(
        "Tipo de Reporte (Skill)",
        list(AI_SKILLS.keys()),
        help="EPI: Reporte individual de paciente. CUADERNOS: Sumatoria de diario de consulta."
    )
    
    # 2. Gestión de API Keys (Pool de llaves)
    st.markdown("---")
    st.subheader("🔑 Mis API Keys")
    
    with st.expander("Gestionar llaves (Rotación)", expanded=False):
        nueva_key = st.text_input("Agregar nueva API Key:", type="password")
        if st.button("➕ Agregar a la lista"):
            if nueva_key and nueva_key not in st.session_state['api_key_pool']:
                st.session_state['api_key_pool'].append(nueva_key)
                st.success("Llave agregada correctamente.")
                # Forzar recarga inmediata para que el sistema reconozca el pool actualizado
                configure_genai() 
                time.sleep(1)
                st.rerun()
            elif nueva_key in st.session_state['api_key_pool']:
                st.warning("Esta llave ya está en la lista.")
        
        st.write(f"Total de llaves: **{len(st.session_state['api_key_pool'])}**")
        
        # Botón de Prueba de Rotación
        if len(st.session_state['api_key_pool']) > 1:
            if st.button("🔄 Probar Rotación (Cambiar Llave)"):
                st.session_state['current_key_index'] += 1
                configure_genai()
                st.toast("Llave rotada manualmente.", icon="🔀")
                st.rerun()

        if st.button("🗑️ Limpiar todas las llaves"):
            st.session_state['api_key_pool'] = []
            if "GEMINI_API_KEY" in st.secrets:
                st.session_state['api_key_pool'].append(st.secrets["GEMINI_API_KEY"])
            st.session_state['current_key_index'] = 0
            configure_genai()
            st.rerun()

    # Mostrar diagnóstico de la key activa actual
    if st.session_state['api_key_pool']:
        idx_activa = st.session_state['current_key_index'] % len(st.session_state['api_key_pool'])
        k_activa = st.session_state['api_key_pool'][idx_activa]
        masked = f"{k_activa[:6]}...{k_activa[-4:]}" if len(k_activa) > 10 else "***"
        st.info(f"🟢 **Activa**: Key #{idx_activa + 1} (`{masked}`)")
    else:
        st.error("⚠️ No hay API Keys configuradas.")
    
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

    # 4. Sincronización Global
    st.markdown("---")
    st.subheader("🔄 Consolidación")
    if st.button("📊 Sincronizar GENERALES", help="Suma los totales de todas las hojas de programa y actualiza la hoja GENERALES."):
        with st.spinner("Sincronizando totales..."):
            try:
                # El objeto 'sh' ya debería estar disponible si la conexión fue exitosa
                res = sync_generales(sh)
                if res["actualizados"]:
                    st.success(f"✅ Se actualizaron {len(res['actualizados'])} categorías.")
                    with st.expander("Ver detalles"):
                        for a in res["actualizados"]:
                            st.write(f"- {a}")
                if res["errores"]:
                    st.warning(f"⚠️ Hubo {len(res['errores'])} advertencias.")
                    with st.expander("Ver advertencias"):
                        for e in res["errores"]:
                            st.write(f"- {e}")
            except Exception as e:
                st.error(f"Error en sincronización: {e}")

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
    tab1, tab2, tab3 = st.tabs(["📂 Subir Archivo", "📸 Cámara", "📝 Texto Directo"])
    img = None
    
    with tab1:
        f_up_list = st.file_uploader("Selecciona imágenes o PDFs (puedes elegir varios)", type=['jpg','png','jpeg','pdf'], accept_multiple_files=True)
        if f_up_list:
            all_pages = []
            for f_up in f_up_list:
                if f_up.name.lower().endswith('.pdf'):
                    try:
                        import fitz  # pymupdf
                        pdf_bytes = f_up.read()
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        for page_num in range(len(doc)):
                            page = doc.load_page(page_num)
                            mat = fitz.Matrix(2, 2)
                            pix = page.get_pixmap(matrix=mat)
                            all_pages.append({
                                "source": f_up.name,
                                "page": page_num + 1,
                                "bytes": pix.tobytes("png")
                            })
                        doc.close()
                    except Exception as e:
                        st.error(f"Error leyendo PDF {f_up.name}: {e}")
                else:
                    all_pages.append({
                        "source": f_up.name,
                        "page": 1,
                        "bytes": f_up.read()
                    })
            
            # Guardar en el lote si hay cambios
            if 'batch_images' not in st.session_state or len(st.session_state['batch_images']) != len(all_pages):
                st.session_state['batch_images'] = all_pages
                st.session_state['batch_index'] = 0
                st.success(f"📂 **{len(all_pages)}** páginas/imágenes listas para procesar.")
            
            img = st.session_state['batch_images'][st.session_state.get('batch_index', 0)]['bytes']
            st.session_state.captured_img = None

    with tab2:
        if not st.session_state.cam_active:
            if st.button("📷 ACTIVAR CÁMARA", use_container_width=True):
                st.session_state.cam_active = True
                st.rerun()
        else:
            f_cam = st.camera_input("Capturar con cámara")
            if f_cam:
                st.session_state.captured_img = f_cam.getvalue()
                st.session_state.cam_active = False
                st.session_state.pop('batch_images', None)  # Limpiar lote al usar cámara
                st.rerun()
            
            if st.button("🚫 DESACTIVAR CÁMARA", use_container_width=True):
                st.session_state.cam_active = False
                st.rerun()
    
    with tab3:
        st.markdown("""    
        💬 **Pega datos médicos** y la IA los analizará para subirlos a Google Sheets.
        Puedes enviar varios mensajes y la IA irá **acumulando** los datos.
        """)
        
        # Mostrar historial del chat de texto
        texto_chat_container = st.container(height=250)
        with texto_chat_container:
            for msg in st.session_state.texto_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Input de texto directo
        texto_input = st.text_area(
            "📋 Pega aquí los datos médicos:",
            placeholder="Ej: HOJA PNNA - Lactantes: Masculino 19, Femenino 31, Sanos 18, Enfermos 16...\n\nTambién puedes pegar datos que extraigas de NotebookLM u otra fuente.",
            height=150,
            key="texto_directo_input"
        )
        
        col_analizar, col_experto, col_limpiar = st.columns([2, 2, 1])
        
        with col_analizar:
            if st.button("🚀 ANALIZAR TEXTO", type="primary", use_container_width=True, disabled=not texto_input):
                if texto_input:
                    st.session_state.texto_chat_history.append({"role": "user", "content": texto_input})
                    with st.spinner(f"Analizando con {modelo_sel}..."):
                        res_list = procesar_texto(
                            texto_input,
                            model_id=modelo_sel,
                            target_ws=selected_ws,
                            known_activities=activities_context,
                            skill_name="TEXTO DIRECTO (Chat)",
                            conversation_history=st.session_state.texto_chat_history[:-1]
                        )
                        if res_list:
                            # Nueva persistencia multi-hoja
                            st.session_state.texto_multi_res = [r for r in res_list if r.get('datos')]
                            st.session_state.texto_multi_res_index = 0
                            
                            # CRÍTICO: Establecer el primer resultado como "actual" para que el renderizador (L1342) lo muestre
                            if st.session_state.texto_multi_res:
                                st.session_state['current_res'] = st.session_state.texto_multi_res[0]
                            
                            msj_ia = f"✅ Detectadas **{len(st.session_state.texto_multi_res)}** hojas.\n"
                            for res in st.session_state.texto_multi_res:
                                msj_ia += f"- 📍 **{res['destino']}**: {len(res['datos'])} conceptos.\n"
                            
                            # Cargar la primera por defecto
                            if st.session_state.texto_multi_res:
                                st.session_state['current_res'] = st.session_state.texto_multi_res[0]

                            st.session_state.texto_chat_history.append({"role": "assistant", "content": msj_ia})
                            st.rerun()

        with col_experto:
            if st.button("🧠 CONSULTA EXPERTA", help="Usa NotebookLM para mapeo de precisión", use_container_width=True, disabled=not texto_input):
                st.session_state.texto_chat_history.append({"role": "user", "content": f"CONSULTA EXPERTA: {texto_input}"})
                with st.spinner("Consultando NotebookLM (Modo Agente)..."):
                    res_list = procesar_texto(
                        texto_input,
                        model_id=modelo_sel,
                        target_ws=selected_ws,
                        known_activities=activities_context,
                        skill_name="EXPERT_NOTEBOOK_SKILL", # Skill especial de alta precisión
                        conversation_history=st.session_state.texto_chat_history[:-1]
                    )
                    if res_list:
                        st.session_state.texto_multi_res = [r for r in res_list if r.get('datos')]
                        st.session_state.texto_multi_res_index = 0
                        st.session_state['current_res'] = st.session_state.texto_multi_res[0]
                        st.session_state.texto_chat_history.append({
                            "role": "assistant", 
                            "content": f"🧠 **NotebookLM ha respondido.** He aplicado reglas expertas de clasificación para {len(st.session_state.texto_multi_res)} hojas."
                        })
                        st.rerun()

        with col_limpiar:
            if st.button("🗑️ Limpiar Chat", use_container_width=True):
                st.session_state.texto_chat_history = []
                st.session_state.texto_datos_acumulados = None
                if 'current_res' in st.session_state:
                    del st.session_state['current_res']
                st.rerun()
        
    # Priorizar la imagen capturada si existe, de lo contrario la subida
    if st.session_state.captured_img:
        img = st.session_state.captured_img

# --- Navegación del Lote (Batch) ---
if 'batch_images' in st.session_state and st.session_state['batch_images']:
    batch = st.session_state['batch_images']
    b_idx = st.session_state.get('batch_index', 0)
    total_items = len(batch)
    current_item = batch[b_idx]
    
    st.info(f"📄 **{current_item['source']}** - Parte {current_item['page']} de {total_items} en total")
    
    # --- Chat/Instrucciones para la IA ---
    with st.expander("💬 **Instrucciones para la IA** (opcional)", expanded=False):
        user_instructions = st.text_area(
            "Escribe instrucciones específicas para la IA:",
            placeholder="Ej: 'Esta página es de Escolares', 'Ignora la sección de nutrición'",
            key="ai_instructions"
        )
        if user_instructions:
            st.session_state['ai_user_instructions'] = user_instructions
    
    # --- Selección de páginas ---
    with st.expander("📑 **Seleccionar para Procesamiento Masivo**", expanded=False):
        options = [f"#{i+1}: {item['source']} (P{item['page']})" for i, item in enumerate(batch)]
        selected = st.multiselect(
            "Elige los reportes que quieres procesar en lote:",
            options=options,
            default=[],
            key="selected_batch_multi"
        )
        st.session_state['selected_batch_indices'] = [int(p.split(":")[0].replace("#", "")) - 1 for p in selected]
    
    col_prev, col_next, col_process_all = st.columns([1, 1, 2])
    with col_prev:
        if st.button("⬅️ Anterior", disabled=(b_idx == 0)):
            st.session_state['batch_index'] = b_idx - 1
            st.session_state.pop('current_res', None)
            st.rerun()
    with col_next:
        if st.button("➡️ Siguiente", disabled=(b_idx >= total_items - 1)):
            st.session_state['batch_index'] = b_idx + 1
            st.session_state.pop('current_res', None)
            st.rerun()
    with col_process_all:
        selected_indices = st.session_state.get('selected_batch_indices', [])
        if selected_indices:
            btn_label = f"🔄 PROCESAR {len(selected_indices)} SELECCIONADOS"
            items_to_process = [(i, batch[i]) for i in selected_indices]
        else:
            btn_label = "🔄 PROCESAR TODO EL LOTE"
            items_to_process = [(i, item) for i, item in enumerate(batch)]
        
        if st.button(btn_label, type="secondary"):
            st.session_state['batch_results'] = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            user_instr = st.session_state.get('ai_user_instructions', '')
            
            for idx, (original_idx, item) in enumerate(items_to_process):
                status_text.text(f"⏳ Procesando {item['source']} ({idx+1}/{len(items_to_process)})...")
                progress_bar.progress((idx + 1) / len(items_to_process))
                
                res = procesar_imagen(
                    item['bytes'], 
                    model_id=modelo_sel, 
                    target_ws=None, 
                    known_activities=[],
                    skill_name=skill_sel,
                    user_context=user_instr
                )
                
                if res:
                    st.session_state['batch_results'].append({
                        'source': item['source'],
                        'page': item['page'],
                        'destino': res.get('destino', 'No detectado'),
                        'datos': res['datos'],
                        'razonamiento': res.get('razonamiento', '')
                    })
            
            progress_bar.empty()
            status_text.empty()
            st.success(f"✅ {len(st.session_state['batch_results'])} reportes procesados")
            st.rerun()
    
    img = batch[b_idx]['bytes']

# --- Mostrar resultados del procesamiento en lote ---
if 'batch_results' in st.session_state and st.session_state['batch_results']:
    st.markdown("## 📊 Resultados del Procesamiento en Lote")
    
    # Agrupar por hoja/departamento
    results_by_sheet = {}
    for result in st.session_state['batch_results']:
        sheet_name = result['destino']
        if sheet_name not in results_by_sheet:
            results_by_sheet[sheet_name] = {'sources': [], 'all_data': []}
        
        source_info = f"{result['source']} (P{result['page']})"
        results_by_sheet[sheet_name]['sources'].append(source_info)
        results_by_sheet[sheet_name]['all_data'].extend(result['datos'])
    
    # Mostrar resumen por hoja
    for sheet_name, sheet_data in results_by_sheet.items():
        with st.expander(f"📑 **{sheet_name}** ({len(sheet_data['sources'])} reportes)", expanded=True):
            st.caption(f"Orígenes: {', '.join(sheet_data['sources'])}")
            
            # Mostrar datos combinados
            df_sheet = pd.DataFrame(sheet_data['all_data'])
            edited_df = st.data_editor(
                df_sheet,
                use_container_width=True,
                num_rows="dynamic",
                key=f"editor_{sheet_name}",
                column_config={
                    "actividad": st.column_config.TextColumn("Coordenada", width="large"),
                    "valor": st.column_config.NumberColumn("Valor", min_value=0, format="%d")
                }
            )
            
            # Botón para guardar esta hoja
            if st.button(f"💾 Guardar en {sheet_name}", key=f"save_{sheet_name}"):
                with st.spinner(f"Guardando en {sheet_name}..."):
                    res_to_save = {
                        'destino': sheet_name,
                        'datos': edited_df.to_dict('records')
                    }
                    exito, msj = guardar_datos_quirurgico(res_to_save, semana_sel)
                    if exito:
                        st.success(msj)
                    else:
                        st.error(msj)
    
    # Botón para limpiar resultados
    if st.button("🗑️ Limpiar Resultados en Lote"):
        st.session_state.pop('batch_results', None)
        st.rerun()

    # Checkbox MODO LENTO
    st.toggle("🐢 Modo Lento / Seguro (Usar si aparecen errores rojos)", key="safe_mode_active", help="Aumenta las pausas entre hojas a 8 segundos. Recomendado si tienes muchas hojas.")

    if st.toggle("Modo Sobrescritura (⚠️ Borrar valor anterior)", key="overwrite_mode_toggle", help="Si lo activas, el robot BORRARÁ lo que había en la celda y pondrá el valor nuevo. Si lo desactivas (por defecto), SUMARÁ."):
        st.session_state['overwrite_mode'] = True
    else:
        st.session_state['overwrite_mode'] = False

# -----------------
# BOTÓN DE DESHACER (Visible si hay cambios recientes)
if st.session_state.get('global_undo_log'):
    st.markdown("⚠️ **¿Cometiste un error en la carga anterior?**")
    if st.button("↩️ DESHACER ÚLTIMA CARGA (Restar valores sumados)", type="primary"):
        with st.spinner("Deshaciendo cambios..."):
            if deshacer_actualizacion():
                st.success("✅ Carga revertida correctamente. Los valores se han restado.")
                time.sleep(1.5)
                st.rerun()
# -----------------

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
                st.rerun()

if 'current_res' in st.session_state:
    # --- SELECTOR DE RESULTADOS MULTI-HOJA ---
    if st.session_state.get('texto_multi_res') and len(st.session_state.texto_multi_res) > 1:
        multi_list = st.session_state.texto_multi_res
        # CRÍTICO: Definir nombres_hojas antes de insertar
        nombres_hojas = [f"{i+1}. {r['destino']} ({len(r['datos'])} conceptos)" for i, r in enumerate(multi_list)]
        
        # Opción para "Ver Resumen General"
        nombres_hojas.insert(0, "📊 VER TODO (Resumen General)")
        
        st.markdown(f"### 📑 Se detectaron {len(multi_list)} hojas en el reporte")
        
        col_sel, col_acc = st.columns([3, 1])
        with col_sel:
            sel_idx = st.selectbox(
                "Selecciona la hoja que deseas revisar:",
                range(len(multi_list) + 1),
                format_func=lambda x: nombres_hojas[x],
                index=st.session_state.get('texto_multi_res_index', 0),
                key="multi_res_selector"
            )
        
        with col_acc:
            if st.button("💾 GUARDAR TODO", type="primary", use_container_width=True):
                st.session_state['save_all_trigger'] = True
                st.rerun()

        # Actualizar índice
        if sel_idx != st.session_state.get('texto_multi_res_index'):
             st.session_state.texto_multi_res_index = sel_idx
             st.rerun()

    # LÓGICA DE GUARDADO MASIVO
    if st.session_state.get('save_all_trigger'):
        with st.spinner("Guardando todas las hojas detectadas..."):
            log_errores = []
            log_exitos = []
            progress_bar = st.progress(0)
            
            for i, res_item in enumerate(st.session_state.texto_multi_res):
                # NORMALIZACIÓN CRÍTICA ANTES DE GUARDAR
                raw_dest = res_item.get('destino', '').strip().upper()
                final_dest = raw_dest # Default
                
                # Intentar buscar en SHEET_ALIASES
                if raw_dest in SHEET_ALIASES:
                    final_dest = SHEET_ALIASES[raw_dest]
                # Intentar buscar coincidencia parcial con HOJAS_VALIDAS
                elif raw_dest not in HOJAS_VALIDAS:
                     for v in HOJAS_VALIDAS:
                         if v in raw_dest or raw_dest in v:
                             final_dest = v
                             break
                
                # Actualizar el item antes de enviar
                res_item['destino'] = final_dest
                
                # Pasar flag de overwrite
                overwrite_active = st.session_state.get('overwrite_mode', False)
                exito, msj, log_parcial = guardar_datos_quirurgico(res_item, semana_sel, overwrite=overwrite_active)
                if exito:
                    st.session_state.setdefault('global_undo_log', []).extend(log_parcial)
                    log_exitos.append(f"✅ {res_item['destino']}")
                else:
                    log_errores.append(f"❌ {res_item['destino']}: {msj}")
                progress_bar.progress((i + 1) / len(st.session_state.texto_multi_res))
            
            progress_bar.empty()
            st.session_state['save_all_trigger'] = False
            
            if log_exitos:
                st.success(f"Guardado exitoso: {', '.join(log_exitos)}")
            if log_errores:
                st.error(f"Errores al guardar: {'; '.join(log_errores)}")
            if not log_errores:
                st.balloons()
                # Opcional: Limpiar si todo salió bien
                # del st.session_state['texto_multi_res']
                # st.rerun()

    # VISTA: RESUMEN GENERAL (Índice 0)
    if st.session_state.get('texto_multi_res_index') == 0 and st.session_state.get('texto_multi_res'):
        st.info("Vista previa de toda la extracción. Puedes guardar todo arriba o ir hoja por hoja.")
        all_data_combined = []
        for r in st.session_state.texto_multi_res:
            for d in r['datos']:
                d['Origen'] = r['destino'] # Añadir etiqueta de hoja
                all_data_combined.append(d)
        
        st.dataframe(pd.DataFrame(all_data_combined), use_container_width=True)
        st.stop() # Salir para no mostrar editor individual

    # VISTA: EDITOR INDIVIDUAL (Índices > 0)
    # Ajustar índice porque insertamos "Ver Todo" al principio
    real_idx = st.session_state.get('texto_multi_res_index', 1) - 1
    if real_idx >= 0 and real_idx < len(st.session_state.texto_multi_res):
        res = st.session_state.texto_multi_res[real_idx]
        st.session_state['current_res'] = res # Sincronizar para compatibilidad
    else:
        res = st.session_state.get('current_res')

    if not res: st.stop()
    st.success(f"📍 Mostrando datos de: **{res['destino']}**")
    
    # Crear un DataFrame para edición
    df_editor = pd.DataFrame(res['datos'])
    
    # Mostrar editor interactivo
    edited_df = st.data_editor(
        df_editor, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "actividad": st.column_config.TextColumn("Coordenada (Sección > Grupo > Item)", width="large"),
            "valor": st.column_config.NumberColumn("Valor", min_value=0, format="%d")
        }
    )
    
    # Sincronizar cambios de vuelta al session_state
    if not edited_df.equals(df_editor):
        st.session_state['current_res']['datos'] = edited_df.to_dict('records')
        # No hacemos rerun aquí para evitar loops, el botón de Guardar usará la data fresca
    
    # --- Mostrar razonamiento de la IA (dudas/confianza) ---
    if 'razonamiento' in res and res['razonamiento']:
        with st.expander("🧠 **Razonamiento de la IA** (Revisa antes de guardar)", expanded=True):
            st.markdown(f"_{res['razonamiento']}_")
            st.caption("⚠️ Si ves algún error en el razonamiento, corrige los valores arriba antes de guardar.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"📤 GUARDAR EN {res['destino']}", type="primary", use_container_width=True):
            with st.spinner("Guardando..."):
                # Asegurarse de usar los datos editados
                # Asegurarse de usar los datos editados
                res_to_save = st.session_state['current_res']
                overwrite_active = st.session_state.get('overwrite_mode', False)
                
                exito, msj, log_parcial = guardar_datos_quirurgico(res_to_save, semana_sel, overwrite=overwrite_active)
                if exito:
                    # Guardar log para deshacer
                    st.session_state.setdefault('global_undo_log', []).extend(log_parcial)
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
if 'current_res' in st.session_state:
    st.markdown("---")
    st.subheader("💬 Asistente de Correcciones")
    if st.button("🧹 LIMPIAR CHAT"):
        st.session_state.chat_history = []
        st.rerun()
    
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
    
    # --- CUADRO TOTALIZADOR (RESUMEN FINAL) ---
    st.markdown("##### 📊 Resumen Totalizado (Correcciones Aplicadas)")
    res_final = st.session_state['current_res']
    df_resmen = pd.DataFrame(res_final['datos'])
    # Mostrar como tabla compacta para mejor estética
    st.table(df_resmen)

if 'last_update_log' in st.session_state:
    st.markdown("---")
    if st.button("⏪ DESHACER ÚLTIMA CARGA EN SHEETS", type="secondary", use_container_width=True):
        if deshacer_actualizacion():
            st.success("✅ Datos borrados de la tabla correctamente.")
            st.rerun()
