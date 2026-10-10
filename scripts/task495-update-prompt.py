#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 495: обновление системных промтов kip8 + kip8test (post-495).

kip8: post-Task 495 ПЕРЕНОС (kipia-v518→v519, 6165/0, из kip8test@
f1e9be83 по команде «Сразу вноси изменения и в kip8»).
kip8test: post-Task 495 ПЕРЕНОС-зеркало (код в kip8test v719/6161,
перенос выполнен, открытых хвостов нет).
"""
import io
import sys
import unicodedata

K8 = '/home/z/my-project/kip8'
KT = '/home/z/my-project/kip8test'
PREV_MARK = '> **Версия документа (предыдущая):**'


def find_prompt(root):
    for f in io.listdir_hack(root) if False else __import__('os').listdir(root):
        if f.endswith('.md') and unicodedata.normalize('NFC', f).startswith('Системный_промт'):
            return root + '/' + f
    return None


def update(path, new_line, cur_mark, tail):
    src = io.open(path, encoding='utf-8').read()
    if cur_mark not in src:
        print('ОШИБКА: якорь текущей версии не найден в %s' % path)
        sys.exit(1)

    # удалить самую старую «предыдущую» (ПОСЛЕДНЯЯ по позиции)
    if src.count(PREV_MARK) > 2:
        iprev = src.rindex(PREV_MARK)
        iprev_end = src.index('\n', iprev)
        src = src[:iprev] + src[iprev_end + 1:]

    i3 = src.index(cur_mark)
    i3end = src.index('\n', i3)
    old_line3 = src[i3:i3end]
    new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
    src = src[:i3] + new_line + tail + '\n' + new_prev + src[i3end:]
    io.open(path, 'w', encoding='utf-8').write(src)
    print('%s: строка версии обновлена' % path.split('/')[-2])


# ===================== kip8 =====================
PT8 = find_prompt(K8)
LINE3_8 = ('> **Версия документа:** 2026-10-10 (post-Task 495 ПЕРЕНОС: '
           '«ДАТЧИКИ ТЕМПЕРАТУРЫ» — БЛОК ВВОДА ДАННЫХ РАСЧЁТА ТАБЛИЦЫ '
           'БЕЗ ПОЛЯ ТИПА ДАТЧИКА, ПАНЕЛЬ С ЭФФЕКТОМ УГЛУБЛЕНИЯ — '
           'заявка: «В блоке ввода данных для расчёта таблицы убери поле '
           'с типом датчика, и убери тексты "Тип датчика" и "Шаг расчёта '
           'таблицы в градусах Цельсия", и оформи этот блок так же как '
           'блок произвольного расчёта, только не с эффектом выступа, а '
           'наоборот. Сразу вноси изменения и в kip8.»; КЛИЕНТ-ONLY, '
           'Apps Script не тронут). СУТЬ: на #page-temp-sensor-view '
           '(колонка ввода, ПОД панелью произвольного расчёта Task '
           '371/373/494): (а) УДАЛЕНЫ подпись «Тип датчика», чип '
           '#tempSensorViewChip (заполнение убрано из openTempSensor — '
           'тип датчика показывает заголовок страницы) и подсказка «Шаг '
           'расчёта таблицы в градусах Цельсия»; мёртвые CSS-правила '
           '.ts-view-chip* сняты; (б) обёртка .scale-form заменена '
           'панелью #tempTableFormPanel (класс ts-calc-panel '
           'ts-calc-inset) — как блок произвольного расчёта, но '
           'ПРОТИВОПОЛОЖНЫЙ эффект: УГЛУБЛЕНИЕ (border 1px '
           'rgba(74,143,199,0.32) против яркой 2px; фон rgba(13,17,23,'
           '0.55) БЕЗ синего градиента; box-shadow ТОЛЬКО внутренние '
           'inset 0 3px 10px + inset 0 -1px 0 — внешней НЕТ; светлая — '
           '21,54,83 0.08 + inset 0 2px 8px + светлая кромка; правило '
           'ПОСЛЕ базового и светлого .ts-calc-panel — перекрывает); '
           '(в) поля min/max/шаг — класс ts-calc-field (52/19/700/белый; '
           'ids/логика НЕ менялись; кнопка «Рассчитать» — ВНЕ панели). '
           'SW kipia-v518 → v519 (один инкремент). ТЕСТЫ kip8 6165/0 = '
           '6150+15: НОВЫЙ test-task495.js (MAP kipia-test→kipia; SRC '
           '×6 — литералы отсутствуют во всём index.html (урок 488: и '
           'в комментариях); CSS ×4; VM ×3 — чип не создаётся; SW ×2); '
           'адаптации 372/373 (чип) + 494 (конец чанка panelChunk → '
           'tempTableFormPanel); бамп guards v519→v520 ×149 / ассерты '
           'v518→v519 ×615; ОКНА kip8-геометрии (дистанции ≠ kip8test — '
           'переносить значения kip8test НЕЛЬЗЯ): 471 9800→10600, '
           '478/479 7700→8400 (якорь 478@7701 — вылет на 1!), 481 '
           'w1400→8400, 482 w7700→8400, 488 3200→4100; LIMITS 472 '
           '9100→9900 ×6 / 471 9800→10600 ×7; каскады 475/481/482/486. '
           'SMOKE task495-smoke-k8.py 21/21 (порт 9007, ключи БЕЗ '
           'префикса) + VLM ×5.')
update(PT8, LINE3_8,
       '> **Версия документа:** 2026-10-10 (post-Task 494 ПЕРЕНОС: панель произвольного расчёта',
       ' ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 — Task 495 ПЕРЕНЕСЁН (команда «Сразу '
       'вноси изменения и в kip8»), SW `kipia-v519` (guard v520), '
       'тесты 6165/0; kip8test @f1e9be83, SW `kipia-test-v719` (guard '
       'v720), тесты 6161/0 — Task 495 выкачан в ОБОИХ репо, открытых '
       'хвостов нет. Десктопы — CI-автосинк. Пользователям kip8: '
       'Ctrl+Shift+R ×1-2. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 496.')

src = io.open(PT8, encoding='utf-8').read()
reps8 = [
    ('> **Текущая версия кэша:** `kipia-v518`',
     '> **Текущая версия кэша:** `kipia-v519`'),
    ('Формат: `kipia-test-v718` → `kipia-test-v719` (для kip8test) или '
     '`kipia-v518` → `kipia-v519` (для kip8)',
     'Формат: `kipia-test-v719` → `kipia-test-v720` (для kip8test) или '
     '`kipia-v519` → `kipia-v520` (для kip8)'),
    ('# Ожидается: 6150 passed, 0 failed (kip8; в kip8test — 6146 passed, '
     '0 failed — Task 494 ПЕРЕНЕСЁН одним инкрементом kipia-v517→v518)',
     '# Ожидается: 6165 passed, 0 failed (kip8; в kip8test — 6161 passed, '
     '0 failed — Task 495 ПЕРЕНЕСЁН одним инкрементом kipia-v518→v519)'),
]
for old, new in reps8:
    if src.count(old) != 1:
        print('ПРЕДУПРЕЖДЕНИЕ kip8: %r найдено %d' % (old[:60], src.count(old)))
    src = src.replace(old, new)
io.open(PT8, 'w', encoding='utf-8').write(src)
print('kip8: кэш/формат/ожидание обновлены')

# ===================== kip8test =====================
PTT = find_prompt(KT)
LINE3_T = ('> **Версия документа:** 2026-10-10 (post-Task 495 '
           'ПЕРЕНОС-зеркало: «ДАТЧИКИ ТЕМПЕРАТУРЫ» — БЛОК ВВОДА ДАННЫХ '
           'РАСЧЁТА ТАБЛИЦЫ БЕЗ ПОЛЯ ТИПА ДАТЧИКА, ПАНЕЛЬ С ЭФФЕКТОМ '
           'УГЛУБЛЕНИЯ (ts-calc-inset) — заявка: «В блоке ввода данных '
           'для расчёта таблицы убери поле с типом датчика, и убери '
           'тексты "Тип датчика" и "Шаг расчёта таблицы в градусах '
           'Цельсия", и оформи этот блок так же как блок произвольного '
           'расчёта, только не с эффектом выступа, а наоборот. Сразу '
           'вноси изменения и в kip8.» — выполнено в kip8test (SW '
           'kipia-test-v718→v719, тесты 6161/0 = 6146+15, новый '
           'test-task495.js, адаптации 372/373/494, окна истории, '
           'browser-check 24/24 (порт 8983) + VLM ×5) и по команде из '
           'заявки ПЕРЕНЕСЕНО в боевой kip8 ОДНИМ инкрементом SW '
           'kipia-v518→v519 (регламент Task 441; тесты kip8 6165/0 = '
           '6150+15, SMOKE 21/21 (порт 9007, ключи БЕЗ префикса) + VLM '
           '×5; окна kip8-ГЕОМЕТРИИ — дистанции ≠ kip8test; ДЕТАЛИ: '
           'DEPLOY-Task495-temp-sensors-table-panel.md). КЛИЕНТ-ONLY.')
update(PTT, LINE3_T,
       '> **Версия документа:** 2026-10-10 (post-Task 494: «ДАТЧИКИ ТЕМПЕРАТУРЫ»',
       ' ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test @f1e9be83, SW `kipia-test-v719` '
       '(guard v720), тесты 6161/0; kip8 — Task 495 ПЕРЕНЕСЁН, SW '
       '`kipia-v519` (guard v520), тесты 6165/0. СЛЕДУЮЩИЙ НОМЕР '
       'ЗАДАЧИ: 496.')

src = io.open(PTT, encoding='utf-8').read()
repsT = [
    ('> **Текущая версия кэша:** `kipia-test-v718`',
     '> **Текущая версия кэша:** `kipia-test-v719`'),
    ('Формат: `kipia-test-v718` → `kipia-test-v719` (для kip8test) или '
     '`kipia-v517` → `kipia-v518` (для kip8)',
     'Формат: `kipia-test-v719` → `kipia-test-v720` (для kip8test) или '
     '`kipia-v518` → `kipia-v519` (для kip8)'),
    ('# Ожидается: 6146 passed, 0 failed (kip8test; в kip8 — 6138 passed, '
     '0 failed +12 после переноса Task 494 = 6150, одним инкрементом '
     'kipia-v517→v518)',
     '# Ожидается: 6161 passed, 0 failed (kip8test; в kip8 — 6150 passed, '
     '0 failed +15 после переноса Task 495 = 6165, одним инкрементом '
     'kipia-v518→v519)'),
]
for old, new in repsT:
    if src.count(old) != 1:
        print('ПРЕДУПРЕЖДЕНИЕ kip8test: %r найдено %d' % (old[:60], src.count(old)))
    src = src.replace(old, new)
io.open(PTT, 'w', encoding='utf-8').write(src)
print('kip8test: кэш/формат/ожидание обновлены')
