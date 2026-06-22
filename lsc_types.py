import datetime
import hashlib
from abc import ABC, abstractmethod
from typing import Union


def date_to_jdn(day: int, month: int, year: int) -> int:
    """
    Дата -> целый юлианский день (JDN)
    """
    if month <= 2:
        year -= 1
        month += 12
    
    A = year // 100
    B = 2 - A + A // 4
    
    jdn = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524
    return jdn


class Type(ABC):
    '''Абстрактный класс для типов полей'''
    type_code = b'\x00\x00\x00\x00\x00'

    def __init__(self, value):
        self.value = value
        
    def __call__(self):
        return self.value
    
    def __str__(self) -> str:
        if self.value is None:
            return f'{self.__class__.__name__}(None)'
        return f'{self.__class__.__name__}({self.value})'
    
    def __repr__(self) -> str:
        return str(self)
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        '''Возвращает байты, которые нужно записать после кода поля'''
        pass
    
    def size(self) -> int:
        return len(self.to_bytes())


class Date(Type):
    '''Класс для типа DATE'''
    type_code = b'\x00\x00\x00\x0E\x00'

    def __init__(self, day: int | None=None, month: int | None=None, year: int | None=None):
        if day is None or month is None or year is None:
            self.value = None
            return
        if not isinstance(day, int):
            raise ValueError(f'В поле day типа Date необходимо записать int, не {type(day).__name__}')
        if not isinstance(month, int):
            raise ValueError(f'В поле day типа Date необходимо записать int, не {type(month).__name__}')
        if not isinstance(year, int):
            raise ValueError(f'В поле day типа Date необходимо записать int, не {type(year).__name__}')
        self.value = datetime.date(year=year, month=month, day=day)
        
    def __str__(self) -> str:
        if self.value is None:
            return f'Date()'
        return f'{self.__class__.__name__}(day={self.value.day}, month={self.value.month}, year={self.value.year})'
    
    def to_bytes(self) -> bytes:
        if self.value is None:
            return self.type_code + b'\xFF\xFF\xFF\xFF'
        return self.type_code + date_to_jdn(self.value.day, self.value.month, self.value.year).to_bytes(4, 'big')
    

class Text(Type):
    '''Класс для типа TEXT, в коструктор передать одно значение - str или None'''
    type_code = b'\x00\x00\x00\x0A\x00'

    def __init__(self, value: str | None):
        if not isinstance(value, str) and value is not None:
            raise ValueError(f'В поле типа Text можно записывать только строковые данные, не {type(value).__name__}')
        self.value = value
    
    def to_bytes(self):
        if self.value is None:
            return self.type_code + b'\xFF\xFF\xFF\xFF'
        if self.value == '':
            return self.type_code + int(0).to_bytes(4, 'big')
        encoded = self.value.encode('utf-16be')
        return self.type_code + len(encoded).to_bytes(4, 'big') + encoded

    def __str__(self) -> str:
        if self.value is None:
            return f'{self.__class__.__name__}(None)'
        return f'{self.__class__.__name__}("{self.value}")'


class Int(Type):
    '''Класс для целочисленных значений, в конструктор число или None'''
    type_code = b'\x00\x00\x00\x02\x00'

    def __init__(self, value: int | None):
        if not isinstance(value, int) and value is not None:
            raise ValueError(f'В поле типа Int можно записывать только числовые данные, не {type(value).__name__}')
        self.value = value
    
    def to_bytes(self):
        if self.value is None:
            return self.type_code + b'\xFF\xFF\xFF\xFF'
        return self.type_code + self.value.to_bytes(4, 'big')
    

class Some(Int):
    '''Класс параметра GL_723 (там по сути число, совпадающее с серийником сканера, возможно это тоже число, только беззнаковое например)'''
    type_code = b'\x00\x00\x00\x03\x00'


