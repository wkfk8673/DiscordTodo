import json
import os

DATA_PATH = "data/todos.json"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w") as f:
        json.dump({}, f)

def load_todos():
    with open(DATA_PATH, "r", encoding="utf-8") as f:  # ← 인코딩 추가
        return json.load(f)

def save_todos(todos):
    with open(DATA_PATH, "w", encoding="utf-8") as f:  # ← 인코딩 추가
        json.dump(todos, f, indent=2, ensure_ascii=False)

def add_todo(user_id, item):
    todos = load_todos()
    todos.setdefault(user_id, []).append({"text": item, "done": False})
    save_todos(todos)

def list_todos(user_id):
    todos = load_todos()
    return todos.get(user_id, [])

def delete_todo_multiple(user_id, indices):
    todos = load_todos()
    try:
        user_todos = todos.get(user_id, [])
        indices = sorted(set(indices), reverse=True)
        deleted_items = []
        for index in indices:
            if 0 <= index < len(user_todos):
                deleted_items.append(user_todos.pop(index)["text"])
        if not user_todos:
            todos.pop(user_id)
        save_todos(todos)
        return list(reversed(deleted_items))
    except (IndexError, KeyError):
        return None

def delete_all_todos(user_id):
    todos = load_todos()
    if user_id in todos:
        deleted = [item["text"] for item in todos[user_id]]
        del todos[user_id]
        save_todos(todos)
        return deleted
    return None

def mark_done_multiple(user_id, indices):
    todos = load_todos()
    results = []
    try:
        for index in indices:
            if 0 <= index < len(todos[user_id]):
                item = todos[user_id][index]
                if not item["done"]:
                    item["done"] = True
                    results.append((index, item["text"], True))
                else:
                    results.append((index, item["text"], False))
        save_todos(todos)
        return results
    except (IndexError, KeyError):
        return None

def mark_all_done(user_id):
    todos = load_todos()
    updated = []
    try:
        for item in todos.get(user_id, []):
            if not item["done"]:
                item["done"] = True
                updated.append(item["text"])
        save_todos(todos)
        return updated
    except KeyError:
        return None

def clear_completed():
    todos = load_todos()
    changed = False
    for user_id in list(todos.keys()):
        new_items = [item for item in todos[user_id] if not item["done"]]
        if len(new_items) != len(todos[user_id]):
            if new_items:
                todos[user_id] = new_items
            else:
                del todos[user_id]
            changed = True
    if changed:
        save_todos(todos)
