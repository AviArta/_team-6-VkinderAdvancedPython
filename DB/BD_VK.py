import psycopg2


def create_table(conn):
    """
    Функция создания таблиц
    """
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Client
            (
                id_client SERIAL PRIMARY KEY,
                name VARCHAR(40),
                surname VARCHAR(40),
                city VARCHAR(40),
                age VARCHAR(40),
                id_vk_c INTEGER UNIQUE,
                gender VARCHAR(40)

            );
            """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Favorites(
                id_favorites SERIAL PRIMARY KEY,
                id_client_f INTEGER NOT NULL REFERENCES Client(id_client) ON DELETE CASCADE,
                name_f VARCHAR(40),
                surname_f VARCHAR(40),
                city_f VARCHAR(40),
                age_f VARCHAR(40),
                id_vk_f INTEGER UNIQUE,
                gender_f VARCHAR(40)
            );
            """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Blocked(
                id_blocked SERIAL PRIMARY KEY,
                id_client_b INTEGER NOT NULL REFERENCES Client(id_client),
                id_vk_b INTEGER UNIQUE

            );
            """)
        conn.commit()
    print("Таблицы созданы")


def insert_client(conn, name: str, surname: str, city: str, age: int, id_vk_c: int, gender: str):
    """
    Функция заполнения таблицы Пользователь.
    Функция принимает на вход данные о пользователе, исходя из его профиля ВК
    """
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO Client(name, surname, city, age, id_vk_c, gender)
                        VALUES('{name}', '{surname}', '{city}', '{age}', '{id_vk_c}', '{gender}') 
                        RETURNING id_client;""")

        conn.commit()
    print("Пользователь добавлен")


def insert_favorites(conn, id_client_f: int, name_f: str, surname_f: str, city_f: str, age_f: int,
                     id_vk_f: int, gender_f: str):
    """
    Функция заполнения таблицы Избранное
    Функция принимает на вход данные об "избранных", которых выберет пользователь, исходя из их профиля ВК
    """
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO Favorites(id_client_f, name_f, surname_f, city_f, age_f, id_vk_f, gender_f)
                        VALUES('{id_client_f}','{name_f}', '{surname_f}', '{city_f}', '{age_f}', '{id_vk_f}', 
                        '{gender_f}') RETURNING id_favorites;""")

        conn.commit()
    print("Добавлено в избранное")


def insert_blocked(conn, id_client_b: int, id_vk_b: int):
    """
    Функция заполнения таблицы ЧС
    Функция принимает на вход данные об "заблокированных", которых выберет пользователь, исходя из их профиля ВК
    """
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO Blocked(id_client_b, id_vk_b)
                        VALUES('{id_client_b}', '{id_vk_b}') RETURNING id_blocked;""")
        conn.commit()
    print("Добавлено в ЧС")


def search_count(conn, check: int):
    """
    Функция поиска актуального идентификатора пользователя при повторном вводе.
    Функция принимает на вход id ВК пользователя и возвращает id Пользователя в таблице,
    который был ранее ему присвоен.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_client FROM Client
                    WHERE id_vk_c ={check};
                """)
        return cur.fetchall()[-1][0]


def search_count_first(conn):
    """
    Функция поиска актуального идентификатора пользователя при первичном вводе
    Функция возвращает id Пользователя в таблице, который был ему присвоен.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_client FROM Client
                """)
        return cur.fetchall()[-1][0]


def drop_table_all(conn):
    """
    Функция удаления всех таблиц
    """
    with conn.cursor() as cur:
        cur.execute("""                    
            DROP TABLE Favorites;
            DROP TABLE Blocked;
            DROP TABLE Client;
            """)
        conn.commit()
    print("Таблицы удалены")


def delete_blocked(conn, id_vk_b: int):
    """
    Функция удаления человека из чс.
    Функция удаляет человека из ЧС, принимая на вход его id ВК
    """
    with conn.cursor() as cur:
        cur.execute("""
                       DELETE FROM Blocked WHERE id_vk_b=%s;
                       """, (id_vk_b,))

        conn.commit()
        print("Запись удалена")


def delete_favorites(conn, id_vk_f: int):
    """
    Функция удаления человека из избранного.
    Функция удаляет человека из избранного, принимая на вход его id ВК
    """
    with conn.cursor() as cur:
        cur.execute("""
                       DELETE FROM Favorites WHERE id_vk_f=%s;
                       """, (id_vk_f,))

        conn.commit()
        print("Запись удалена")


