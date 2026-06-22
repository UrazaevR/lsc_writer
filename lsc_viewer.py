import sys
import datetime
from typing import Any

params: list[str] = []
dates: list[str] = []
others: list[str] = []

def jd_to_date(jd) -> str:
    """Перевод юлианского дня в дату (григорианский календарь)"""
    jd = jd + 0.5  # поправка на полдень
    
    z = int(jd)
    f = jd - z
    
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    
    return datetime.datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")

def read_file(file_path: str) -> dict[str, Any]:
    data = {}

    with open(file_path, mode='rb') as file:
        data['value_type'] = []

        #заголовок
        data['extension'] = file.read(4).decode() #расширение файла
        data['version'] = int.from_bytes(file.read(4), byteorder='little') #версия
        data['head_size'] = int.from_bytes(file.read(4), byteorder='little') #размер заголовка
        data['data_size'] = int.from_bytes(file.read(4), byteorder='little') #размер тела файла
        data['count_fields'] = int.from_bytes(file.read(4), byteorder='little') #сколько всего ключей в файле (7 в заголовке, 1 количество полей в теле, 40 полей в теле)
        data['some2'] = int.from_bytes(file.read(4), byteorder='little') #еще что-то везде 0
        data['file_size'] = int.from_bytes(file.read(4), byteorder='little') #размер файла целиком

        #тело
        data['count_keys'] = int.from_bytes(file.read(4), byteorder='big') #количество полей в теле

        for _ in range(1, data['count_keys'] + 1):
            key_size = int.from_bytes(file.read(4), byteorder='big') #читаем длину ключа в байтах и переводим в int
            key = file.read(key_size).decode('utf-16be') #читаем ключ
            params.append(key)
            data['value_type'].append(file.read(5).hex().upper()) # тип данных поля
            value_size = int.from_bytes(file.read(4), byteorder='big', signed=True) #читаем длину значения в байтах и переводим в int
            #print('key', key, '\t', 'key_size:', key_size, '\t', 'value_size:', value_size)
            if value_size == -1: #если записано -1, значит данных нет (null)
                value = None
            elif data['value_type'][-1] != '0000000A00':
                if data['value_type'][-1] == '0000000E00': #обозначение даты
                    value = jd_to_date(value_size)
                    dates.append(key)
                else:
                    if data['value_type'][-1] not in ('0000000A00', '0000000E00'):
                        others.append(key + '-->' + data['value_type'][-1])
                    value = value_size # получается для всех типов что я не знаю пишется просто следующий байт в значение
                # TODO: 00 00 00 03 00 - надо узнать что за тип данных, используется в параметре 723
            else:
                value = file.read(value_size).decode('utf-16be') #читаем значение поля
            data[key] = value
    return data
        

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input('Введите путь к LSC файлу: ')
    from pprint import pprint
    pprint(read_file(file_path))
    