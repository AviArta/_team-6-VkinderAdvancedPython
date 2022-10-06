from random import randrange

import vk_api
from vk_api import keyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from VK.VKUser import config_read, VkUser
from DB.BD_VK import insert_client, insert_blocked, insert_favorites, check_client, search_count, \
    result_favorites, delete_favorites, update_user_city


class VKinder:
    '''
        Класс для представления бота в VK.
        ...
        Атрибуты
        --------
        conn - соединение с базой данных
        user_vk - авторизованный по ключу доступа пользователя
        public_vk - авторизованный по ключу сообщества

        Методы
        ------
        write_msg(self, user_id, message, keyboard=None):
            Отправка сообщения пользователю.
        send_photos(self, user_id, likes, owner_id, first_name, age, keyboard):
            Отправка фото подходящего человека пользователю.
        wait_message(self, longpoll):
            Проверка сообщений, которые пришли боту.
        bot_keyboard(self):
            Создание кнопок в диалоге с пользователем.
        photos(self, event, db_client_id, user, suitable, counter, user_city):
            Отправка данных подходящего человека пользователю.
        search_peoples(self, event, longpoll, offset, user_city):
            Доп. метод для поиска подходящих профилей
        listen(self, city):
            Метод отвечает за работу бота.
        '''

    def __init__(self, user_token: str, public_token: str, conn):
        self.user_token = user_token
        self.public_token = public_token
        self.user_vk = vk_api.VkApi(token=self.user_token)
        self.public_vk = vk_api.VkApi(token=self.public_token)
        self.conn = conn

    def write_msg(self, user_id, message, keyboard=None):
        """Метод для отправки сообщения пользователю. """
        self.public_vk.get_api().messages.send(
            user_id=user_id,
            message=message,
            random_id=randrange(10 ** 7),
            keyboard=keyboard)

    def send_photos(self, user_id, likes, owner_id: int, first_name, age, keyboard=None):
        """
            Метод, выполняющий отправку фото подходящего человека пользователю. Используется только в связке
        с другими функциями.
        """
        photos = self.user_vk.get_api().photos.get(owner_id=owner_id,
                                                   album_id='profile',
                                                   extended=1, rev=0)

        id_photos = []
        for photo in photos['items']:
            if photo['likes']['count'] in likes:
                id_photos.append(photo['id'])
        # Создание строки с фотографиями
        if len(id_photos) == 2:
            photos = f"photo{owner_id}_{id_photos[0]},photo{owner_id}_{id_photos[1]}"
        elif len(id_photos) == 1:
            photos = f"photo{owner_id}_{id_photos[0]}"
        else:
            photos = f"photo{owner_id}_{id_photos[0]},photo{owner_id}_{id_photos[1]},photo{owner_id}_{id_photos[2]}"
        response = self.public_vk.get_api().messages.send(
            user_id=user_id,
            message=f'{first_name}, {age}',
            attachment=photos,
            random_id=randrange(0, 100 ** 10000),
            keyboard=keyboard.get_keyboard())
        return response

    def wait_message(self, longpoll):
        """Данная повторяющаяся конструкция ждёт сообщение которое пришло именно боту."""
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    return request, event.user_id

    def bot_keyboard(self):
        """ Метод создания кнопок в диалоге с пользователем. """
        rate = keyboard.VkKeyboard(one_time=True)
        rate.add_button(label='❤', color=keyboard.VkKeyboardColor.NEGATIVE)
        rate.add_button(label='👎🏻', color=keyboard.VkKeyboardColor.PRIMARY)
        rate.add_line()
        rate.add_button(label='Остановить поиск', color=keyboard.VkKeyboardColor.SECONDARY)

        start_search = keyboard.VkKeyboard(one_time=True)
        start_search.add_button(label='Поиск', color=keyboard.VkKeyboardColor.POSITIVE)

        next_people_button = keyboard.VkKeyboard(one_time=True)
        next_people_button.add_button(label='Смотреть следующих.')
        next_people_button.add_button(label='Остановить поиск', color=keyboard.VkKeyboardColor.SECONDARY)
        return rate, start_search, next_people_button

    def photos(self, user_id, db_client_id, user, suitable, counter: int, user_city):
        """
            Метод по отправке данных подходящего человека. Используется в связке с функцией listen.
        В функции используется несколько рекурсий, без них бот перестаёт обрабатывать сообщения, каждая рекурсия функции,
        новый человек.
        """
        print('yes')
        rate, start_search, next_people_button = self.bot_keyboard()
        longpoll = VkLongPoll(self.public_vk)
        if not user.enumeration_ids(counter=counter, suitable=suitable) is None:
            try:
                owner_id, first_name, last_name, age, sex, city, counter = user.enumeration_ids(counter=counter,
                                                                                                suitable=suitable)
            except ValueError:
                self.write_msg(user_id, 'Вы просмотрели весь список подходящих. Хотите увидеть следующий?',
                               keyboard=next_people_button.get_keyboard())
                request, user_id = self.wait_message(longpoll)
                if request == 'Смотреть следующих.':
                    self.search_peoples(user_id, longpoll, 300, user_city)
                elif request == 'Остановить поиск':
                    self.listen()
        else:
            try:
                owner_id, first_name, last_name, age, city, sex, counter = user.enumeration_ids(counter=counter + 1,
                                                                                                suitable=suitable)
            except ValueError:
                self.write_msg(user_id,
                               '''Вы просмотрели весь первый список подходящих. Хотите увидеть следующий?''',
                               keyboard=next_people_button.get_keyboard())
                request, user_id = self.wait_message(longpoll).strip()
                if request == 'Смотреть следующих.':
                    self.search_peoples(user_id, longpoll, 300, user_city)
                elif request == 'Остановить поиск':
                    self.listen()
        likes = user.get_likes_most_popular_photos(owner_id)[:3]
        self.send_photos(user_id, likes, owner_id, first_name, age, rate)
        request, user_id = self.wait_message(longpoll)
        if request.strip() == 'Остановить поиск':
            self.write_msg(user_id,
                           '''Поиск остановлен.''')
            self.write_msg(user_id,
                           '''Хотите увидеть людей выбранных вами?. \n1. Да\n2. Нет''')
            choice, user_id = self.wait_message(longpoll)
            if choice.strip().lower() in ['1', 'да']:
                favorites = result_favorites(self.conn, user_id)
                text = ''
                for favorite in favorites:
                    text += f'{favorite[0]}, {favorite[3]} - https://vk.com/id{favorite[4]}\n'
                self.write_msg(user_id,
                               f'Люди выбранные вами.\n\n{text}')
            delete_favorites(self.conn, user_id)
            self.write_msg(user_id,
                           '''Для повторного поиска введите команду "Поиск" или нажмите на кнопку.''',
                           keyboard=start_search.get_keyboard())
            self.listen()
        elif request.strip() == '❤':
            insert_favorites(self.conn, db_client_id, first_name, last_name, city, age, owner_id, sex)

            self.write_msg(user_id, f'[id{owner_id}|Для дальнейшего общения нажимай на меня &#9995;]')
            self.photos(user_id=user_id, db_client_id=db_client_id, user=user, suitable=suitable, counter=counter,
                        user_city=user_city)
        elif request.strip() == '👎🏻':
            insert_blocked(self.conn, db_client_id, owner_id)
            self.photos(user_id=user_id, db_client_id=db_client_id, user=user, suitable=suitable, counter=counter,
                        user_city=user_city)
        else:
            self.write_msg(user_id, "Не понял вашего ответа...")


    def search_peoples(self, user_id, longpoll, offset=0, user_city=None):
        """
        Метод для поиска подходящих людей,
        выведен в отдельный метод для того чтобы была возможность использовать в рекурсии,
        и при остановке поиска или просмотра всех загруженных подходящих не требовалось начинать с самого начала логики бота

        user_city - параметр которая указывается при рекурсии,
        suitable - список словарей, в котором находятся подходящие, далее делаем по нему цикл.
        """
        user_id = user_id
        user = VkUser(user_id, self.conn)
        f_name, l_name, age, city, relation, sex = user.get_user_info(user_id)
        if user_city is not None:  # Проверка первый раз вызвана или рекурсивно.
            city = user_city
        if city is None:
            self.write_msg(user_id,
                           f"{f_name}, введите город &#127970;")
            city, user_id = self.wait_message(longpoll)
        else:
            if user_city is None:
                self.write_msg(user_id,
                               f'{f_name}, \nВаш город - "{city}". \nИщем по нему?\n1. Да\n2. Нет')
                choice, user_id = self.wait_message(longpoll)
                if choice.strip() == '2' or choice.strip().lower() == 'нет':
                    self.write_msg(user_id,
                                   f"{f_name}, введите город &#127970;")
                    city, user_id = self.wait_message(longpoll)

        if len(check_client(self.conn, user_id)) == 0:
            insert_client(self.conn, f_name, l_name, city, age, user_id, sex)
        else:
            update_user_city(self.conn, user_id, city)
        client_id = search_count(self.conn, user_id)
        self.write_msg(user_id,
                       f"{f_name}, ваши подходящие:")

        suitable = user.search_users_by_city_sex(city, sex, offset)
        print(suitable)
        for client in suitable:

            self.photos(user_id=user_id, db_client_id=client_id, user=user, suitable=suitable, counter=0, user_city=city)

    def listen(self):
        """Начало логики бота.
        Тут создаем LongPoll соединение и получаем ответы в реальном времени.
        Первое условие реализовано больше для пользователей которые зашли впервые, у них будет кнопка Start & Начать,
        Второе условие отвечает за поиск людей."""
        longpoll = VkLongPoll(self.public_vk)
        start_search = keyboard.VkKeyboard(one_time=True)
        start_search.add_button(label='Поиск', color=keyboard.VkKeyboardColor.POSITIVE)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    if request.lower().strip() in ['start', 'начать']:
                        self.write_msg(event.user_id, '''Здравствуйте, для поиска людей нажмите на кнопку.''',
                                       keyboard=start_search.get_keyboard())
                    elif request.lower().strip() == "поиск":
                        self.search_peoples(event.user_id, longpoll)

                    elif request.strip().lower() == "пока":
                        self.write_msg(event.user_id, "Пока :(")
                    else:
                        self.write_msg(event.user_id, "Не понял вашего ответа...")