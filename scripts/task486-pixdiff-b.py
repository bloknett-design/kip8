#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 486 SMOKE (kip8): объективная сверка рендера kip8 против
# эталона kip8test (b-open-after-silent.png; код идентичен —
# «дифф диффов» сошёлся). Ожидаются ТОЛЬКО ожидаемые различия:
# подсветка текущего дня (7-е vs 8-е), штамп «данные от …».
from PIL import Image, ImageChops
import sys

A = '/home/z/my-project/download/kip8-task486-transfer/b-open-after-silent.png'
B = '/home/z/my-project/download/kip8test-task486/b-open-after-silent.png'

ia = Image.open(A).convert('RGB')
ib = Image.open(B).convert('RGB')
print('размеры: kip8 %s, kip8test %s' % (ia.size, ib.size))
if ia.size != ib.size:
    print('РАЗМЕРЫ РАЗЛИЧАЮТСЯ — сравнение после приведения')
    ib = ib.resize(ia.size)

diff = ImageChops.difference(ia, ib)
bbox = diff.getbbox()
print('bbox различий:', bbox)

# Грубая карта: сетка 16x9 ячеек, доля изменённых пикселей в каждой
W, H = ia.size
gx, gy = 16, 9
changed_cells = 0
total_cells = 0
for yy in range(gy):
    row = []
    for xx in range(gx):
        box = (xx * W // gx, yy * H // gy,
               (xx + 1) * W // gx, (yy + 1) * H // gy)
        cell = diff.crop(box)
        hist = cell.convert('L').histogram()
        nonblack = sum(hist[8:])  # пиксели с |diff| >= 8
        frac = nonblack / (cell.size[0] * cell.size[1])
        total_cells += 1
        mark = '#' if frac > 0.02 else '.'
        if frac > 0.02:
            changed_cells += 1
        row.append(mark)
    print(''.join(row))
print('изменённых ячеек (>2%% пикселей): %d из %d' %
      (changed_cells, total_cells))
# Вердикт: при идентичном коде меняются день-подсветка (1 колонка
# сетки), штамп даты (верх), скроллбар — считаем < 10 ячеек нормой
sys.exit(0 if changed_cells <= 10 else 1)