def result_favorites(conn, check: int):
    """
    Функция вывода избранных для текущего пользователя
    Функция принимает на вход id ВК пользователя и возвращает список избранных,
    которые соответствуют этому пользователю
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT name_f, surname_f, city_f, age_f, id_vk_f, gender_f FROM Favorites 
                JOIN Client ON  Client.id_client = id_client_f
                WHERE id_client_f =(SELECT id_client FROM Client WHERE id_vk_c = {check});
                    """)
        return cur.fetchall()


def result_blocked(conn, check: int):
    """
    Функция вывода чc для текущего пользователя
    Функция принимает на вход id ВК пользователя и возвращает список людей в ЧС,
    которые соответствуют этому пользователю
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_vk_b FROM Blocked 
                JOIN Client ON  Client.id_client = id_client_b
                WHERE id_client_b =(SELECT id_client FROM Client WHERE id_vk_c = {check});
                    """)
        result_list_b = []
        for res in cur.fetchall():
            result_list_b.append(res[-1])
        return result_list_b


def result_favorites_id(conn, check: int):
    """
    Функция вывода id VK избранных для текущего пользователя
    Функция принимает на вход id ВК пользователя и возвращает список id VK избранных,
    которые соответствуют этому пользователю. Нужна для отсекания повтора показа ранее избранных.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_vk_f FROM Favorites 
                JOIN Client ON  Client.id_client = id_client_f
                WHERE id_client_f =(SELECT id_client FROM Client WHERE id_vk_c = {check});
                    """)
        result_list_f = []
        for res in cur.fetchall():
            result_list_f.append(res[-1])
        return result_list_f


def result_favorites_blocked(conn, check):
    """
        Функция вывода id VK избранных и заблокированных для текущего пользователя
        Функция принимает на вход id ВК пользователя и возвращает список id VK избранны и заблокированных,
        которые соответствуют этому пользователю. Нужна для отсекания повтора показа ранее избранных и заблокированных.
        """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_vk_f FROM Favorites 
                JOIN Client ON  Client.id_client = id_client_f
                WHERE id_client_f =(SELECT id_client FROM Client WHERE id_vk_c = {check});
                    """)
        result_list_f = []
        for res in cur.fetchall():
            result_list_f.append(res[-1])

        cur.execute(f"""
                        SELECT id_vk_b FROM Blocked 
                        JOIN Client ON  Client.id_client = id_client_b
                        WHERE id_client_b =(SELECT id_client FROM Client WHERE id_vk_c = {check});
                            """)
        result_list_b = []
        for res in cur.fetchall():
            result_list_b.append(res[-1])
        result_list_fb = result_list_f + result_list_b
        print(result_list_fb)
        return result_list_fb


def result_favorites_first(conn):
    """
    Функция вывода избранных для пользователя, который воспользовался программой в первый раз
    Функция ищет всех людей в таблице избранные.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                    SELECT name_f, surname_f, city_f, age_f, id_vk_f, gender_f FROM Favorites 
                    """)
        return cur.fetchall()


def result_blocked_first(conn):
    """
    Функция вывода чc для пользователя, который воспользовался программой в первый раз
    Функция ищет всех людей в таблице чс.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_vk_b FROM Blocked 
                    """)
        result_list_bf = []
        for res in cur.fetchall():
            result_list_bf.append(res[-1])
        return result_list_bf


def check_client(conn, check: int):
    """
    Функция проверки нахождения пользователя в бд.
    Функция принимает на вход id пользователя в ВК и ищет соответствие ранее записанных id с введенным,
    возвращает список id.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
                SELECT id_vk_c FROM Client
                    WHERE id_vk_c ={check};
                """)
        return cur.fetchall()


def delete_favorites(conn, check: int):
    """
        Функция изменения города при повторном заходе и удаления записей из избранного с прежним городом.
        Функция принимает на вход id пользователя ВК и название нового города,
        производит замену названия города в таблице для пользователей и удаляет записи в таблице "избранное",
        которые были с прежним названием города.
        """
    with conn.cursor() as cur:
        cur.execute(f"""
                    DELETE FROM Favorites WHERE city_f IN (SELECT city_f FROM Favorites 
                    JOIN Client ON  Client.id_client = id_client_f
                    WHERE  id_vk_c = {check});
                     """)

        conn.commit()
        print("Клиенты прежнего города удалены")


def update_user_city(conn, check, city):
    with conn.cursor() as cur:
        cur.execute(f"""
                    UPDATE Client SET city=%s WHERE id_vk_c=%s;
                    """, (f"{city}", check))


def result_blocked_all(conn):
    """
    Функция вывода списка всех пользователей в ЧС.
    Функция возвращает список id ВК всех пользователей в ЧС
    """
    with conn.cursor() as cur:
        cur.execute("""
                       SELECT * FROM Blocked 
                       """)
        result_list_ba = []
        for res in cur.fetchall():
            result_list_ba.append(res[-1])
        return result_list_ba
