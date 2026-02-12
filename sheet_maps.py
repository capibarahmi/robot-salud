# sheet_maps.py — Diccionario completo de mapeo para TODAS las hojas de Google Sheets
# Fuente: all_sheets_structure.json (dump directo del spreadsheet)
import json

# =====================================================================
# ESTRUCTURA COMPLETA DE TODAS LAS HOJAS (filas de la columna A)
# =====================================================================
ALL_SHEETS = {
  "PNNA": [
    "ACTIVIDAD /ESTABLECIMIENTO",
    "Programa De Atención Integral Niño Y Adolescente",
    "Atención al Lactante y Pre-escolar Hasta 6 años",
    "Total Lactantes y Pre-escolares",
    "Masculino Lactantes y Pre-escolares",
    "Femenino Lactantes y Pre-escolares",
    "Total de Consultas < 23 Meses (A+B+C+D)",
    "A. 1rea Consulta < de 1 mes",
    "B. 1era. Consulta de 1 a 11 meses",
    "C. 1era. Consulta de 12 a 23 meses",
    "D. Consulta Sucesivas <  23 Meses",
    "E. Lactantes Atendidos por Enfermería",
    "Total de Consultas de 2 a  6 Años (A+B+D)",
    "A. 1era. Consulta de 2 a 3 años",
    "B. 1era. Consulta de 4 a 6 años",
    "D. Consultas Sucesivas de 2 a 6 años",
    "E. Preescolares Atendidos por Enfermería",
    "Estado Nutricional Lactante y Pre-escolar",
    "Exceso", "Normal", "Zona Crítica", "Leve", "Moderada", "Grave",
    "Evaluación Cefálica",
    "Microcefalia", "Macrocefalia", "Normal",
    "Déficit Lactante y Pre-escolar",
    "Examen Sensorial", "Desarrollo Psicomotor", "Agudeza Visual", "Audición y Lenguaje", "Maduración Sexual",
    "Tensión Arterial Lactante y Pre-escolar",
    "Normal", "Hipertenso", "Hipotenso",
    "Riesgo Biológico Lactante y Pre-escolar",
    "Enf. Infecciosas y Parasitarias", "Neoplasias",
    "Enf. de la Sangre y Org. Hematopoyético",
    "Enf. Endocrina, Nutricional y Metabólica",
    "Enf. Trastorno Mental y Comportamiento",
    "Enf. del Sistema Nervioso", "Enf. del Ojo y sus Anexos",
    "Enf. del Oído y Apófisis Mastoides", "Enf. del Sistema Circulatorio",
    "Enf. del Sistema Respiratorio", "Enf. del Sistema Digestivo",
    "Enf. de la Piel y Tej. Conjuntivo", "Enf. Genital y Urinaria",
    "Enf. Parto y Puerperio", "Traumatismo y Envenenamientos",
    "Anomalía Congénita",
    "Diagnósticos:  (Lactante y Pre-escolar)",
    "Lactantes Sanos", "Lactantes Enfermos",
    "Pre-escolares Sanos", "Pre-escolares Enfermos",
    "Programa de Atención en Salud Escolar 7 a Menores de 12 Años",
    "Total  Escolares",
    "Masculino Escolar", "Femenino Escolar",
    "Total de Consultas Escolares (A+B+C+D+F)",
    "A.- 1era. Consulta 1er Grado", "B.- 1era. Consulta 3er Grado",
    "C.- 1era. Consulta 6to Grado",
    "D.- Consultas Sucesivas y Otros Grados",
    "E.- Escolar Atendido por Enfermería",
    "F. Primeras Consultas de Otros Grados",
    "Estado Nutricional Escolar",
    "Exceso", "Normal", "Zona Crítica", "Leve", "Moderada", "Grave",
    "Riesgo Biológico Escolar",
    "Enf. Infecciosas y Parasitarias", "Neoplasias",
    "Enf. de la Sangre y Org. Hematopoyético",
    "Enf. Endocrina, Nutricional y Metabólica",
    "Enf. Trastorno Mental y Compotamiento",
    "Enf. del Sistema Nervioso", "Enf. del Ojo y Sus Anexos",
    "Enf. del Oído y Apófisis Mastoides", "Enf. del Sistema Circulatorio",
    "Enf. Sistema Respiratorio", "Enf. del Sistema Digestivo",
    "Enf. de la Piel y Tej. Conjuntivo", "Enf. Genital y Urinaría",
    "Diagnósticos (Escolares)",
    "Escolares Sanos", "Escolares Enfermos",
  ],

  "PADULTO 19 A 60 AÑOS": [
    "ACTIVIDAD",
    "Programa De Atención Al Adulto De 19años A Menores De 60 Años",
    "Total Adultos", "Masculino Adultos", "Femenino Adultos",
    "Total Consultas Adultos (A+D)",
    "A. 1eras Consultas Adultos", "D. Consultas Sucesivas Adultos",
    "E. Adultos Atendidos por Enfermería",
    "Diagnósticos (Adultos)", "Adulto Sano", "Adulto Enfermo",
    "Estado Nutricional (Adulto)",
    "Exceso", "Normal", "Zona Crítica", "Leve", "Moderada", "Grave", "Bajo Peso",
    "Déficit (Adulto)", "Examen Sensorial", "Agudeza Visual", "Audición y Lenguaje", "Maduración Sexual",
    "Tensión Arterial (Adulto)", "Normal", "Hipertenso", "Hipotenso",
    "Riesgo Biológico (Adultos)",
    "Enf. Infecciosas y Parasitarias", "Neoplasias",
    "Enf. de la Sangre y Org. Hematopoyético",
    "Enf. Endocrina, Nutricional y Metabólica",
    "Enf. Trastor Mental y Comportamiento",
    "Enf. del Sisteam Nervioso", "Enf. del Ojo y sus Anexos",
    "Enf. del Ojo y Apísis Mastoides",
    "Enf. de Sistema Circulatorio", "Enf. del Sistema Respiratorio",
    "Enf. del Sistema Digestivo", "Enf. de la Piel y Tej. Conjuntivo",
    "Enf. Genital y Urinaria", "Enf. Parto y Puerperio",
    "Traumatismos y Envenenamientos",
    "Riesgo Psicosocial (Adultos)",
    "Accidente del Hogar", "Accidente de Tránsito",
    "Violencia Familiar",
  ],

  "ADULTOS MAYOR": [
    "Actividad",
    "Programa De La Tercera Edad 60 Años Y Más",
    "Total de la Tercera Edad", "Masculino Tercera Edad", "Femenino Tercera Edad",
    "Total Consultas Tercera Edad (A+D)",
    "A. 1era Consulta Tercera Edad", "D. Consulta Sucesiva Tercera Edad",
    "E. Adultos Atendidos por Enfermería",
    "Diagnósticos (Tercera Edad)",
    "Adulto de la Tercera Edad Sano", "Adulto de la Tercera Edad Enfermo",
    "Estado Nutricional (Tercera Edad)",
    "Exceso", "Normal", "Zona Crítica", "Leve", "Moderada", "Grave", "Bajo Peso",
    "Déficit (Tercera Edad)", "Examen Sensorial", "Agudeza Visual", "Audición y Lenguaje",
    "Tensión Arterial (Tercera Edad)", "Normal", "Hipertenso", "Hipotenso",
    "Riesgo Biológico (Tercera Edad)",
    "Enf. Infecciosas y Parasitarias", "Neoplasias",
    "Enf. de la Sangre y Org. Hematopoyético",
    "Enf. Endocrina, Nutricional y Metabólica",
    "Enf. Trastorno Mental y Comportamiento",
    "Enf. Sistema Nervioso", "Enf. del Ojo y sus Anexos",
    "Enf. del Oído y Apófisis Mastoides",
    "Enf. del Sistema Circulatorio", "Enf. del Sistema Respiratorio",
    "Enf. Sistema Digestivo", "Enf. de la Piel y Tej. Conjuntivo",
    "Enf. Genital y Urinaria", "Traumatismos y Envenenamientos",
  ],

  "PSALUD RESPIRATORIA": [
    "ACTIVIDAD",
    "Programa Integrado De Tuberculosis Y Asma",
    "Programa de Tuberculosis",
    "Primeras Consultas 15 años y más (Tuberculosis)",
    "Sintomáticos Respiratorios Identificados",
    "Sintomáticos Respiratorios Examinados",
    "Casos Nuevos de T.B.C. por Tipo de Diagnóstico",
    "1. Serie P (Pulmonar Bk+) 15 Años y más",
    "2. Serie N (Pulmonar Bk-) 15 Años y más",
    "3. Serie EP (Extrapulmonar) 15 Años y más",
    "T.B.C en Menores de 15 Años",
    "Recaídas Diagnosticadas",
    "Programa de Asma",
    "Diagnósticos (Asma)",
    "1. Crisis en Usuarios de 0 a < 10 Años",
    "2. Crisis en Usuarios de 10 Años y más",
    "Tipo de Consulta (Asma)",
    "A. Primeras de 0 a <10 Años  (P ó X) Asma",
    "3. Leve", "4. Moderada", "5. Severa",
    "B. Primeras de 10 años  y Más (P ó X) Asma",
    "6. Leve", "7. Moderada", "8. Severa",
    "9. Sucesiva de 0 - 9 años Asma",
    "10. Sucesiva de 10 años y más Asma",
  ],

  "ITS-HIV-SIDA": [
    "ACTIVIDAD",
    "Programa De Control De Infecciones De Transmisión Sexual (I.T.S.)",
    "0211 Total de Consultas (P ó X + S)",
    "Primera Consulta ITS-SIDA", "Consultas Sucesivas ITS-SIDA",
    "Atendidos por Enfermería (ITS-SIDA)",
    "Sífilis",
    "Congénita < 2 Años Femenino", "Congénita < 2 Años Masculino",
    "Todas Formas 12 - 19 Años  Femenino", "Todas Formas 12 - 19 Años  Masculino",
    "Todas Formas 20 - 39 Años Femenino", "Todas Formas 20 - 39 Años  Masculino",
    "Todas Formas 40 y Más Años Femenino", "Todas Formas 40 y Más Años Masculino",
    "Embarazada con Sifílis",
    "Infección Gonocóccica",
    "Candidiasis Genital",
  ],

  "SANGRE SEGURA": [
    "ACTIVIDAD",
    "Programa Sangre Segura",
    "Total de Pacientes Atendidos",
    "Donantes Atendidos", "Donantes Aceptados", "Donantes Descartados",
    "Donantes voluntarios", "Donantes Diferidos",
    "Transfusiones Preparadas",
    "Transfusiones Administradas (1+2)",
    "1.Niños, Niñas, Adolescentes", "2.Adultos (as)",
    "Número de Reacciones a la Transfusión",
    "Transfusiones Descartadas",
    "Estudios Inmunohematológicos",
    "ABO", "RH", "RH DEBIL",
  ],

  "PREVENCION CANCER CUELLO UTERIN": [
    "ACTIVIDAD",
    "Prevención Y Control Del Cáncer Cervico Uterino",
    "0215 Pesquisa Oncológica (Total A+D)",
    "A. Mayor de 3 años Realizada (P)", "D. Menor de 3 años Realizada",
    "Patología Cervical",
    "1. Primera Consulta con Colposcopia", "2. Primera Consulta sin Colposcopia",
    "3. Consulta Sucesiva sin Colposcopia", "4. Consulta Sucesiva con Colposcopia",
    "Manejo Terapéutico",
    "1. Radioterapia", "2. Cirugía", "3. Cono en frío", "4. Exéresis",
    "Prevención Y Control Del Cáncer De Mama",
    "Prevención Y Control Del Cáncer De Próstata",
    "Prevención Y Control Del Cáncer De Pulmón",
    "Prevención Y Control Otro Tipo de Cáncer",
  ],

  "PROMOCIÓN DE SALUD": [
    "ACTIVIDAD",
    "Educación Sanitaria",
    "Número de Personas Capacitadas en:",
    "Nutrición e Higiene",
    "Signos de Alarma durante el Embarazo",
    "Importancias de la Consulta Sucesivas",
    "Lactancia Materna",
    "Prevención Diarreas", "Prevención de I.R.A.", "Vacunas",
    "Auto Examen de Mamas y Cáncer",
    "Prevención del Cáncer de Cuello Uterino",
    "Planificación de la Pareja",
    "Dengue", "I.T.S. - SIDA", "Tuberculosis", "Epilepsia",
    "Diabetes e Hipertensión Arterial",
    "Seguridad y Prevención Hechos Violentos",
    "Otras",
  ],

  "ENDOCRINO-METABOLICO": [
    "ACTIVIDAD",
    "Programa Endocrino Metabólico",
    "Programa Prevención y Control de Diabetes Mellitus",
    "Total por Género del Alto Riesgo",
    "Total de Masculino", "Total de Femenino",
    "Alto Riesgo Para Diabetes (1+2+3+4)",
    "1. 1eras. Consultas con Glicemia Normal",
    "2. 1eras. Consultas con Glicemia Alterada",
    "3. 1eras. Consultas con Glicemia Alterada en ayunas",
    "4. 1eras. Consultas con Intolerancia a los Hidratos de Carbono",
    "Consultas Sucesivas con Glicemia Alterada",
    "Total de Consultas (1+2) (Diabéticos)",
    "1. 1eras Consultas (P ó X)", "2. Consultas Sucesivas (S)",
    "Clasificación del Consultante: Solo Casos Nuevos (DX)",
    "Diabetes Tipo 1", "Diabetes Tipo 2", "Diabetes Gestacional",
    "Complicaciones Agudas (DM)",
    "1. Cetoacidosis", "2. Hipoglicemia", "3. Descompensación por Hiperglicemia",
    "Complicaciones Crónicas (DM)",
    "4. Neuropatía Periférica", "5. Neuropatía Autonómica",
    "6. Retinopatía Preproliferativa", "7. Retinopatía Proliferativa",
    "16. Cardiopatía Isquémica",
  ],

  "CARDIOVASCULAR": [
    "Programa Prevención y Control de Enfermedades Cardiovasculares",
    "Factores de Riesgo",
    "Total de Masculino", "Total de Femenino",
    "Pacientes con Dislipidemias",
    "Pacientes Obesos (más de 20% sobre el Peso Ideal)",
    "Número de Personas con Hábito Tabáquico",
    "Personas con Diabetes Mellitus",
    "Hipertensión Arterial Sistémica",
    "Total de Consultas (1+2)",
    "1.  1eras. Consultas (P ó X)", "2.   Consultas Sucesivas (S)",
    "3.Controlados por Enfermería",
    "Clasif. del Consultante: (Casos Nuevos)",
    "H.T.A. Estadio I", "H.T.A. Estadio II",
    "Cardiopatía Isquémica", "Fiebre Reumática", "Chagas",
    "H.T.A. + Diabetes tipo 1", "H.T.A. + Diabetes tipo 2",
    "Complicaciones Agudas (HTA)",
    "Infarto del Miocardio", "Crisis Hipertensiva",
    "Insuficiencia Cardíaca por H.T.A.",
  ],

  "HEREDOMETABÓLICAS": [
    "ACTIVIDAD",
    "Programa Heredo Metabólico",
    "Programa tamizaje",
    "Total por Género del Alto Riesgo",
    "Total de Masculino", "Total de Femenino",
    "Alto Riesgo Herdometabólicas (1+2+3+4)",
    "1. 1eras. Consultas con Valores Normales",
    "2. 1eras. Consultas con Valores Alterados",
    "Consultas Sucesivas",
    "Total de Consultas (1+2) (HM)",
    "1. 1eras Consultas (P ó X)", "2. Consultas Sucesivas (S)",
    "Clasificación del Consultante: Solo Casos Nuevos (DX)",
    "Fibrosis Quística", "Fenilcetonuria",
    "Hipotiroidismo Congénito", "Hiperplasia Suprarrenal congénita",
  ],

  "SALUD BUCAL": [
    "ACTIVIDAD",
    "PROGRAMA DE SALUD BUCAL",
    "Días Odontólogo Trabajados",
    "Total de Consultas (2+3)",
    "2. Ingresos (Primera Vez)", "Femeninos", "Masculinos",
    "3. Sucesivas", "Femeninos", "Masculinos",
    "Total Consultas Odontológicas",
    "Primera Consulta Odontológica",
    "Primera consulta < 10 años", "Primera consulta 10 a 19 años",
    "Primera consulta  19 años a 59 años", "Primera consulta > 60 años",
    "Consulta Sucesiva Odontológica",
    "Sucesiva < 10 años", "Sucesiva 10 a 19 años",
    "Sucesiva 20 a 59 años", "Sucesiva > 60 años",
  ],

  "SALUD MENTAL": [
    "ACTIVIDAD",
    "Programa De Atención Integral Salud Mental",
    "Total por Género (Salud Mental)",
    "Total Masculino (Salud Mental)", "Total Femenino (Salud Mental)",
    "0208 Total de Consultas (A+B+C+F+D) (Salud Mental)",
    "A. 1eras Consultas < de 12 años",
    "B. 1eras Consultas de 12 a < 19 años",
    "C. 1eras Consultas 19 a < 60 años",
    "F. 1eras Consultas 60 años y más",
    "D. Consultas Sucesivas", "E. Atendidos por Enfermería",
    "Diagnóstico (Salud Mental)",
    "Retraso Mental", "Trastorno Habilidades Escolares",
    "Trastorno de Lenguaje", "Trastorno Hiperkinético",
    "Trastorno de Conducta", "Esquizofrenia  y Otras Psicosis",
    "Depresión", "Demencia", "Epilepsia",
    "Abuso de Alcohol", "Trastornos de Ansiedad",
    "Abuso de Drogas", "Sin Evidencia de Trastorno Mental",
  ],

  "SSR": [
    "ACTIVIDAD",
    "Programa De Atención Integral Y Salud Reproductiva",
    "Atencion Materna",
    "0201 Total Prenatal (A+B+D)",
    "Primeras Consultas < 19 años (A)",
    "1. Hasta 13 Semanas", "2. 14 Semanas y más",
    "Primeras Consultas de 19 Años  y más (B)",
    "1. Hasta 13 Semanas", "2. Después de 14 Semanas y más",
    "Consultas Sucesivas (D)",
    "Tipo de Riesgo (Atención Materna)",
    "Bajo Riesgo", "Alto Riesgo Tipo I", "Alto Riesgo Tipo II", "Alto Riesgo Tpo III",
    "Patología del Embarazo",
    "1. Hipertensión Previa", "2. Preeclampsia", "3. Eclampsia",
    "4. Diabetes", "5. Infección Urinaria",
    "6. Amenaza Parto Prematuro", "7. Ruptura Prematura de Membrana",
    "Planificación Familiar de la Pareja",
    "Con Gestágenos Orales", "Con D.I.U.", "Método de Barrera",
    "Vasectomía", "Esterilización",
  ],

  "VISITAS Y ABORDAJES": [
    "ACTIVIDAD",
    "Visitas y Abordajes / Casa a Casa",
    "Total Visitas",
    "A Familias Nuevas con Alto Riesgo",
    "A Familias de Bajo Control con Bajo Riesgo",
    "A Niño s < 7 años con Alto Riesgo",
    "A Casos Prenatales Alto Riesgo",
    "A Casos T.B.C.", "A Contactos de V.I.H.",
    "A Casos de Dengue", "A Casos de Rabia",
    "A Escuelas", "A Otras Instituciones", "Otros",
  ],

  "SALUD RENAL": [
    "ACTIVIDAD",
    "Programa Prevención y Control de Enfermedades Renales",
    "Número de  Pacientes por Censo",
    "Total Pacientes Atendidos (1+2)",
    "1. Total Primeras",
    "Consultas Primera Masculinos", "Consultas Primera Femeninos",
    "2.Total Sucesivas",
    "Consultas Sucesivas Masculinos", "Consultas Sucesivas Femeninos",
    "Causas",
    "Glomerulonefritis", "Nefropatía Obstructiva", "Nefroangioesclerosis",
    "Poliquistosis Renal", "Nefropatía Diabética",
    "Hemodiálisis", "Diálisis Peritoneal",
  ],

  "NUTRICIÓN": [
    "ACTIVIDAD",
    "Programa de Nutrición",
    "Embarazadas",
    "Total de Consultas a Embarazadas (A+D)",
    "A. Primeras Consultas", "D. Consultas Sucesivas",
    "Riesgos Biológicos (Embarazada)", "1. Desnutrición", "2. Obesidad",
    "Total de Consultas  Lactantes <  2 Años (A+B+C+D)",
    "A. Primeras Consultas < 1 Mes",
    "B. Primeras Consultas de 1 a 11 Meses",
    "C. Primeras Consultas < 23 Meses",
    "D. Consultas Sucesivas Lactantes",
    "Total de Consultas Pre-Escolar de 2 a < 7 Años (A+B+D)",
    "Total de Consultas Escolares de 7 a < 12 Años (A+B+C+D)",
    "Total de Consultas Adolescente de 12 a < 19 Años (A+D)",
    "Total de Consultas Adulto de 19 a < 60 Años (A+D)",
    "Total de Consultas Adulto Mayor 60 Años y Más (A+D)",
  ],

  "DERMATOLOGÍA SANITARIA": [
    "ACTIVIDAD",
    "Programa De Atención Integral En Dermatología Sanitaria",
    "Sub-Programa de Hansen",
    "Total por Género (Hansen)",
    "Total Masculino (Hansen)", "Total Femenino (Hansen)",
    "0220 Total de Consultas (A+B+C+D) (Hansen)",
    "A. Primera Consulta 2 - 11 años",
    "B. Primeras Consultas de 12 - 19 años",
    "C. Primera Consulta 19 años y más",
    "D. Consultas Sucesivas (Controles Sucesivos a Casos)",
    "Total de Ingresos (Hansen) Diagnóstico",
    "Multibacilares", "Pausibacilares",
    "Sub-Programa de Leishmaniasis (Dermatología)",
    "Leishmaniasis Cutánea", "Leishmaniasis Visceral",
  ],

  "MUSCULOESQUELETICAS": [
    "ACTIVIDAD",
    "Prevención y Control del Enfermedades Musculoesqueléticas",
    "Total Pacientes Atendidos (1+2)",
    "1. Total Primeras",
    "Consultas Primera Masculinos", "Consultas Primera Femeninos",
    "2.Total Sucesivas",
    "Consultas Sucesivas Masculinos", "Consultas Sucesivas Femeninos",
    "Tipo de Patología",
    "Artritis Reumatoidea", "Artritis Psoriásica", "Artritis Reactiva",
    "Artritis Ideopatica Juvenil", "Tendinitis", "Tenosinovitis",
    "Bursitis", "Cervicalgia", "Dorsalgia", "Fibromialgia",
    "Lupus eritematoso sistémico", "Gota", "Osteoartrosis",
    "Osteoporosis", "Artralgias", "Otras",
  ],

  "PREVEN ACCD Y HECHOS VIOLEN ": [
    "ACTIVIDAD",
    "Total Violencia Familiar y Hechos Violentos",
    "Masculino", "Femenino",
    "Violencia familiar",
    "Accidente del Hogar", "Accidente de Tránsito",
    "Violencia Familiar", "Violencia Física",
    "Adolescente Hombre", "Adolescente Mujer",
    "Violencia Psicológica", "Violencia Sexual",
    "Tipo de Hecho Violento",
    "Abandono / Negligencia", "Accidente De Transito",
    "Accidente Laboral", "Agresión", "Homicidios",
    "Intento De Suicidio", "Maltrato", "Riña", "Suicidio",
    "Violencia Domestica",
    "Objeto con que se Efectuó el Hecho Violento",
    "Arma Blanca", "Arma De Fuego", "Golpiza",
    "Tipo De Lesión (Diagnostico)",
    "Fractura", "Herida", "Quemaduras", "Politraumatismo",
  ],

  "ZOONOSIS": [
    "ACTIVIDAD",
    "Sub Programa de Rabia",
    "1. Número de Personas Mordidas",
    "1.1 Por Animal Controlable", "1.2 Por Animal no Controlable",
    "2. Número de Animales Mordedores",
    "2.1 Caninos", "2.2 Felinos", "2.3 Otros",
    "6. Personas Mordidas Referidas a Trat.",
    "7. Número de Cerebros Enviados al Laboratorio",
    "8.4 Número de Animales Vacunados",
    "2. Sub - Programa Leptopirosis",
    "3. Sub - Programas Brucelosis",
    "4. Sub - Programa Leishmaniasis",
    "5. Sub - Programa Encefalitis Equina V.",
  ],
}

