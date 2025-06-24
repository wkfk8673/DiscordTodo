from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os

os.makedirs("data", exist_ok=True)

db = TinyDB("data/todos.json", storage=CachingMiddleware(JSONStorage), encoding="utf-8")
User = Query()

def add_todo(user_id, text):
    db.insert({"user_id": user_id, "text": text, "done": False})

def list_todos(user_id):
    return db.search(User.user_id == user_id)

def delete_todo_multiple(user_id, indexes):
    todos = list_todos(user_id)
    deleted = []
    for i in sorted(indexes, reverse=True):
        if 0 <= i < len(todos):
            db.remove(doc_ids=[todos[i].doc_id])
            deleted.append(todos[i]['text'])
    return deleted

def delete_all_todos(user_id):
    db.remove(User.user_id == user_id)

def mark_done_multiple(user_id, indexes):
    todos = list_todos(user_id)
    marked = []
    for i in indexes:
        if 0 <= i < len(todos):
            db.update({"done": True}, doc_ids=[todos[i].doc_id])
            marked.append(todos[i]['text'])
    return marked

def mark_all_done(user_id):
    todos = list_todos(user_id)
    for t in todos:
        db.update({"done": True}, doc_ids=[t.doc_id])

def clear_completed(user_id):
    db.remove((User.user_id == user_id) & (User.done == True))

def restore_from_google_sheet(sheet):
    db.truncate()
    records = sheet.get_all_records()
    for row in records:
        user_id = str(row.get("User ID") or "")
        text = row.get("할 일") or ""
        done_val = row.get("완료됨")
        done = str(done_val).strip().lower() in ["true", "1", "yes", "y", "완료", "o", "✔", "✅"]
        if user_id and text:
            db.insert({"user_id": user_id, "text": text, "done": done})

def save_to_google_sheet(sheet):
    sheet.clear()
    sheet.append_row(["User ID", "할 일", "완료됨"])
    for row in db.all():
        sheet.append_row([
            row.get("user_id", ""),
            row.get("text", ""),
            "TRUE" if row.get("done") else "FALSE"
        ])
