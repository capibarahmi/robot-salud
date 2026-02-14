import gspread
import toml
import re

def check_bold():
    secrets = toml.load('.streamlit/secrets.toml')
    creds = dict(secrets['GOOGLE_CREDENTIALS'])
    creds['private_key'] = creds['private_key'].replace('\\n', '\n')
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key(secrets['SHEET_ID'])
    ws = sh.worksheet("PNNA")
    
    # Intentar obtener metadatos de formato
    try:
        # Spreadsheet.get() permite especificar campos
        res = gc.request('get', f'https://sheets.googleapis.com/v4/spreadsheets/{secrets["SHEET_ID"]}?ranges=PNNA!A1:A50&fields=sheets(data(rowData(values(userEnteredFormat/textFormat/bold))))')
        data = res.json()
        rows = data['sheets'][0]['data'][0]['rowData']
        for i, row in enumerate(rows):
            vals = row.get('values', [])
            if vals:
                bold = vals[0].get('userEnteredFormat', {}).get('textFormat', {}).get('bold', False)
                print(f"Fila {i+1}: {'BOLD' if bold else 'normal'}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bold()
