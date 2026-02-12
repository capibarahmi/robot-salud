# sheet_maps.py — Diccionario completo de mapeo para hojas de Google Sheets
# Fuente: NotebookLM + pnna_rows.txt (estructura real del Excel)

# =====================================================================
# ESTRUCTURA PNNA — SECCIÓN LACTANTE Y PREESCOLAR (Filas 3-133)
# =====================================================================
PNNA_LACTANTE_PREESCOLAR = """
SECCIÓN: Atención al Lactante y Pre-escolar Hasta 6 años

SEXO:
- Fila 5: "Masculino Lactantes y Pre-escolares"
- Fila 6: "Femenino Lactantes y Pre-escolares"

CONSULTAS LACTANTES (<23 meses):
- Fila 8:  "A. 1rea Consulta < de 1 mes" → Primera consulta, bebé < 1 mes
- Fila 9:  "B. 1era. Consulta de 1 a 11 meses" → Primera consulta, 1-11 meses
- Fila 10: "C. 1era. Consulta de 12 a 23 meses" → Primera consulta, 12-23 meses
- Fila 11: "D. Consulta Sucesivas <  23 Meses" → Consulta sucesiva, cualquier lactante
- Fila 12: "E. Lactantes Atendidos por Enfermería"

CONSULTAS PREESCOLARES (2-6 años):
- Fila 14: "A. 1era. Consulta de 2 a 3 años" → Primera consulta, 2-3 años
- Fila 15: "B. 1era. Consulta de 4 a 6 años" → Primera consulta, 4-6 años
- Fila 16: "D. Consultas Sucesivas de 2 a 6 años" → Consulta sucesiva, cualquier preescolar
- Fila 17: "E. Preescolares Atendidos por Enfermería"

ESTADO NUTRICIONAL:
- Fila 19: "Exceso"
- Fila 20: "Normal"
- Fila 21: "Zona Crítica"
- Fila 22: "Leve"
- Fila 23: "Moderada"
- Fila 24: "Grave"

EVALUACIÓN CEFÁLICA:
- Fila 26: "Microcefalia"
- Fila 27: "Macrocefalia"
- Fila 28: "Normal"

DÉFICIT:
- Fila 30: "Examen Sensorial"
- Fila 31: "Desarrollo Psicomotor"
- Fila 32: "Agudeza Visual"
- Fila 33: "Audición y Lenguaje"
- Fila 34: "Maduración Sexual"

TENSIÓN ARTERIAL:
- Fila 36: "Normal"
- Fila 37: "Hipertenso"
- Fila 38: "Hipotenso"

RIESGO BIOLÓGICO (Morbilidad):
- Fila 40: "Enf. Infecciosas y Parasitarias"
- Fila 41: "Neoplasias"
- Fila 42: "Enf. de la Sangre y Org. Hematopoyético"
- Fila 43: "Enf. Endocrina, Nutricional y Metabólica"
- Fila 44: "Enf. Trastorno Mental y Comportamiento"
- Fila 45: "Enf. del Sistema Nervioso"
- Fila 46: "Enf. del Ojo y sus Anexos"
- Fila 47: "Enf. del Oído y Apófisis Mastoides"
- Fila 48: "Enf. del Sistema Circulatorio"
- Fila 49: "Enf. del Sistema Respiratorio"
- Fila 50: "Enf. del Sistema Digestivo"
- Fila 51: "Enf. de la Piel y Tej. Conjuntivo"
- Fila 52: "Enf. Genital y Urinaria"
- Fila 53: "Enf. Parto y Puerperio"
- Fila 54: "Traumatismo y Envenenamientos"
- Fila 55: "Anomalía Congénita"

DIAGNÓSTICOS:
- Fila 97: "Lactantes Sanos"
- Fila 98: "Lactantes Enfermos"
- Fila 99: "Pre-escolares Sanos"
- Fila 100: "Pre-escolares Enfermos"
"""

