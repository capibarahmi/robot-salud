import gspread
from google.oauth2.service_account import Credentials
import re

def analyze():
    # Manual parsing of toml to avoid dependency issues
    secrets = {}
    with open(".streamlit/secrets.toml", "r") as f:
        current_section = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                if current_section not in secrets: secrets[current_section] = {}
            elif "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if current_section:
                    secrets[current_section][key] = value
                else:
                    secrets[key] = value
    
    # Reconstruct creds dict
    creds_dict = {
        "type": secrets["GOOGLE_CREDENTIALS"]["type"],
        "project_id": secrets["GOOGLE_CREDENTIALS"]["project_id"],
        "private_key_id": secrets["GOOGLE_CREDENTIALS"]["private_key_id"],
        "private_key": secrets["GOOGLE_CREDENTIALS"]["private_key"].replace("\\n", "\n"),
        "client_email": secrets["GOOGLE_CREDENTIALS"]["client_email"],
        "client_id": secrets["GOOGLE_CREDENTIALS"]["client_id"],
        "auth_uri": secrets["GOOGLE_CREDENTIALS"]["auth_uri"],
        "token_uri": secrets["GOOGLE_CREDENTIALS"]["token_uri"],
        "auth_provider_x509_cert_url": secrets["GOOGLE_CREDENTIALS"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": secrets["GOOGLE_CREDENTIALS"]["client_x509_cert_url"],
    }
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(secrets["SHEET_ID"])
    ws = sheet.worksheet("PNNA")
    
    rows = ws.col_values(1)
    for i in range(229, 300): 
        if i < len(rows):
            print(f"{i+1}: {rows[i]}")

if __name__ == "__main__":
    analyze()
