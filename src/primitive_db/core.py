import os
from .constants import VALID_TYPES, DATA_DIR, META_FILE
from .utils import load_table_data, save_table_data, save_metadata

def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")
            if func.__name__ in ['insert', 'select', 'update', 'delete']:
                return [] if func.__name__ in ['insert', 'select'] else args[0]
            return args[0] if args else None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return [] if func.__name__ in ['insert', 'select'] else args[0] if args else None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return [] if func.__name__ == 'insert' else args[0] if args else None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return [] if func.__name__ in ['insert', 'select'] else args[0] if args else None
    return wrapper

@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    schema = {"ID": "int"}
    for col_def in columns:
        if ":" not in col_def:
            print(f'Некорректное значение: {col_def}. Попробуйте снова.')
            return metadata
        name, type_ = col_def.split(":", 1)
        if type_ not in VALID_TYPES:
            print(f'Некорректное значение: {type_}. Попробуйте снова.')
            return metadata
        schema[name] = type_

    # Сначала обновляем словарь в памяти
    metadata[table_name] = {"columns": schema}

    # И только потом сохраняем на диск
    save_metadata(metadata)
    save_table_data(table_name, [])

    cols_str = ", ".join([f"{k}:{v}" for k, v in schema.items() if k != "ID"])
    print(f'Таблица "{table_name}" успешно создана со столбцами: ID:int' + (", " + cols_str if cols_str else ""))
    return metadata

@handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    save_metadata(metadata)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

def list_tables(metadata: dict) -> None:
    if not metadata:
        print("(список таблиц пуст)")
    else:
        for name in metadata.keys():
            print(f"- {name}")

@handle_db_errors
def insert(metadata: dict, table_name: str, values: list) -> list:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []

    table_data = load_table_data(table_name)
    schema = metadata[table_name]["columns"]
    expected_count = len(schema) - 1

    if len(values) != expected_count:
        print(f"Ошибка: Ожидалось {expected_count} значений, получено {len(values)}.")
        return table_data

    if table_data:
        new_id = max(record["ID"] for record in table_data) + 1
    else:
        new_id = 1

    col_names = [name for name in schema.keys() if name != "ID"]
    record = {"ID": new_id}

    for i, value in enumerate(values):
        col_name = col_names[i]
        expected_type = schema[col_name]

        if expected_type == "int":
            try:
                record[col_name] = int(value)
            except ValueError:
                print(f"Ошибка валидации: значение '{value}' для столбца '{col_name}' не является числом.")
                return table_data
        elif expected_type == "str":
            record[col_name] = str(value)
        elif expected_type == "bool":
            if isinstance(value, bool):
                record[col_name] = value
            elif isinstance(value, str):
                if value.lower() in ("true", "yes", "1"):
                    record[col_name] = True
                elif value.lower() in ("false", "no", "0"):
                    record[col_name] = False
                else:
                    print(f"Ошибка валидации: значение '{value}' для столбца '{col_name}' не является boolean.")
                    return table_data
            else:
                print(f"Ошибка валидации: значение '{value}' для столбца '{col_name}' не является boolean.")
                return table_data
        else:
            record[col_name] = value

    table_data.append(record)
    save_table_data(table_name, table_data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

@handle_db_errors
def select(table_data: list, where_clause: dict = None) -> list:
    if not where_clause:
        return table_data
    result = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            result.append(row)
    return result

@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    updated = False
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            row.update(set_clause)
            updated = True
    return table_data if not updated else table_data

@handle_db_errors
def delete(table_data: list, where_clause: dict) -> list:
    initial_len = len(table_data)
    table_data = [row for row in table_data if not all(row.get(k) == v for k, v in where_clause.items())]
    if len(table_data) < initial_len:
        return table_data
    return table_data