# =====================================================================
# ESTRUCTURA PNNA — SECCIÓN ESCOLAR (Filas 134-251)
# =====================================================================
PNNA_ESCOLAR = """
SECCIÓN: Programa de Atención en Salud Escolar 7 a Menores de 12 Años

SEXO:
- Fila 136: "Masculino Escolar"
- Fila 137: "Femenino Escolar"

CONSULTAS:
- Fila 139: "A.- 1era. Consulta 1er Grado" → Primera consulta, 1er grado (~7 años)
- Fila 140: "B.- 1era. Consulta 3er Grado" → Primera consulta, 3er grado (~9 años)
- Fila 141: "C.- 1era. Consulta 6to Grado" → Primera consulta, 6to grado (~11 años)
- Fila 142: "D.- Consultas Sucesivas y Otros Grados" → Consultas sucesivas
- Fila 143: "E.- Escolar Atendido por Enfermería"
- Fila 144: "F. Primeras Consultas de Otros Grados" → Primera consulta sin grado específico

ESTADO NUTRICIONAL:
- Fila 150: "Exceso"
- Fila 151: "Normal"
- Fila 152: "Zona Crítica"
- Fila 153: "Leve"
- Fila 154: "Moderada"
- Fila 155: "Grave"

RIESGO BIOLÓGICO (Morbilidad):
- Fila 167: "Enf. Infecciosas y Parasitarias"
- Fila 168: "Neoplasias"
- Fila 169: "Enf. de la Sangre y Org. Hematopoyético"
- Fila 170: "Enf. Endocrina, Nutricional y Metabólica"
- Fila 171: "Enf. Trastorno Mental y Compotamiento"
- Fila 172: "Enf. del Sistema Nervioso"
- Fila 173: "Enf. del Ojo y Sus Anexos"
- Fila 174: "Enf. del Oído y Apófisis Mastoides"
- Fila 175: "Enf. del Sistema Circulatorio"
- Fila 176: "Enf. Sistema Respiratorio"
- Fila 177: "Enf. del Sistema Digestivo"
- Fila 178: "Enf. de la Piel y Tej. Conjuntivo"
- Fila 179: "Enf. Genital y Urinaría"

DIAGNÓSTICOS:
- Fila 230: "Escolares Sanos"
- Fila 231: "Escolares Enfermos"
"""

# =====================================================================
# TABLA DE CLASIFICACIÓN DE EDAD → GRUPO PNNA
# =====================================================================
REGLAS_EDAD = """
CLASIFICACIÓN DE EDAD PARA PNNA:
| Edad del paciente | Grupo en PNNA | Notación manuscrita |
|---|---|---|
| 0 días a 29 días | Lactante (Neonato) | "1d", "15d", "RN", "Neonato" |
| 1 mes a 11 meses | Lactante menor | "1m", "2m", "5m", "8m", "11m" |
| 12 meses a 23 meses | Lactante mayor | "1a", "12m", "18m", "1 año" |
| 2 años a 3 años | Preescolar (rango A) | "2a", "3a", "2 años", "3 años" |
| 4 años a 6 años | Preescolar (rango B) | "4a", "5a", "6a" |
| 7 años a 11 años | Escolar | "7a", "8a", "9a", "10a", "11a" |
| 12 años a 18 años | Adolescente | "12a", "13a", "14a", "15a"-"18a" |

IMPORTANTE:
- "a" = años, "m" = meses, "d" = días
- "1a" = 1 año = 12 meses = LACTANTE MAYOR (NO preescolar)
- "2a" = 2 años = PREESCOLAR (ya NO es lactante)
"""

# =====================================================================
# MAPEO DE TIPO DE CONSULTA → FILA EXACTA
# =====================================================================
REGLAS_CONSULTA = """
MAPEO TIPO DE CONSULTA:
En el reporte manuscrito: P = Primera consulta, S = Sucesiva

LACTANTES (<2 años):
| Tipo | Edad | Fila destino |
|---|---|---|
| P (Primera) | < 1 mes | "A. 1rea Consulta < de 1 mes" |
| P (Primera) | 1-11 meses | "B. 1era. Consulta de 1 a 11 meses" |
| P (Primera) | 12-23 meses | "C. 1era. Consulta de 12 a 23 meses" |
| S (Sucesiva) | cualquier <24m | "D. Consulta Sucesivas <  23 Meses" |

PREESCOLARES (2-6 años):
| Tipo | Edad | Fila destino |
|---|---|---|
| P (Primera) | 2-3 años | "A. 1era. Consulta de 2 a 3 años" |
| P (Primera) | 4-6 años | "B. 1era. Consulta de 4 a 6 años" |
| S (Sucesiva) | cualquier 2-6a | "D. Consultas Sucesivas de 2 a 6 años" |

ESCOLARES (7-11 años):
| Tipo | Edad | Fila destino |
|---|---|---|
| P (Primera) | ~7 años / 1er grado | "A.- 1era. Consulta 1er Grado" |
| P (Primera) | ~9 años / 3er grado | "B.- 1era. Consulta 3er Grado" |
| P (Primera) | ~11 años / 6to grado | "C.- 1era. Consulta 6to Grado" |
| P (Primera) | otros / sin grado | "F. Primeras Consultas de Otros Grados" |
| S (Sucesiva) | cualquier 7-11a | "D.- Consultas Sucesivas y Otros Grados" |

ADOLESCENTES (12-18 años):
| Tipo | Fila destino |
|---|---|
| P (Primera) | "A. Primera Consulta Adolescentes" |
| S (Sucesiva) | "D. Consulta Sucesiva Adolescentes" |
"""