# =====================================================================
# REGLAS ESPECIALIZADAS PARA PNNA (de NotebookLM)
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

IMPORTANTE: "a" = años, "m" = meses, "d" = días
- "1a" = 1 año = 12 meses = LACTANTE MAYOR (NO preescolar)
"""

REGLAS_CONSULTA = """
MAPEO TIPO DE CONSULTA (P = Primera, S = Sucesiva):

LACTANTES (<2 años):
| Tipo | Edad | Fila destino |
|---|---|---|
| P | < 1 mes | "A. 1rea Consulta < de 1 mes" |
| P | 1-11 meses | "B. 1era. Consulta de 1 a 11 meses" |
| P | 12-23 meses | "C. 1era. Consulta de 12 a 23 meses" |
| S | cualquier <24m | "D. Consulta Sucesivas <  23 Meses" |

PREESCOLARES (2-6 años):
| Tipo | Edad | Fila destino |
|---|---|---|
| P | 2-3 años | "A. 1era. Consulta de 2 a 3 años" |
| P | 4-6 años | "B. 1era. Consulta de 4 a 6 años" |
| S | cualquier 2-6a | "D. Consultas Sucesivas de 2 a 6 años" |

ESCOLARES (7-11 años):
| Tipo | Fila destino |
|---|---|
| P sin grado | "F. Primeras Consultas de Otros Grados" |
| S | "D.- Consultas Sucesivas y Otros Grados" |
"""

DIAGNOSTICO_SISTEMA = """
MAPEO DIAGNÓSTICOS MANUSCRITOS A RIESGO BIOLÓGICO:
| Diagnóstico | Fila |
|---|---|
| Rinofaringitis, Asma, Bronquitis, Neumonía, IRA | "Enf. del Sistema Respiratorio" |
| Escabiosis, Dermatitis, Piodermitis, Urticaria | "Enf. de la Piel y Tej. Conjuntivo" |
| Gastroenteritis, Parasitosis, Diarrea, EDA | "Enf. Infecciosas y Parasitarias" |
| Anemia, Púrpura | "Enf. de la Sangre y Org. Hematopoyético" |
| ITU, Vulvovaginitis, Fimosis | "Enf. Genital y Urinaria" |
| Fractura, Quemadura, Mordedura | "Traumatismo y Envenenamientos" |
| Diabetes, Hipotiroidismo, Talla Baja, Obesidad | "Enf. Endocrina, Nutricional y Metabólica" |
| Conjuntivitis, Estrabismo | "Enf. del Ojo y sus Anexos" |
| Otitis, Amigdalitis (ORL) | "Enf. del Oído y Apófisis Mastoides" |
| Epilepsia, Convulsión | "Enf. del Sistema Nervioso" |
| TDAH, Autismo, Ansiedad | "Enf. Trastorno Mental y Comportamiento" |
| Embarazo, Parto, Puerperio | "Enf. Parto y Puerperio" |
| S. Down, Cardiopatía congénita | "Anomalía Congénita" |
| Reflujo, Dolor abdominal, Estreñimiento | "Enf. del Sistema Digestivo" |

ABREVIATURAS: CNS=Control Niño Sano, DLN=Dentro Límites Normales, ITU=Infección Tracto Urinario,
EDA=Enfermedad Diarreica Aguda, IRA=Infección Respiratoria Aguda, RN=Recién Nacido

REGLA SANO/ENFERMO: "Sano","CNS","DLN" = SANO. Cualquier patología = ENFERMO.
"""


# =====================================================================
# FUNCIÓN DINÁMICA: genera el prompt con las filas de la hoja destino
# =====================================================================
def get_sheet_prompt(sheet_name):
    """Devuelve las filas de una hoja formateadas para inyectar en el prompt de la IA."""
    # Buscar por nombre exacto o normalizado
    rows = ALL_SHEETS.get(sheet_name, [])
    if not rows:
        # Buscar por nombre parcial (por encodings diferentes)
        norm = sheet_name.upper().strip()
        for key, val in ALL_SHEETS.items():
            if key.upper().strip() == norm or norm in key.upper():
                rows = val
                break

    if not rows:
        return f"⚠️ No se encontró estructura para la hoja '{sheet_name}'. Usa los nombres que veas en la imagen."

    filas_str = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(rows)])

    prompt = f"""
📋 ESTRUCTURA DE FILAS DE LA HOJA "{sheet_name}":
Usa EXACTAMENTE estos nombres para el campo "actividad" en tu JSON.
NO escribas en filas de "Total" (tienen fórmulas automáticas).
Solo escribe en filas INDIVIDUALES (datos específicos).

{filas_str}
"""

    # Agregar reglas especializadas para PNNA
    if sheet_name == "PNNA":
        prompt += f"""

🎯 REGLAS ESPECIALES PARA PNNA:
{REGLAS_EDAD}
{REGLAS_CONSULTA}
{DIAGNOSTICO_SISTEMA}
"""

    return prompt


# =====================================================================
# PROMPT COMPLETO PARA PNNA (retrocompatibilidad)
# =====================================================================
PNNA_MAPPING_PROMPT = get_sheet_prompt("PNNA")