class Daktocard:
    '''Класс дактокарты, просто хранит данные и может их записать в .lsc файл'''
    def __init__(self, 
             _VERBALNOTE: Union[Text, str, None] = None,
             _VERBAL: Union[Text, str, None] = None,
             _CARD_TYPE: Union[Text, str, None] = None,
             Prefix: Union[Text, str, None] = None,
             FullPrefix: Union[Text, str, None] = None,
             GL_837: Union[Text, str, None] = None,
             GL_822: Union[Text, str, None] = None,
             GL_821: Union[Text, str, None] = None,
             GL_803: Union[Text, str, None] = None,
             GL_723: Union[Some, int, None] = None,
             GL_708: Union[Text, str, None] = None,
             GL_701: Union[Text, str, None] = None,
             GL_493: Union[Text, str, None] = None,
             GL_492: Union[Text, str, None] = None,
             GL_366: Union[Text, str, None] = None,
             GL_365: Union[Text, str, None] = None,
             GL_318: Union[Text, str, None] = None,
             GL_317: Union[Text, str, None] = None,
             GL_202: Union[Text, str, None] = None,
             GL_163: Union[Text, str, None] = None,
             GL_161: Union[Text, str, None] = None,
             GL_160: Union[Text, str, None] = None,
             GL_141: Union[Text, str, None] = None,
             GL_138: Union[Text, str, None] = None,
             GL_137: Union[Text, str, None] = None,
             GL_125: Union[Text, str, None] = None,
             GL_123: Union[Text, str, None] = None,
             GL_122: Union[Text, str, None] = None,
             GL_119: Union[Text, str, None] = None,
             GL_118: Union[Text, str, None] = None,
             GL_117: Union[Text, str, None] = None,
             GL_116: Union[Text, str, None] = None,
             GL_113: Union[Date, datetime.date, str, None] = None,
             GL_112: Union[Text, str, None] = None,
             GL_111: Union[Text, str, None] = None,
             GL_110: Union[Text, str, None] = None,
             GL_108: Union[Int, int, None] = None,
             GL_107: Union[Date, datetime.date, str, None] = None,
             GL_105: Union[Text, str, None] = None,
             GL_103: Union[Text, str, None] = None):
    
        # Вспомогательная функция для преобразования в Text
        def to_text(value):
            if value is None:
                return Text(None)
            if isinstance(value, Text):
                return value
            if isinstance(value, str):
                return Text(value)
            return Text(str(value))
        
        # Вспомогательная функция для преобразования в Int
        def to_int(value):
            if value is None:
                return Int(None)
            if isinstance(value, Int):
                return value
            if isinstance(value, int):
                return Int(value)
            return Int(int(value))
        
        # Вспомогательная функция для преобразования в Some
        def to_some(value):
            if value is None:
                return Some(None)
            if isinstance(value, Some):
                return value
            if isinstance(value, int):
                return Some(value)
            return Some(int(value))
        
        # Вспомогательная функция для преобразования в Date
        def to_date(v):
            if v is None:
                return Date()
            if isinstance(v, Date):
                return v
            if isinstance(v, datetime.date):
                return Date(v.day, v.month, v.year)
            if isinstance(v, datetime.datetime):
                return Date(v.day, v.month, v.year)
            if isinstance(v, str):
                try:
                    dt = datetime.datetime.strptime(v, '%Y-%m-%d')
                    return Date(dt.day, dt.month, dt.year)  # day, month, year
                except ValueError:
                    raise ValueError(f"Не удалось распарсить дату: {v}")
            raise TypeError(f"Неподдерживаемый тип для Date: {type(v)}")
        
        # Присваиваем значения с преобразованием
        self._VERBALNOTE = to_text(_VERBALNOTE)
        self._VERBAL = to_text(_VERBAL)
        self._CARD_TYPE = to_text(_CARD_TYPE)
        self.Prefix = to_text(Prefix)
        self.FullPrefix = to_text(FullPrefix)
        self.GL_837 = to_text(GL_837)
        self.GL_822 = to_text(GL_822)
        self.GL_821 = to_text(GL_821)
        self.GL_803 = to_text(GL_803)
        self.GL_723 = to_some(GL_723)
        self.GL_708 = to_text(GL_708)
        self.GL_701 = to_text(GL_701)
        self.GL_493 = to_text(GL_493)
        self.GL_492 = to_text(GL_492)
        self.GL_366 = to_text(GL_366)
        self.GL_365 = to_text(GL_365)
        self.GL_318 = to_text(GL_318)
        self.GL_317 = to_text(GL_317)
        self.GL_202 = to_text(GL_202)
        self.GL_163 = to_text(GL_163)
        self.GL_161 = to_text(GL_161)
        self.GL_160 = to_text(GL_160)
        self.GL_141 = to_text(GL_141)
        self.GL_138 = to_text(GL_138)
        self.GL_137 = to_text(GL_137)
        self.GL_125 = to_text(GL_125)
        self.GL_123 = to_text(GL_123)
        self.GL_122 = to_text(GL_122)
        self.GL_119 = to_text(GL_119)
        self.GL_118 = to_text(GL_118)
        self.GL_117 = to_text(GL_117)
        self.GL_116 = to_text(GL_116)
        self.GL_113 = to_date(GL_113)
        self.GL_112 = to_text(GL_112)
        self.GL_111 = to_text(GL_111)
        self.GL_110 = to_text(GL_110)
        self.GL_108 = to_int(GL_108)
        self.GL_107 = to_date(GL_107)
        self.GL_105 = to_text(GL_105)
        self.GL_103 = to_text(GL_103)

    def write_lsc(self, file_folder: str) -> str:
        '''Функция получает путь к каталогу и записывает в него lsc файл с данными объекта, возвращает md5-хэш файла"'''
        body = b''
        for key in self.__dict__.keys():
            data = self.__dict__[key].to_bytes()
            if key.startswith('GL_'):
                key = key[3:]
            encode = key.encode('utf-16be')
            body += len(encode).to_bytes(4, 'big') + encode + data
        body = len(self.__dict__.keys()).to_bytes(4, 'big') + body

        header = b''
        header += 'LSC '.encode() # расширение файла
        header += int(101).to_bytes(4, 'little') # версия
        header += int(28).to_bytes(4, 'little') # размер заголовка
        header += len(body).to_bytes(4, 'little') # размер тела файла
        header += int(7 + 1 + len(self.__dict__.keys())).to_bytes(4, 'little') # сколько всего ключей в файле
        header += int(0).to_bytes(4, 'little') # хз что это, но везде 0
        header += int(len(header) + 4 + len(body)).to_bytes(4, 'little') # общий размер файла
        with open(file_folder + f'/{self.GL_105.value.rjust(19, '0')}.lsc', 'wb') as file:
            file.write(header)
            file.write(body)
            md5 = hashlib.md5(header + body).hexdigest()
        return md5

    @classmethod
    def from_dict(cls, data: dict) -> Daktocard:
        '''Получает на вход словарь, ищет там параметры для конструктора дактокарты и возвращает объект класса Daktocard с этими параметрами, неподходящие ключи отбрасываются'''
        params = {}
        for key in data:
            card_key = key
            if key.isnumeric():
                card_key = 'GL_' + key
            if card_key in ('_VERBALNOTE', '_VERBAL', '_CARD_TYPE', 'Prefix', 'FullPrefix', 'GL_837', 'GL_822', 'GL_821', 'GL_803', 'GL_723', 'GL_708', 'GL_701', 'GL_493', 'GL_492', 'GL_366', 'GL_365', 'GL_318', 'GL_317', 'GL_202', 'GL_163', 'GL_161', 'GL_160', 'GL_141', 'GL_138', 'GL_137', 'GL_125', 'GL_123', 'GL_122', 'GL_119', 'GL_118', 'GL_117', 'GL_116', 'GL_113', 'GL_112', 'GL_111', 'GL_110', 'GL_108', 'GL_107', 'GL_105', 'GL_103'):
                params[card_key] = data[key]
        return Daktocard(**params)
    
    def __str__(self) -> str:
        params = []
        for attr in sorted(self.__dict__.keys()):
            value = getattr(self, attr)
            params.append(f"{attr}={value}")
        return f"{self.__class__.__name__}({', '.join(params)})"