# =====================================================================
# MAPEO DE DIAGNÓSTICO MANUSCRITO → CATEGORÍA DE RIESGO BIOLÓGICO
# =====================================================================
DIAGNOSTICO_SISTEMA = """
MAPEO DE DIAGNÓSTICOS MANUSCRITOS A SISTEMA:
(El médico escribe diagnósticos específicos. Debes clasificarlos en el sistema correcto)

| Diagnóstico manuscrito | Fila de Riesgo Biológico |
|---|---|
| Rinofaringitis, Asma, Bronquitis, Neumonía, Bronquiolitis, Rinitis Alérgica, Sibilancia, Tos, IRA | "Enf. del Sistema Respiratorio" |
| Escabiosis, Dermatitis, Piodermitis, Prurigo, Tinea, Miliaria, Urticaria, Impétigo | "Enf. de la Piel y Tej. Conjuntivo" |
| Gastroenteritis, Parasitosis, Diarrea, EDA, GEAA, Síndrome Viral, Amebiasis, Giardiasis | "Enf. Infecciosas y Parasitarias" |
| Anemia, Púrpura, Hemorrágica, Talasemia | "Enf. de la Sangre y Org. Hematopoyético" |
| ITU, Infección urinaria, Vulvovaginitis, Fimosis, Criptorquidia | "Enf. Genital y Urinaria" |
| Traumatismo, Fractura, Quemadura, Mordedura, Contusión, Herida | "Traumatismo y Envenenamientos" |
| Diabetes, Hipotiroidismo, Talla Baja, Obesidad, Desnutrición | "Enf. Endocrina, Nutricional y Metabólica" |
| Cardiopatía, Soplo, Hipertensión | "Enf. del Sistema Circulatorio" |
| Conjuntivitis, Estrabismo, Chalazión, Orzuelo | "Enf. del Ojo y sus Anexos" |
| Otitis, Hipoacusia, Amigdalitis (ORL) | "Enf. del Oído y Apófisis Mastoides" |
| Epilepsia, Convulsión, Cefalea crónica, Parálisis | "Enf. del Sistema Nervioso" |
| TDAH, Autismo, Ansiedad, Depresión, Retraso del desarrollo | "Enf. Trastorno Mental y Comportamiento" |
| Embarazo, Control prenatal, Parto, Puerperio | "Enf. Parto y Puerperio" |
| Síndrome de Down, Labio leporino, Cardiopatía congénita, Síndrome de Poland | "Anomalía Congénita" |
| Reflujo, Dolor abdominal, Estreñimiento, Vómitos | "Enf. del Sistema Digestivo" |

ABREVIATURAS COMUNES EN REPORTES MANUSCRITOS:
| Abreviatura | Significado |
|---|---|
| CNS / C.N.S | Control Niño Sano |
| DLN | Dentro de Límites Normales (= Sano) |
| Emb | Embarazo |
| Sem | Semanas |
| ITU / I.T.U | Infección del Tracto Urinario |
| EDA | Enfermedad Diarreica Aguda |
| IRA | Infección Respiratoria Aguda |
| GEAA | Gastroenteritis Aguda Acuosa |
| RN | Recién Nacido |
| Sme | Síndrome |

REGLA SANO vs ENFERMO:
- Si el diagnóstico es "Sano", "CNS", "Control Niño Sano", "DLN", "Lactante Sano", "Escolar Sano", "Neonato Sano" → contar como SANO
- Si el diagnóstico es CUALQUIER patología → contar como ENFERMO
- Un paciente con "Talla Baja" + "Escolar Sano" → contar como SANO (el control de talla no indica enfermedad)
"""

# =====================================================================
# PROMPT COMPLETO PARA INYECTAR EN LA IA
# =====================================================================
PNNA_MAPPING_PROMPT = f"""
🏥 MAPA COMPLETO DE LA HOJA PNNA (Programa Niño, Niña y Adolescente)
Esta hoja cubre TODOS los pacientes de 0 a 18 años.

{REGLAS_EDAD}

{REGLAS_CONSULTA}

{DIAGNOSTICO_SISTEMA}

📋 ESTRUCTURA DE FILAS — LACTANTE Y PREESCOLAR (0-6 años):
{PNNA_LACTANTE_PREESCOLAR}

📋 ESTRUCTURA DE FILAS — ESCOLAR (7-11 años):
{PNNA_ESCOLAR}
"""
