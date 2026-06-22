import sqlite3
import sys
import configparser
import json
import datetime
import logging
from lsc_types import *

LOG_FILE = 'logging.log'


def dict_to_json(data, filename='data.json'):
    '''Функция записывает словарь в json-файл'''
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_all_data(default_file='default.json', data_file='data.json') -> dict:
    '''Возвращает словарь из двух файлов\n
    Берет данные по умолчанию из файла default-file\n
    Данные конкретной карты из файла data_file\n
    По-умолчанию файлы default.json и data.json\n
    '''
    data = {}
    with open(default_file, 'r', encoding='utf-8') as file:
        data.update(json.load(file))
    with open(data_file, 'r', encoding='utf-8') as file:
        data.update(json.load(file))
    return data

def touppercase(data: dict) -> dict:
    '''Возвращает словарь с приведенными к верхнему регистру значениями'''
    white_list = ['GL_118', 'GL_163', 'Prefix', 'GL_110', 'GL_111', 'GL_112', 'GL_137', 'GL_116', 'GL_117', 'GL_117', 'GL_118', 'GL_317', 'GL_318', 'GL_160', 'GL_138', 'GL-161', 'GL_141']
    answer = data.copy()
    for key in answer.keys():
        if isinstance(answer[key], str) and key in white_list:
            answer[key] = answer[key].upper()
    return answer


class Cards_Writer:
    '''Класс для записи данных в систему ЖС'''

    def __init__(self, config_file: str='config.ini'):
        '''
        coinfig_file: str - файл с конфигурацией
        (По умолчанию config.ini)
        '''
        config = configparser.ConfigParser()
        config.read(config_file)

        self._db_file = config['PATH']['db_path']
        self._cards_folder = config['PATH']['lsc_folder']

        self.conn = sqlite3.connect(self._db_file)

    def _write_to_db(self, data: dict) -> None:
        '''Пишет данные призывника в БД и записывает id в словарь'''
        cur = self.conn.cursor()
        CARD_ID = cur.execute('SELECT ID FROM GEN_CARD_ID').fetchone()[0]
        cur.execute('''UPDATE GEN_CARD_ID SET ID = ?''', (CARD_ID + 1,))
        data_to_db = data.copy()

        #дополнение и изменение значений для БД (некоторые поля в lsc отличаются названиями от того что в БД)
        data_to_db['CARD_ID'] = CARD_ID + 1 # по сути тут мы считаем новый АВТОИНКРЕМЕНТЫЙ ID, да такая вот хрень у них базе творится, чтобы получить ID я должен заполнить CARD_ID
        data_to_db['GL_105'] = data["GL_105"] = str(data_to_db['CARD_ID']).rjust(8, '0') # записываем id в словарь для lsc файла
        data_to_db['CARDTYPE'] = data_to_db.pop('_CARD_TYPE')
        data_to_db['GL_PREFIX'] = data_to_db.pop('Prefix')
        data_to_db['GL_FULLPREFIX'] = data_to_db.pop('FullPrefix')

        fields = [ #поля таблицы CARDS
            'CARD_ID',
            'CARDTYPE',
            'GL_PREFIX',
            'GL_FULLPREFIX',
            'GL_105',
            'GL_110',
            'GL_111',
            'GL_112',
            'GL_107',
            'GL_108',
            'GL_109',
            'GL_116',
            'GL_117',
            'GL_317',
            'GL_318',
            'GL_319',
            'GL_320',
            'GL_321',
            'GL_170',
            'GL_171',
            'GL_172',
            'GL_301',
            'GL_302',
            'GL_138',
            'GL_326',
            'GL_327',
            'GL_137',
            'GL_300',
            'GL_152',
            'GL_153',
            'GL_161',
            'GL_163',
            'GL_113',
            'GL_118',
            'GL_141',
            'GL_119',
            'GL_126',
            'GL_122',
            'GL_125',
            'GL_160',
            'GL_162',
            'GL_121',
            'GL_303',
            'GL_114',
            'GL_120',
            'GL_136',
            'GL_1303',
            'GL_147',
            'GL_503',
            'GL_504',
            'GL_506',
            'GL_505',
            'GL_192',
            'GL_158',
            'GL_159',
            'GL_518',
            'GL_322',
            'GL_325',
            'GL_169',
            'GL_173',
            'GL_174',
            'GL_175',
            'GL_501',
            'GL_502',
            'GL_328',
            'GL_329',
            'GL_330',
            'GL_331',
            'GL_332',
            'GL_333',
            'GL_334',
            'GL_339',
            'GL_340',
            'GL_341',
            'GL_342',
            'GL_343',
            'GL_344',
            'GL_345',
            'GL_346',
            'GL_347',
            'GL_348',
            'GL_349',
            'GL_350',
            'GL_351',
            'GL_541',
            'GL_851'
        ]

        columns = [col for col in data_to_db.keys() if col in fields] # получаем список всех ключей, которые знаем и которые нужны для БД
        values = [data_to_db[key] for key in columns] # получаем значения для них

        query = f'INSERT INTO CARDS ({', '.join(columns)}) VALUES ({", ".join(["?" for _ in values])}) RETURNING ID'
        id = cur.execute(query, tuple(values)).fetchone()[0] # вставляем данные в CARDS получаем id который присвоили карте

        query = f"INSERT INTO CARDSTATE (CARD_ID, DATE_CREATED, CREATED_BY) VALUES (?, datetime('now', 'localtime'), ?) RETURNING STATE_ID"
        state_id = cur.execute(query, (id, data_to_db["GL_119"])).fetchone()[0] # вставляем данные в CARDSTATE получаем STATE_ID который присвоили состоянию карты
        cur.execute('UPDATE GEN_STATE_ID SET ID = ?', (state_id, )) # АВТОМАТЬЕГОИНКРЕМЕНТ STATE_ID
        cur.execute('UPDATE CARD_NUMBER SET ID = ID + 1') # АВТОРАСКУДРИТЬВТОЮЧЕРЕЗКОРОМЫСЛОИНКРЕМЕНТ CARD_NUMBER
        self.conn.commit()
        logging.info(f'Карта записана в БД\nID = {id}\tФИО: {data["GL_110"]} {data["GL_111"]} {data["GL_112"]}')
        data['STATE_ID'] = state_id # запоминаем состояние, потому что потом надо будет записать md5 файла

    def write_card(self, data: dict):
        data = touppercase(data)
        '''Функция для записи карты в БД и в .lsc файл\n
        data: dict - словарь со всеми ключами необходимыми для дактокарты'''
        data["GL_113"] = datetime.datetime.now().strftime('%Y-%m-%d') # дата создания карты, собственно, сегодня
        self._write_to_db(data) # записываем данные в БД
        card = Daktocard.from_dict(data) # создали объект Дактокарты из данных что у нас были и что дополнила БД
        logging.debug(card)
        md5 = card.write_lsc(self._cards_folder) # записываем карту в .lsc файл и получаем md5-хэш файла
        logging.info('Карта записана в .lsc файл')
        cur = self.conn.cursor()
        cur.execute('UPDATE CARDSTATE SET MD5 = ? WHERE STATE_ID = ?', (md5, data['STATE_ID'],)) # записываем md5 файла в CARDSTATE по STATE_ID, который до этого сохраняли
        self.conn.commit()
        logging.info('MD5 записан, карта полностью создана\n' + '=' * 32)


