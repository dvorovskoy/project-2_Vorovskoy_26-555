import functools
import time

# src/primitive_db/decorators.py

def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")
            if func.__name__ in ['insert', 'select']:
                return []
            if func.__name__ in ['update', 'delete']:
                return args[0] if args else []
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец '{e}' не найден.")
            if func.__name__ in ['insert', 'select']:
                return []
            if func.__name__ in ['update', 'delete']:
                return args[0] if args else []
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            if func.__name__ == 'insert':
                return args[0] if args else []
            return None
    return wrapper

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция '{func.__name__}' выполнилась за {execution_time:.4f} секунд.")
        return result
    return wrapper

def confirm_action(action_name: str):
    # Декоратор должен ВСЕГДА возвращать функцию (wrapper)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if confirmation.lower() != 'y':
                print(f"Действие \"{action_name}\" отменено.")
                if func.__name__ in ['delete', 'update']:
                    return args[0]
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print(f"[CACHE HIT] Для ключа '{key}' взят закэшированный результат.")
            return cache[key]

        print(f"[CACHE MISS] Для ключа '{key}' вычисляем результат...")
        result = value_func()
        cache[key] = result
        return result

    return cache_result