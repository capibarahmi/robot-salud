"""Dump ALL sheet tabs and their first-column structure."""
import gspread
import toml
import json

secrets = toml.load('.streamlit/secrets.toml')
creds = dict(secrets['GOOGLE_CREDENTIALS'])
creds['private_key'] = creds['private_key'].replace('\\n', '\n')
gc = gspread.service_account_from_dict(creds)
sh = gc.open_by_key(secrets['SHEET_ID'])

# List ALL tabs
all_tabs = [ws.title for ws in sh.worksheets()]
print(f"TOTAL TABS: {len(all_tabs)}")
print("=" * 60)
for i, tab in enumerate(all_tabs, 1):
    print(f"{i:3d}. {tab}")

print("\n" + "=" * 60)
print("DUMPING ROWS FOR EACH TAB...")
print("=" * 60)

# Exclude known non-data sheets
EXCLUDE = {"GENERAL", "H-PRINCIPAL", "HPRINCIPAL", "Hoja 1", "Hoja 2", "Hoja 25", "Hoja1", "Hoja2", "Hoja25"}

output = {}
for tab_name in all_tabs:
    if tab_name in EXCLUDE:
        print(f"\n--- SKIPPING: {tab_name} ---")
        continue
    try:
        ws = sh.worksheet(tab_name)
        rows = ws.col_values(1)
        # Only first 80 rows to get the structure
        rows_clean = [r.strip() for r in rows[:80] if r.strip()]
        output[tab_name] = rows_clean
        print(f"\n--- {tab_name} ({len(rows_clean)} filas) ---")
        for j, r in enumerate(rows_clean, 1):
            print(f"  {j:3d}. {r}")
    except Exception as e:
        print(f"\n--- ERROR accessing {tab_name}: {e} ---")

# Save to file
with open("all_sheets_structure.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nSaved to all_sheets_structure.json")