if __name__ == '__main__':
    if '-d' in sys.argv:
        logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        print('debug_mode')
    else:
        logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    #общие значения
    if '-H' in sys.argv:
        from collections import OrderedDict
        
        data = OrderedDict()

        data["GL_110"] = input('Фамилия: ').upper()
        data["GL_111"] = input('Имя: ').upper()
        data["GL_112"] = input('Отчество: ').upper()
        data["GL_137"] = input('Гражданство: ').upper()
        data["GL_107"] = input('Дата рождения в формате YYYY-MM-DD: ').upper()
        data["GL_116"] = input('Место рождения: ').upper()
        registration = input('Адрес регистрации: ').upper()
        data["GL_117"] = registration
        data["GL_317"] = registration
        data["GL_318"] = registration
        data["GL_160"] = input('Регион: ').upper()
        data["GL_138"] = input('Паспорт: ').upper()
        data["GL_141"] = input('Основание: ').upper()
        data["GL_161"] = input('Жетон: ').upper()

        #записывает полученные данные в файл по-умолчанию data.json
        dict_to_json(data)
    
    try:
        writer = Cards_Writer() # это основной класс для записи данных
        # это функция с основной магией, на вход получает словарь со всеми данными которые пишутся в карту
        # в данном случае передаю словарь собраный из двух json файлов функцией get_all_data()
        logging.info('Создание новой карты...')
        writer.write_card(get_all_data())
        print('ok')
    except Exception as ex:
        logging.error(f'Ошибка: {ex}')