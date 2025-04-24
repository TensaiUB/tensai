import json
import os

DB_FILE_PATH: str = os.path.join("tensai/db", 'db.json')


def _load() -> dict:
    """Loads datas from db."""
    if not os.path.exists(DB_FILE_PATH):
        return {}
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save(data: dict) -> None:
    """Save datas into db."""
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get(keys, default: any = None) -> any:
    data = _load()
    if isinstance(keys, str):
        keys = keys.split('.')

    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data


def set(key: str, value) -> None:
    data = _load()
    keys = key.split('.')

    current = data
    for i, sub_key in enumerate(keys):
        if i == len(keys) - 1:
            current[sub_key] = value
        else:
            if sub_key not in current or not isinstance(current[sub_key], dict):
                current[sub_key] = {}
            current = current[sub_key]

    _save(data)