import gspread
import toml

secrets = toml.load('.streamlit/secrets.toml')
creds = dict(secrets['GOOGLE_CREDENTIALS'])
creds['private_key'] = creds['private_key'].replace('\\n', '\n')
gc = gspread.service_account_from_dict(creds)
ws = gc.open_by_key(secrets['SHEET_ID']).worksheet('PNNA')
rows = ws.col_values(1)

# Find start of Adolescente section (should be after Escolar)
start_idx = None
for i, r in enumerate(rows):
    if "Adolescente" in r and "12" in r:  # "Adolescente de 12 a 19"
        start_idx = i
        break

if start_idx:
    filtered_rows = []
    for i in range(start_idx, min(start_idx + 80, len(rows))):
        filtered_rows.append(f"{i+1}: {rows[i]}")
    
    with open("adolescente_rows.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_rows))
else:
    print("Adolescente section not found")
