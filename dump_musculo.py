import gspread
import toml

secrets = toml.load('.streamlit/secrets.toml')
creds = dict(secrets['GOOGLE_CREDENTIALS'])
creds['private_key'] = creds['private_key'].replace('\\n', '\n')
gc = gspread.service_account_from_dict(creds)
ws = gc.open_by_key(secrets['SHEET_ID']).worksheet('MUSCULOESQUELETICAS')
rows = ws.col_values(1)

with open("musculoesqueleticas_rows.txt", "w", encoding="utf-8") as f:
    for i, r in enumerate(rows[:50]):
        f.write(f"{i+1}: {r}\n")
