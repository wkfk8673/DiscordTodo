import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tinydb import TinyDB

def backup_to_sheets(sheet_name="MyTodoBackup"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1
    sheet.clear()
    sheet.append_row(["User ID", "할 일", "완료됨"])

    db = TinyDB("data/todos.json")
    todos = db.all()

    for item in todos:
        sheet.append_row([
            item["user_id"],
            item["text"],
            "✅" if item["done"] else "⬜"
        ])
