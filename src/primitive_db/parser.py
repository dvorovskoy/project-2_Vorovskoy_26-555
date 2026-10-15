import shlex

def parse_where(where_str: str) -> dict:
    """Превращает 'age = 28' в {'age': 28}"""
    if not where_str:
        return {}


    if "=" not in where_str:
        print("Ошибка: условие where должно содержать '='")
        return {}

    col, val = where_str.split("=", 1)
    col = col.strip()
    val = val.strip()


    if val.startswith('"') and val.endswith('"'):
        return {col: val[1:-1]}
    elif val.lower() in ("true", "false"):
        return {col: val.lower() == "true"}
    else:
        try:
            return {col: int(val)}
        except ValueError:
            return {col: val}

def parse_values(values_str: str) -> list:
    """Превращает '("Sergei", 28, true)' в ['Sergei', 28, True]"""
    if not values_str:
        return []

    args = shlex.split(values_str)
    if not args:
        return []

    # Если пользователь обернул в скобки, убираем их
    raw = args[0]
    if raw.startswith("(") and raw.endswith(")"):
        raw = raw[1:-1]
        args = shlex.split(raw)

    result = []
    for item in args:
        if item.startswith('"') and item.endswith('"'):
            result.append(item[1:-1])
        elif item.lower() == "true":
            result.append(True)
        elif item.lower() == "false":
            result.append(False)
        else:
            try:
                result.append(int(item))
            except ValueError:
                result.append(item)
    return result

def parse_set(set_str: str) -> dict:
    """Превращает 'age = 29' в {'age': 29}"""
    return parse_where(set_str)