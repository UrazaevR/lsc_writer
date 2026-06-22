from lsc_types import *
from lsc_viewer import *
import sqlite3

# VARCHAR (Text) поля
varchar_fields = [
    'GL_109', 'GL_319', 'GL_320', 'GL_321', 'GL_170', 'GL_171', 'GL_172',
    'GL_301', 'GL_302', 'GL_326', 'GL_327', 'GL_300', 'GL_152', 'GL_126',
    'GL_162', 'GL_303', 'GL_120', 'GL_136', 'GL_1303', 'GL_147', 'GL_506',
    'GL_505', 'GL_192', 'GL_158', 'GL_159', 'GL_322', 'GL_325', 'GL_169',
    'GL_173', 'GL_174', 'GL_175', 'GL_502', 'GL_329', 'GL_339', 'GL_342',
    'GL_343', 'GL_345', 'GL_346', 'GL_348', 'GL_349', 'GL_350', 'GL_351'
]

# DATE поля
date_fields = [
    'GL_153', 'GL_114', 'GL_518', 'GL_330', 'GL_334', 'GL_340', 'GL_341',
    'GL_344', 'GL_347', 'GL_851'
]

# INTEGER поля
int_fields = [
    'GL_503', 'GL_504', 'GL_331', 'GL_332', 'GL_333'
]

# BLOB (Text) поля
blob_fields = [
    'GL_121', 'GL_501', 'GL_328', 'GL_541'
]

'''params = {}
for i in range(38, 50):
    if i == 43: continue
    file_path = f'C:/Users/Руслан/Projects/Козлов/Пальцы/папилон дата/cards/0000000000000000/00000000000000000{i}.lsc'
    data = read_file(file_path)
    for key in data.keys():
        if key in params:
            params[key].append(data[key])
        else:
            params[key] = [data[key]]

for key in params.keys():
    if params[key].count(params[key][0]) == len(params[key]):
        x = params[key][0]
        print(key if not key.isnumeric() else 'GL_'+key, '=', x if isinstance(x, int) else f'"{x}"')'''

print('123'.rjust(8, '0'))