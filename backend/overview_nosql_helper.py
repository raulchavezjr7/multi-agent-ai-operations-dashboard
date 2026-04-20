import os

from tinydb import Query, TinyDB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "overview.json")

db = TinyDB(DB_PATH)
Overview = Query()


def get_all_overview():
    return db.all()


def get_overview(overview_id: str):
    return db.get(Overview.id == overview_id)


def add_overview(overview_data):
    db.insert(overview_data)
    return overview_data


def update_overview(overview_id: int, updates):
    db.update(updates, doc_ids=[overview_id])
    return db.get(doc_id=overview_id)


def delete_overview(overview_id: str):
    db.remove(Overview.id == overview_id)
    return True
