import gspread
from google.oauth2.service_account import Credentials
import toml

# Read from secrets
secrets = toml.load('.streamlit/secrets.toml')
creds_dict = dict(secrets['GOOGLE_CREDENTIALS'])
if 'private_key' in creds_dict:
    creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sheet_id = secrets['SHEET_ID']
sheet = client.open_by_key(sheet_id)
ws = sheet.worksheet('PNNA')

# Get all values from column A
col_a = ws.col_values(1)

# Print with row numbers for analysis
with open('pnna_rows.txt', 'w', encoding='utf-8') as f:
    for i, val in enumerate(col_a[:250], 1):
        f.write(f'{i}: {val}\n')
        print(f'{i}: {val}')

print("\n\nSaved to pnna_rows.txt")
