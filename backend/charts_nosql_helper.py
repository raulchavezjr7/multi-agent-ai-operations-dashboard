import os

from tinydb import Query, TinyDB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "charts.json")

db = TinyDB(DB_PATH)
Chart = Query()


def get_all_charts():
    return db.all()


def get_chart(chart_id: str):
    return db.get(Chart.id == chart_id)


def add_chart(chart_data: dict):
    db.insert(chart_data)
    return chart_data


def update_chart(chart_id: str, updates: dict):
    db.update(updates, Chart.id == chart_id)
    return get_chart(chart_id)


def delete_chart(chart_id: str):
    db.remove(Chart.id == chart_id)
    return True
