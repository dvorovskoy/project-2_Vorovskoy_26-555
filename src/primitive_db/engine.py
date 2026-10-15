# src/primitive_db/engine.py
# Используем обычный split для максимальной надежности на Windows
from . import core, utils, parser
from prettytable import PrettyTable

def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("<command> insert into <имя_таблицы> values (<знач1>, <знач2>...) - добавить запись")
    print("<command> select from <имя_таблицы> [where <столбец> = <значение>] - прочитать")
    print("<command> update <имя_таблицы> set <столбец> = <значение> where <ст> = <зн> - обновить")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить")
    print("<command> info <имя_таблицы> - инфо о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def _print_select_result(data: list):
    if not data:
        print("(нет данных)")
        return
    pt = PrettyTable()
    pt.field_names = data[0].keys()
    for row in data:
        pt.add_row(row.values())
    print(pt)

def run():
    print("***База данных***")
    print_help()

    while True:
        metadata = utils.load_metadata()
        user_input = input(">>>Введите команду: ")

        if not user_input.strip():
            continue

        # САМЫЙ ПРОСТОЙ СПЛИТ. Никаких умных кавычек.
        args = user_input.split()

        if not args:
            continue

        cmd = args[0]

        if cmd == "exit":
            break
        elif cmd == "help":
            print_help()
        elif cmd == "list_tables":
            core.list_tables(metadata)

        elif cmd == "create_table":
            if len(args) < 2:
                print("Ошибка: укажите имя таблицы.")
                continue
            metadata = core.create_table(metadata, args[1], args[2:])
            if args[1] in metadata:
                utils.save_metadata(metadata)
        elif cmd == "drop_table":
            if len(args) != 2:
                print("Ошибка: укажите имя таблицы.")
                continue
            metadata = core.drop_table(metadata, args[1])

        elif cmd == "insert":
            if len(args) < 4 or args[1] != "into" or args[2] not in metadata or args[3] != "values":
                print("Ошибка: синтаксис -> insert into <table> values (...)")
                continue

            table_name = args[2]

            # Берем всё, что идет после слова "values"
            values_parts = args[4:]

            # Если это одна строка в скобках: ("Test", 1)
            if len(values_parts) == 1 and values_parts[0].startswith("(") and values_parts[0].endswith(")"):
                # Убираем скобки и разбиваем по запятой
                inner = values_parts[0][1:-1]
                raw_values = [v.strip() for v in inner.split(',')]
            else:
                # Если это отдельные слова: "Test" 1
                raw_values = values_parts

            # Финальная очистка от кавычек
            clean_values = []
            for v in raw_values:
                v = v.strip('()')
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                elif v.startswith("'") and v.endswith("'"):
                    v = v[1:-1]
                clean_values.append(v)

            schema = metadata[table_name]["columns"]
            expected_count = len(schema) - 1

            if len(clean_values) != expected_count:
                print(f"Ошибка: Ожидалось {expected_count} значений, получено {len(clean_values)}.")
                continue

            utils.save_table_data(table_name, core.insert(metadata, table_name, clean_values))

        elif cmd == "select":
            if len(args) < 3 or args[1] != "from" or args[2] not in metadata:
                print("Ошибка: синтаксис -> select from <table> [where ...]")
                continue

            table_name = args[2]
            table_data = utils.load_table_data(table_name)

            where_clause = {}
            if len(args) > 3 and args[3] == "where":
                where_parts = args[4:]
                where_str = " ".join(where_parts)
                where_clause = parser.parse_where(where_str)

            result = core.select(table_data, where_clause)
            _print_select_result(result)

        elif cmd == "update":
            if len(args) < 6 or args[3] != "set" or "where" not in args:
                print("Ошибка: синтаксис -> update <table> set <col> = <val> where ...")
                continue

            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            set_str = args[4]
            where_index = args.index("where")
            where_str = " ".join(args[where_index+1:])

            set_clause = parser.parse_set(set_str)
            where_clause = parser.parse_where(where_str)

            table_data = utils.load_table_data(table_name)
            updated_data = core.update(table_data, set_clause, where_clause)
            if updated_data is not None and updated_data != table_data:
                utils.save_table_data(table_name, updated_data)

        elif cmd == "delete":
            if len(args) < 5 or args[1] != "from" or args[3] != "where" or args[2] not in metadata:
                print("Ошибка: синтаксис -> delete from <table> where ...")
                continue

            table_name = args[2]
            where_str = " ".join(args[4:])
            where_clause = parser.parse_where(where_str)

            table_data = utils.load_table_data(table_name)
            updated_data = core.delete(table_data, where_clause)
            if updated_data is not None and updated_data != table_data:
                utils.save_table_data(table_name, updated_data)

        elif cmd == "info":
            if len(args) != 2 or args[1] not in metadata:
                print("Ошибка: info <table_name>")
                continue
            tbl = metadata[args[1]]
            cols = ", ".join([f"{k}:{v}" for k, v in tbl["columns"].items()])
            count = len(utils.load_table_data(args[1]))
            print(f"Таблица: {args[1]}")
            print(f"Столбцы: {cols}")
            print(f"Количество записей: {count}")

        else:
            print(f"Функции {cmd} нет. Попробуйте снова.")