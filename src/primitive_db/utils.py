# src/primitive_db/utils.py
import json
import os

from .constants import DATA_DIR, META_FILE


def _get_project_root():
    """Возвращает абсолютный путь к корню проекта (директории src)."""
    # __file__ -> путь к текущему utils.py
    # os.path.dirname -> путь к папке primitive_db
    # еще раз os.path.dirname -> путь к папке src
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_metadata(filepath: str = META_FILE) -> dict:
    """Загружает метаданные. Если файла нет — возвращает пустой словарь."""
    project_root = _get_project_root()
    full_path = os.path.join(project_root, filepath)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(data: dict, filepath: str = META_FILE) -> None:
    """Сохраняет метаданные в файл."""
    project_root = _get_project_root()
    full_path = os.path.join(project_root, filepath)

    # Проверяем, есть ли у файла директория (для db_meta.json это корень, директории нет)
    dir_path = os.path.dirname(full_path)
    if dir_path: # Выполняем makedirs только если путь не пустой
        os.makedirs(dir_path, exist_ok=True)

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_table_data(table_name: str) -> list:
    """Загружает данные конкретной таблицы."""
    project_root = _get_project_root()
    filepath = os.path.join(project_root, DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные конкретной таблицы."""
    project_root = _get_project_root()
    filepath = os.path.join(project_root, DATA_DIR, f"{table_name}.json")

    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)