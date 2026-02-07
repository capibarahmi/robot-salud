import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Load credentials from the local JSON file
with open("cuenta servicio robot sim-capibara-ba845446c392.json") as f:
    creds_dict = json.load(f)

# Hardened formatting
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_ID = "1k3hJ5X5_ebnLbGj4XiA1I8t8x28-zlH0QjjuuHkDRnw"

def analyze():
    print(f"Connecting to Sheet: {SHEET_ID}...")
    sheet = client.open_by_key(SHEET_ID)
    worksheets = sheet.worksheets()
    
    print(f"Found {len(worksheets)} worksheets.\n")
    
    for ws in worksheets:
        print(f"Worksheet: {ws.title}")
        try:
            headers = ws.row_values(1)
            print(f"  Headers: {headers}")
        except Exception as e:
            print(f"  Error reading headers: {e}")
        print("-" * 30)

if __name__ == "__main__":
    analyze()
