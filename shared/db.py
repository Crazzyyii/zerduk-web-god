import json, os

DB_FILE = os.path.join(os.path.dirname(__file__), "db.json")
STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_db():
    return _load(DB_FILE)

def save_db(data):
    _save(DB_FILE, data)

def load_stats():
    return _load(STATS_FILE)

def save_stats(data):
    _save(STATS_FILE, data)

def ensure_files():
    # Ensure both files exist
    if not os.path.exists(DB_FILE):
        save_db({})
    if not os.path.exists(STATS_FILE):
        save_stats({})