if __name__ == '__main__':
    card = Daktocard(FullPrefix=Text('581201L001'), GL_103=Text('5a56'), GL_105=Text('00000163'), GL_107=Date(day=6, month=6, year=1996),
                      GL_108=Int(1), GL_110=Text('КОЗЛОВ'), GL_111=Text('НИКИТА'), GL_112=Text('МИХАЙЛОВИЧ'), GL_113=Date(day=21, month=6, year=2026), 
                      GL_116=Text('Г. ПЕНЗА'), GL_117=Text('Г. ПЕНЗА, УЛ. КАРЬЕРНАЯ, Д. 4, КВ. 1'), GL_118=Text('ВОЕННЫЙ КОМИССАРИАТ ПЕНЗЕНСКОЙ ОБЛАСТИ'), 
                      GL_119=Text('КОЗЛОВ Н.М.'), GL_122=Text(None), GL_123=Text('КОЗЛОВ Н.М.'), GL_125=Text(None), GL_137=Text('РОССИЙСКАЯ ФЕДЕРАЦИЯ,RU'), 
                      GL_138=Text('5618463959'), GL_141=Text(''), GL_160=Text('58'), GL_161=Text('СА-446227'), GL_163=Text('КАДРОВАЯ,1'), GL_202=Text('581201L001'), 
                      GL_317=Text('Г. ПЕНЗА'), GL_318=Text('УЛ. КАРЬЕРНАЯ'), 
                      GL_365=Text('6a0afcb2'), GL_366=Text('КОЗЛОВ Н.М.'), GL_492=Text('22665'), GL_493=Text('K132-1'), GL_701=Text('DS45 S/N 24352), GL_708=Text(Live Scanner 5.1.5-14 build 16.01.2026'), 
                      GL_723=Some(24352), GL_803=Text('1205'), GL_821=Text('1'), GL_822=Text('1'), GL_837=Text(None), Prefix=Text('ПРИЗЫВНИК МО,1205'), _CARD_TYPE=Text('rus-i_reg'), _VERBAL=Text(None), _VERBALNOTE=Text(None))
    card.write_lsc('./cards')