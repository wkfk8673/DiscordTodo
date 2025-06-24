import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("MyTodoBackup").sheet1
sheet.clear()
sheet.append_row(["User ID", "할 일", "완료됨"])

print("✅ 시트에 정상적으로 접근되었습니다!")
