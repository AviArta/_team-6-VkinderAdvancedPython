import psycopg2

from VK.VKinder import VKinder
from DB.BD_VK import create_table, drop_table_all

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


if __name__ == '__main__':
    with psycopg2.connect(database="bd_VKinder", user="postgres", password="VKinder_BD", host='185.246.67.169',
                          port='33835') as conn:
        drop_table_all(conn)
        create_table(conn)

        user_token = config_read()[0]
        group_token = config_read()[1]

        bot = VKinder(user_token, group_token, conn)
        bot.listen()
