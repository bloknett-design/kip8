#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 494 (kip8): обновление системного промта kip8 (post-494 ПЕРЕНОС).
# kip8: кэш v518, формат v518→v519, ожидание 6150/6146, факт 6150.
import io
import glob
import sys

fail = []

def rd(p):
    return io.open(p, encoding='utf-8').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)

def rep(path, old, new, tag, cnt=1):
    s = rd(path)
    n = s.count(old)
    if n != cnt:
        fail.append('[%s] вхождений %d, ожидалось %d' % (tag, n, cnt))
        print('FAIL [%s]: вхождений %d, ожидалось %d' % (tag, n, cnt))
        return
    wr(path, s.replace(old, new))
    print('OK [%s]' % tag)

K8P = glob.glob('/home/z/my-project/kip8/Системный*.md')[0]

VER8_NEW = (
    '> **Версия документа:** 2026-10-10 (post-Task 494 ПЕРЕНОС: панель '
    'произвольного расчёта «Датчиков температуры» — заголовок «Расчёт '
    'произвольных значений» и подсказка «Введите значение в любое поле — '
    'другое рассчитается автоматически» УДАЛЕНЫ по заявке; блок — эффект '
    'ВЫСТУПА по образцу featured-кнопок Task 492 (рамка 2px '
    'rgba(74,143,199,0.85) + градиент linear-gradient(180deg, 0.2→0.05) '
    'ПОВЕРХ var(--card-bg) + тень 0 5px 14px / inset 0 1px 0 / inset '
    '0 -3px; светлая — рамка 43,111,163, тень 21,54,83 0.22); поля '
    '(оба: tempQueryTemp/tempQueryVal, класс ts-calc-field) — крупнее и '
    'ярче: 52px/19px/700/#ffffff, рамка 0.45, плейсхолдер 0.4, :focus '
    'рамка 0.85+свечение; светлая — #141413 на белом 0.75; подписи '
    '.scale-form-label в панели ярче (0.6/12px); ПОДВОДНЫЙ КАМЕНЬ: '
    'мобильные @media 480px/400px ужимают .form-field/.scale-field до '
    '14/13px и 40/38px ПОЗЖЕ основного правила (каскад, равная '
    'специфичность 0,1,0) — override-ы .ts-calc-field { padding: 10px '
    '14px; font-size: 19px; height: 52px; } ПОСЛЕ общих правил в ОБОИХ '
    'media-блоках; подписи полей под тип датчика (openTempSensor: '
    'Сопротивление R(t), Ом ↔ Термо-ЭДС E(t), мВ) и живой расчёт — НЕ '
    'менялись; текст подсказки жив в ДРУГИХ разделах (шкала-сигнал, '
    'буй) — НЕ трогать) выполнена в kip8test @92656802 (v718, 6146/0) '
    'и по команде «Сразу вноси изменения и в kip8» перенесена в боевой '
    'kip8 ОДНИМ инкрементом SW kipia-v517→v518 (регламент Task 441; '
    'КЛИЕНТ-ONLY, Apps Script не тронут, данные не менялись). ПЕРЕНОС '
    '(3 целевых правки index.html: панель/CSS/media-override — блоки '
    'идентичны kip8test; sw.js v518 + комментарий 494; тесты — '
    'test-task494.js MAP-версии kip8 (v518/v517/v519), адаптации '
    '371/373, бамп guards v518→v519 ×148 / ассерты v517→v518 ×611, '
    'окна kip8-геометрии 7300→7700/6800→7200/6600→7000/5400→5800/'
    '5500→5900/5100→5500/4400→4800 + каскады 482/486). Тесты kip8 '
    '6150/0 = 6138+12. SMOKE task494-smoke-k8.py 20/20 (порт 9007, '
    'ключи БЕЗ префикса; статика ×8 — в т.ч. подсказка отсутствует '
    'ИМЕННО в чанке панели; браузер: мобайл 375 тёмная 50М — панель '
    'без заголовка/подсказки, 2px/градиент/inset, поля 19px/52px/700/'
    'белый, живой расчёт t=55→R(t) 61,77; ТП tc_K (ключ ТП в каталоге '
    ' \'tc_\'+буква) — подпись Термо-ЭДС, t=300→E(t) 12,2086; светлая; '
    'десктоп; 0 JS ×3) + VLM ×4 (заголовка НЕТ, панель приподнятая, '
    'поля крупные). Десктопы — CI-автосинк. ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 '
    'PENDING, SW `kipia-v518` (guard v519), тесты 6150/0; kip8test '
    '@92656802, SW `kipia-test-v718` (guard v719), тесты 6146/0 — '
    'Task 494 выкачан в ОБОИХ репо, открытых хвостов нет. Пользователям '
    'kip8: Ctrl+Shift+R ×1-2. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 495 (в обоих '
    'репо).')

PREV_MARK = '> **Версия документа (предыдущая):**'

src = rd(K8P)
cur_mark = '> **Версия документа:** 2026-10-10 (post-Task 493 ПЕРЕНОС:'
if cur_mark not in src:
    print('ОШИБКА: строка версии не найдена')
    sys.exit(1)

# удалить самую старую «предыдущую» (последняя по позиции), если > 6
if src.count(PREV_MARK) > 6:
    iprev = src.rindex(PREV_MARK)
    iprev_end = src.index('\n', iprev)
    src = src[:iprev] + src[iprev_end + 1:]

i3 = src.index(cur_mark)
i3end = src.index('\n', i3)
old_line3 = src[i3:i3end]
new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
src = src[:i3] + VER8_NEW + '\n' + new_prev + src[i3end:]
wr(K8P, src)
print('%s: строка 3 обновлена (post-494 ПЕРЕНОС)' % K8P)

# --- скаляры kip8 ---
rep(K8P, '> **Текущая версия кэша:** `kipia-v517`',
    '> **Текущая версия кэша:** `kipia-v518`', 'кэш v518')
rep(K8P,
    'Формат: `kipia-test-v717` → `kipia-test-v718` (для kip8test) или '
    '`kipia-v516` → `kipia-v517` (для kip8)',
    'Формат: `kipia-test-v718` → `kipia-test-v719` (для kip8test) или '
    '`kipia-v518` → `kipia-v519` (для kip8)', 'формат инкремента')
rep(K8P,
    '# Ожидается: 6138 passed, 0 failed (kip8; в kip8test — 6134 passed, '
    '0 failed — Task 493 ПЕРЕНЕСЁН одним инкрементом kipia-v516→v517)',
    '# Ожидается: 6150 passed, 0 failed (kip8; в kip8test — 6146 passed, '
    '0 failed — Task 494 ПЕРЕНЕСЁН одним инкрементом kipia-v517→v518)',
    'ожидание тестов')
rep(K8P,
    '(`tests/`, 6138 тестов, 201 тест-файл, `node tests/run-all.js`)',
    '(`tests/`, 6150 тестов, 205 тест-файлов, `node tests/run-all.js`)',
    'таблица тестов')

if fail:
    print('FAIL: %s' % fail)
    sys.exit(1)
print('kip8: скаляры обновлены')
