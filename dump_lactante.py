import gspread
import toml

secrets = toml.load('.streamlit/secrets.toml')
creds = dict(secrets['GOOGLE_CREDENTIALS'])
creds['private_key'] = creds['private_key'].replace('\\n', '\n')
gc = gspread.service_account_from_dict(creds)
ws = gc.open_by_key(secrets['SHEET_ID']).worksheet('PNNA')
rows = ws.col_values(1)

filtered_rows = []
started = False
for i, r in enumerate(rows):
    # Start capturing at Lactante section
    if "Lactante" in r or "Preescolar" in r or i < 135:
        filtered_rows.append(f"{i+1}: {r}")
    # Stop at Escolar to avoid duplication
    if i > 100 and "Escolar 7" in r:
        break

with open("lactante_rows.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_rows))
