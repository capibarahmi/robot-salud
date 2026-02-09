import gspread
import toml
import json

secrets = toml.load('.streamlit/secrets.toml')
creds = dict(secrets['GOOGLE_CREDENTIALS'])
creds['private_key'] = creds['private_key'].replace('\\n', '\n')
gc = gspread.service_account_from_dict(creds)
ws = gc.open_by_key(secrets['SHEET_ID']).worksheet('PNNA')
rows = ws.col_values(1)

filtered_rows = []
started = False
for r in rows:
    if "Escolar" in r: started = True
    if started:
        if "Sano" in r or "Enf" in r or "Diagn" in r or "Grado" in r or "Sucesiva" in r:
            filtered_rows.append(r)
        if "Adolescente" in r: break # Stop at next section

with open("rows_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_rows))
