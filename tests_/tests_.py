import pytest
import psycopg2

from VK.VKUser import VkUser

# блок тестирования методов класса VkUser:
fixture_get_user_info = [
    (132793779, ('Екатерина', 'Игнатова', 28, 'Москва', 'не указано', 1)),
    (22043492, ('Наталия', 'Кулемина', 26, 'Москва', 'не указано', 1)),
    (44445447, ('Anna', 'Kozlova', 'не указан', 'Москва', 'не указано', 1))
]
@pytest.mark.parametrize('user_id, right_result', fixture_get_user_info)
def test_get_user_info(user_id, right_result):
    with psycopg2.connect(database="bd_VKinder", user="postgres", password="VKinder_BD", host='185.246.67.169',
                          port='33835') as conn:
        vk_user = VkUser(user_id, conn)
        function_result = vk_user.get_user_info(user_id)
        assert function_result == right_result
        assert isinstance(function_result, tuple)


fixture_get_likes_most_popular_photos = [(132793779, [88, 79, 71, 60, 40, 40, 39, 39, 36, 36, 34, 33, 33, 30, 30, 29,
                                                     28, 27, 25, 25, 23, 23, 21, 20, 19, 17, 17, 10]),
                                         (22043492, [106, 94, 89, 65, 62, 61, 59, 54, 50, 48, 45, 43, 42, 37, 35, 15]),
                                         (1330394, [])
                                        ]
@pytest.mark.parametrize('owner_id, right_result', fixture_get_likes_most_popular_photos)
def test_get_likes_most_popular_photos(owner_id, right_result):
    with psycopg2.connect(database="bd_VKinder", user="postgres", password="VKinder_BD", host='185.246.67.169',
                          port='33835') as conn:
        vk_user = VkUser(owner_id, conn)
        function_result = vk_user.get_likes_most_popular_photos(owner_id)
        assert function_result == right_result
        assert isinstance(function_result, list)


fixture_check_is_сlosed = [(132793779, False),
                                        (4177627, True),
                                        (687864146, True)]
@pytest.mark.parametrize('user_id, right_result', fixture_check_is_сlosed)
def test_check_is_сlosed(user_id, right_result):
    with psycopg2.connect(database="bd_VKinder", user="postgres", password="VKinder_BD", host='185.246.67.169',
                          port='33835') as conn:
        vk_user = VkUser(user_id, conn)
        function_result = vk_user.check_is_сlosed(user_id)
        assert function_result == right_result
        assert isinstance(function_result, bool)


fixture_check_in_favorites_blocked = [(132793779, True),
                                        (22043492, True),
                                        (1330394, True)]
@pytest.mark.parametrize('user_id, right_result', fixture_check_in_favorites_blocked)
def test_check_in_favorites_blocked(user_id, right_result):
    with psycopg2.connect(database="bd_VKinder", user="postgres", password="VKinder_BD", host='185.246.67.169',
                          port='33835') as conn:
        vk_user = VkUser(132793779, conn)
        function_result = vk_user.check_in_favorites_blocked(user_id)
        assert function_result == right_result
        assert isinstance(function_result, bool)

# блок тестирования методов класса VKinder: