import pytest
import BD_VK_for_test
from BD_VK_for_test import search_count, search_count_first, result_favorites, result_blocked, result_favorites_id, \
    result_favorites_blocked, result_favorites_first, result_blocked_first, check_client, result_blocked_all, \
    conn, create_table, insert_client, insert_favorites, insert_blocked, drop_table_all, delete_blocked, \
    delete_favorites, update_city_delete_favorites
from parameterized import parameterized

"""
Тест для "BD_VK_for_test". Так как все функции связаны с работой с базой данных, нужно создавать таблицы. 
Рекомендуется, если вы уже проводили тест, начать с удаления таблиц. При первом запуске, начинать сразу с создания
таблиц. BD_VK_for_test не обрабатывает исключения, так как работает в связке с другими модулями, входные данные с 
которых всегда предсказуемы.
 
"""





"""
Проверка функции удаления таблиц
"""
fixture = [
    (True)
]


@pytest.mark.parametrize("result", fixture)
def test_drop_table_all(result):
    drop_table_all_result = drop_table_all(conn)
    assert drop_table_all_result == result


"""
Проверка функции создания таблиц
"""
fixture1 = [
    (True)
]


@pytest.mark.parametrize("result", fixture1)
def test_create_table(result):
    create_table_result = create_table(conn)
    assert create_table_result == result


"""
Проверка функции заполнения таблицы "Пользователь"
"""

fixture2 = [
    ("Вася", "Пупкин", "Смоленск", 23, 1, "муж", True),
    ("Петя", "Васин", "Звенигород", 25, 2, "муж", True),
    ("Люда", "Ильина", "Кемерово", 19, 3, "жен", True),
]


@pytest.mark.parametrize("name, surname, city, age, id_vk_c, gender, result", fixture2)
def test_insert_client(name, surname, city, age, id_vk_c, gender, result):
    insert_client_result = insert_client(conn, name, surname, city, age, id_vk_c, gender)
    assert insert_client_result == result


"""
Проверка функции заполнения таблицы "Избранное"
"""

fixture3 = [
    (1, "Даша", "Иванова", "Смоленск", 23, 1, "жен", True),
    (1, "Света", "Васина", "Смоленск", 21, 2, "жен", True),
    (2, "Саша", "Васильев", "Кемерово", 19, 3, "муж", True),
    (3, "Денис", "Петров", "Сочи", 24, 4, "муж", True),
]


@pytest.mark.parametrize("id_client_f, name_f, surname_f, city_f, age_f, id_vk_f, gender_f, result", fixture3)
def test_insert_favorites(id_client_f, name_f, surname_f, city_f, age_f, id_vk_f, gender_f, result):
    insert_favorites_result = insert_favorites(conn, id_client_f, name_f, surname_f, city_f, age_f, id_vk_f, gender_f)
    assert insert_favorites_result == result


"""
Проверка функции заполнения таблицы "Заблокированные"
"""

fixture4 = [
    (1, 1, True),
    (2, 2, True),
    (2, 3, True),
    (3, 4, True),
]


@pytest.mark.parametrize("id_client_b, id_vk_b, result", fixture4)
def test_insert_blocked(id_client_b, id_vk_b, result):
    insert_blocked_result = insert_blocked(conn, id_client_b, id_vk_b)
    assert insert_blocked_result == result


"""
Проверка функции поиска актуального идентификатора пользователя при повторном вводе.
"""

fixture5 = [
    (1, 1),
    (2, 2),
    (3, 3),
]


@pytest.mark.parametrize("check, result", fixture5)
def test_search_count(check, result):
    search_count_result = search_count(conn, check)
    assert search_count_result == result


"""
Проверка функции удаления человека из чс.
"""
fixture6 = [
    (1, True)
]


@pytest.mark.parametrize("id_vk_b, result", fixture6)
def test_delete_blocked(id_vk_b, result):
    delete_blocked_result = delete_blocked(conn, id_vk_b)
    assert delete_blocked_result == result


"""
Проверка функции удаления человека из избранного.
"""
fixture7 = [
    (3, True)
]


@pytest.mark.parametrize("id_vk_f, result", fixture7)
def test_delete_favorites(id_vk_f, result):
    delete_favorites_result = delete_favorites(conn, id_vk_f)
    assert delete_favorites_result == result


"""
Проверка функции вывода избранных для текущего пользователя
"""
fixture9 = [
    (3, [("Денис", "Петров", "Сочи", "24", 4, "муж")])
]


@pytest.mark.parametrize("check, result", fixture9)
def test_result_favorites(check, result):
    result_favorites_result = result_favorites(conn, check)
    assert result_favorites_result == result


"""
Проверка функции вывода чc для текущего пользователя
"""
fixture10 = [
    (2, [2, 3])
]


@pytest.mark.parametrize("check, result", fixture10)
def test_result_blocked(check, result):
    result_blocked_result = result_blocked(conn, check)
    assert result_blocked_result == result


"""
Проверка функции вывода id VK избранных для текущего пользователя
"""
fixture11 = [
    (1, [1, 2])
]


@pytest.mark.parametrize("check, result", fixture11)
def test_result_favorites_id(check, result):
    result_favorites_id_result = result_favorites_id(conn, check)
    assert result_favorites_id_result == result


"""
Проверка функции вывода id VK избранных и заблокированных для текущего пользователя
"""
fixture12 = [
    (3, [4, 4])
]


@pytest.mark.parametrize("check, result", fixture12)
def test_result_favorites_blocked(check, result):
    result_favorites_blocked_result = result_favorites_blocked(conn, check)
    assert result_favorites_blocked_result == result


"""
Проверка функции проверки нахождения пользователя в бд
"""
fixture13 = [
    (3, [(3,)])
]


@pytest.mark.parametrize("check, result", fixture13)
def test_check_client(check, result):
    check_client_result = check_client(conn, check)
    assert check_client_result == result


"""
Проверка функции изменения города при повторном заходе и удаления записей из избранного с прежним городом
"""
fixture14 = [
    (1, "Ярославль", True)
]


@pytest.mark.parametrize("check, city_new, result", fixture14)
def test_update_city_delete_favorites(check, city_new, result):
    update_city_delete_favorites_result = update_city_delete_favorites(conn, check, city_new)
    assert update_city_delete_favorites_result == result


"""
Проверка функции вывода списка всех пользователей в ЧС
"""
fixture15 = [
    ([2, 3, 4])
]


@pytest.mark.parametrize(" result", fixture15)
def test_result_blocked_all(result):
    result_blocked_all_result = result_blocked_all(conn)
    assert result_blocked_all_result == result
