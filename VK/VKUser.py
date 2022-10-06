import json
from datetime import datetime
import psycopg2

import requests
import vk_api
from fake_headers import Headers
from DB.BD_VK import result_favorites_blocked


def config_read():
    '''
        Функция читает необходимые токены из файла для использования в коде. Предназначена для соблюдения мер
    безопасности по использованию персональных данных. Результатом выполнения функции являются переменные,
    в которых хранятся ключи доступа для использования VK_API: ключ доступа пользователя и ключ доступа сообщества.
    '''
    file_name = 'all_tokens.config'
    contents = open(file_name).read()
    config = eval(contents)
    vk_user_token = config['vk_user_token']
    vk_group_token = config['vk_group_token']
    return vk_user_token, vk_group_token


class VkUser:
    '''
    Класс для представления пользователя в VK.
    ...
    Атрибуты
    --------
    user_id - id пользователя
    conn - соединение с базой данных
    user_vk - авторизованный по ключу доступа пользователя
    public_vk - авторизованный по ключу сообщества
    url - общая часть url для всех методов
    params - общая часть параметров для всех методов

    Методы
    ------
    get_user_info(self, user_i):
        Поиск информации по id пользователя.
    check_is_сlosed(self, user_id):
        Проверка на закрытый доступ к аккаунту (для тестирования).
    check_in_favorites_blocked(self, user_id):
        Проверка на нахождение профиля в списке, непонравившихся ранее (для тестирования).
    search_users_by_city_sex(self, user_city, user_sex, offset):
        Поиск профилей, по параметрам подходящих пользователю.
    dump_json(self):
        Запись в файл.
    get_likes_most_popular_photos(self, owner_id):
        Определение самых популярных фото в профиле.
    enumeration_ids(self, counter, suitable):
        Поиск в списке подходящих профилей именно тех, у кого есть необходимые фото.
    '''

    url = 'https://api.vk.com/method/'

    def __init__(self, user_id, conn):
        self.user_id = user_id
        self.conn = conn
        vk_user_token = config_read()[0]
        self.user_vk = vk_api.VkApi(token=vk_user_token)
        version = '5.131'
        self.params = {'access_token': vk_user_token, 'v': version}
        self.headers = Headers(
            os='win'
        ).generate()
    def get_user_info(self, user_id: int) -> tuple:
        '''
            Метод на вход при вызове требует параметр id и возвращает информацию с основными данными для записи в базу данных:
        id, имя и фамилию, город, пол, возраст и указанный вид отношений. Учтены варианты, если какое-либо из полей
        не указаны пользователем.
        '''
        method_url = 'users.get'
        URL = self.url + method_url
        method_params = {'user_ids': user_id,
                         'fields': 'city, sex, bdate, relation'}
        PARAMS = {**self.params, **method_params}
        response = requests.get(URL, params=PARAMS, headers=self.headers).json()

        try:
            user_sex = response['response'][0]['sex']
        except KeyError:
            user_sex = 'не указан'

        try:
            user_city = response['response'][0]['city']['title']
        except KeyError:
            user_city = None

        try:
            relation = response['response'][0]['relation']
            if relation == 0:
                user_relation = 'не указано'
            elif user_sex == 1 or user_sex == 2:
                if relation == 1:
                    if user_sex == 1:
                        user_relation = 'не замужем'
                    elif user_sex == 2:
                        user_relation = 'не женат'
                elif relation == 2:
                    if user_sex == 1:
                        user_relation = 'есть друг'
                    elif user_sex == 2:
                        user_relation = 'есть подруга'
                elif relation == 3:
                    if user_sex == 1:
                        user_relation = 'помолвлена'
                    elif user_sex == 2:
                        user_relation = 'помолвлен'
                elif relation == 4:
                    if user_sex == 1:
                        user_relation = 'замужем'
                    elif user_sex == 2:
                        user_relation = 'женат'
                elif relation == 5:
                    user_relation = 'всё сложно'
                elif relation == 6:
                    user_relation = 'в активном поиске'
                elif relation == 7:
                    if user_sex == 1:
                        user_relation = 'влюблена'
                    elif user_sex == 2:
                        user_relation = 'влюблён'
                elif relation == 8:
                    user_relation = 'в гражданском браке'
        except KeyError:
            user_relation = 'не указано'

        first_name = response['response'][0]['first_name']
        last_name = response['response'][0]['last_name']

        # определение возраста:
        try:
            bdata = response['response'][0]['bdate'][-4:]
        except KeyError:
            bdata = 'не указан'
        if bdata.isdigit() and (bdata[0:2] == '19' or bdata[0:2] == '20'):
            age = datetime.now().year - int(response['response'][0]['bdate'][-4:])
        else:
            age = 'не указан'

        return first_name, last_name, age, user_city, user_relation, user_sex

    def check_is_сlosed(self, user_id):
        '''
            Метод на вход при вызове требует параметр id и возвращает True - если профиль закрыт, False - если профиль
        с открытым доступом. Данный функционал выделен в отдельный метод для проведения тестирования.
        '''
        method_url = 'users.get'
        URL = self.url + method_url
        method_params = {'user_ids': user_id,
                         'fields': 'is_closed'}
        PARAMS = {**self.params, **method_params}
        response = requests.get(URL, params=PARAMS).json()
        if response['response'][0]['is_closed'] is False:
            return False
        else:
            return True

    def check_in_favorites_blocked(self, user_id):
        '''
            Метод при вызове на вход требует параметр id и возвращает True - если данный профиль не находится в таблице с
        профидями, которые были ранее отмечены пользователем, как непонравившиеся, False - если профиль с открытым
        доступом. Данный функционал выделен в отдельный метод для проведения тестирования.
        '''
        if not user_id in result_favorites_blocked(self.conn, self.user_id):
            return True
        else:
            return False

    def search_users_by_city_sex(self, user_city: str, user_sex: int, offset) -> list:
        '''
            Метод принимает город пользователя и его пол в качестве параметров (эти параметры получает из функции
        get_inf_from_user_id) и возвращает данные профилей VK, которые подходят пользователю: id VK, имя и фамилия,
        пол, город проживания и возраст.
            Дополнительно в запросе учитываются следующие параметры: необходимое количество результатов вывода (count),
        сортировка по популярности (sort), диапазон возраста (age_from, age_to) наличие фотографий (has_photo),
        статус (status) "не женат (не замужем)" или "в активном поиске", а также дата рождения (bdate).
            Значение возраста определяется путём проверки последних 4-х элементов строки даты рождения: если
        строка состоит только из цифр, при этом начинается либо с 19.., либо с 20.. - возраст получаем путём разности
        2022(текущего года) и последних 4-х элементов строки даты рождения, перевелённых в тип данных int.
        Иначе в значении указываем, что возраст не задан.
        '''
        method_url = 'users.search'
        URL = self.url + method_url
        param_sex = 0
        if user_sex == 1:
            param_sex = 2
        elif user_sex == 2:
            param_sex = 1
        param_status = 1 or 6
        method_params = {'count': 200, 'hometown': user_city, 'sort': 0, 'age_from': 20, 'age_to': 50, 'sex': param_sex,
                         'has_photo': 1, 'status': param_status, 'offset': offset, 'fields': 'city, sex, bdate, relation,'
                        'domain'}
        PARAMS = {**self.params, **method_params}
        response = requests.get(URL, params=PARAMS, headers=self.headers).json()
        result_users_list = []

        for user in response['response']['items']:

            try:
                if user['is_closed'] is False and not user['id'] in result_favorites_blocked(self.conn, self.user_id):
                    if user['city']['title'] == user_city:
                        result_users_dict = {}
                        result_users_dict['id'] = user['id']
                        result_users_dict['first_name'] = user['first_name']
                        result_users_dict['last_name'] = user['last_name']
                        result_users_dict['city'] = user['city']['title']
                        if user['sex'] == 1:
                            user_sex_name = 'жен'
                        elif user['sex'] == 2:
                            user_sex_name = 'муж'
                        result_users_dict['sex'] = user_sex_name

                        try:
                            bdata = user['bdate'][-4:]
                            if bdata.isdigit() and (bdata[0:2] == '19' or bdata[0:2] == '20'):
                                result_users_dict['age'] = datetime.now().year - int(user['bdate'][-4:])
                        except KeyError:
                            result_users_dict['age'] = 'не указан'

                        result_users_dict['link'] = 'https://vk.com/' + user['domain']
                        result_users_list.append(result_users_dict)
            except KeyError:
                continue

        return result_users_list

    def dump_json(self):
        '''
            Метод записи в файл выполняет запись результирующего списка в указанный файл формата json и
        возвращает подтверждение записи. В итоговой версии программы не используется, оставлена для выполнения
        проверок и локальных задач, которые могут возникнуть при расширении функционала программы.
        '''
        with open('../data_search_users.json') as result_file:

            data = self.search_users_by_city_sex(user_city=self.get_user_info(self.user_id)['user_city'],
                                                 user_sex=self.get_user_info(self.user_id)['user_sex'])

            with open('../data_search_users.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                print('Запись в файл прошла успешно.')

    def get_likes_most_popular_photos(self, owner_id: int) -> list:
        '''
            Мотод получает самые популярные фотографии пользователя по номеру id, который получен результатом метода
        поиска подходящих вариантов.
        '''
        response = self.user_vk.get_api().photos.get(
                                                    owner_id=owner_id,
                                                    album_id='profile',
                                                    extended=1)

        photo_ids = []
        for photo in response['items']:
            photo_ids.append(photo['likes']['count'])

        return sorted(photo_ids, reverse=True)

    def enumeration_ids(self, counter: int, suitable):
        '''
            Метод выполняет получение данных по подходящим пользователю профилям. Если у подходящего нет нужных фото,
        то ищем по следующему, пока не найдем. На вход принимает счётчик для рекурсии, и список словарей с подходящими.
        Выводит данные по подходящему профилю.
        '''
        try:
            if self.get_likes_most_popular_photos(suitable[counter]['id']) != []:
                print(suitable[counter])
                return suitable[counter]['id'], suitable[counter]['first_name'], \
                       suitable[counter]['last_name'], suitable[counter]['age'], \
                       suitable[counter]['city'], suitable[counter]['sex'], \
                       counter + 1

            else:
                counter += 1
                self.enumeration_ids(counter, suitable)
        except IndexError:
            return 'IndexError'


