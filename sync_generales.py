"""
sync_generales.py — Suma automática de totales por programa para la hoja GENERALES.

Mapea cada fila de GENERALES a la hoja/fila origen correspondiente.
Ejemplo: "Pediatría" en GENERALES ← Total Lactantes + Total Escolares de PNNA

Uso desde app.py:
    from sync_generales import sync_generales
    sync_generales(sh)  # sh = spreadsheet abierto con gspread
"""
import gspread


# =====================================================================
# MAPEO: Fila de GENERALES → (Hoja Origen, Fila a leer, Columna)
# Las columnas en Google Sheets suelen tener datos en B, C, D, etc.
# Usaremos columna 2 (B) por defecto (valor de la primera columna numérica)
# =====================================================================
GENERALES_MAP = {
    # ----- CONSULTAS POR TIPO DE MÉDICO -----
    "Pediatría":                        ("PNNA", "Total Lactantes y Pre-escolares"),
    "Nutrición":                        ("NUTRICIÓN", "Programa de Nutrición"),
    "Odontología Curativa":             ("SALUD BUCAL", "Total Consultas Odontológicas"),
    "Psiquiatría":                      ("SALUD MENTAL", "0208 Total de Consultas (A+B+C+F+D) (Salud Mental)"),
    "I.T.S. - SIDA":                    ("ITS-HIV-SIDA", "0211 Total de Consultas (P ó X + S)"),
    "Ginecología":                      ("SSR", "0201 Total Prenatal (A+B+D)"),
    "Obstetricia":                      ("SSR", "Atencion Materna"),
    "Patología Cuello":                 ("PREVENCION CANCER CUELLO UTERIN", "0215 Pesquisa Oncológica (Total A+D)"),
    "Cardiología":                      ("CARDIOVASCULAR", "Total de Consultas (1+2)"),
    "Endocrino":                        ("ENDOCRINO-METABOLICO", "Total de Consultas (1+2) (Diabéticos)"),
    "Geriatría":                        ("ADULTOS MAYOR", "Total Consultas Tercera Edad (A+D)"),
    "Neumonología":                     ("PSALUD RESPIRATORIA", "Programa Integrado De Tuberculosis Y Asma"),
    "Medicina General":                 ("PADULTO 19 A 60 AÑOS", "Total Consultas Adultos (A+D)"),

    # ----- FILAS GENÉRICAS (no mapeadas a hojas específicas) -----
    # Las siguientes filas no tienen hoja propia, se dejan para llenado manual:
    # "Medicina Familiar", "Medicina Interna", "Cirugía Ambulatoria (Adulto)", etc.
}


def sync_generales(sh, col_index=2):
    """
    Lee los totales de cada programa y los escribe en la hoja GENERALES.
    
    Args:
        sh: gspread.Spreadsheet abierto
        col_index: columna numérica a leer/write (2=B, 3=C, etc.)
    
    Returns:
        dict con resultados: {"actualizados": [...], "errores": [...]}
    """
    try:
        ws_general = sh.worksheet("GENERALES")
    except gspread.exceptions.WorksheetNotFound:
        return {"actualizados": [], "errores": ["Hoja 'GENERALES' no encontrada"]}

    # Leer todas las filas de GENERALES (col A)
    filas_generales = ws_general.col_values(1)

    actualizados = []
    errores = []

    for fila_nombre, (hoja_origen, fila_origen) in GENERALES_MAP.items():
        try:
            # Encontrar la fila en GENERALES
            idx_general = None
            for i, nombre in enumerate(filas_generales):
                if nombre.strip() == fila_nombre:
                    idx_general = i + 1  # 1-indexed
                    break

            if idx_general is None:
                errores.append(f"'{fila_nombre}' no encontrada en GENERALES")
                continue

            # Leer el valor de la hoja origen
            ws_origen = sh.worksheet(hoja_origen)
            filas_origen = ws_origen.col_values(1)

            idx_origen = None
            for i, nombre in enumerate(filas_origen):
                if nombre.strip() == fila_origen:
                    idx_origen = i + 1
                    break

            if idx_origen is None:
                errores.append(f"'{fila_origen}' no encontrada en hoja '{hoja_origen}'")
                continue

            # Leer el valor numérico de la hoja origen
            valor = ws_origen.cell(idx_origen, col_index).value
            if valor is None or valor.strip() == "":
                valor = 0
            else:
                try:
                    valor = int(float(valor))
                except ValueError:
                    valor = 0

            # Escribir en GENERALES
            ws_general.update_cell(idx_general, col_index, valor)
            actualizados.append(f"{fila_nombre} = {valor} (de {hoja_origen})")

        except Exception as e:
            errores.append(f"Error procesando '{fila_nombre}': {str(e)}")

    return {"actualizados": actualizados, "errores": errores}


if __name__ == "__main__":
    import toml
    secrets = toml.load('.streamlit/secrets.toml')
    creds = dict(secrets['GOOGLE_CREDENTIALS'])
    creds['private_key'] = creds['private_key'].replace('\\n', '\n')
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key(secrets['SHEET_ID'])
    
    result = sync_generales(sh)
    print("\n✅ ACTUALIZADOS:")
    for a in result['actualizados']:
        print(f"  {a}")
    if result['errores']:
        print("\n❌ ERRORES:")
        for e in result['errores']:
            print(f"  {e}")
