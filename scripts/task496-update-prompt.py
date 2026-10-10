#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 496: обновление системных промтов kip8 + kip8test (post-496).

kip8: post-Task 496 ПЕРЕНОС (kipia-v519→v520, 6182/0, из kip8test@
a3006907 по команде «Сразу вноси изменения и в kip8»).
kip8test: post-Task 496 ПЕРЕНОС-зеркало (код в kip8test v720/6178,
перенос выполнен, открытых хвостов нет).
"""
import io
import sys
import os
import unicodedata

K8 = '/home/z/my-project/kip8'
KT = '/home/z/my-project/kip8test'
PREV_MARK = '> **Версия документа (предыдущая):**'


def find_prompt(root):
    for f in os.listdir(root):
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
LINE3_8 = ('> **Версия документа:** 2026-10-10 (post-Task 496 ПЕРЕНОС: '
           '«ДАТЧИКИ ТЕМПЕРАТУРЫ» — ППР: ENTER ЗАКРЫВАЕТ КЛАВИАТУРУ — '
           'заявка: «В блоке произвольного расчёта, после ввода одного '
           'из данных и при нажатии подтверждения на клавиатуре, '
           'клавиатура должна закрываться, а не перемещаться по '
           'следующим полям ввода.»; КЛИЕНТ-ONLY). СУТЬ: на '
           '#page-temp-sensor-view, панель произвольного расчёта '
           '#tempCustomCalcPanel (поля #tempQueryTemp/#tempQueryVal, '
           'Tasks 371/373/494): (а) enterkeyhint поля температуры '
           'next → done (кнопка «Далее» перескакивала в поле '
           'значения) — у ОБОИХ полей done; (б) onkeydown '
           'tempQueryEnterBlur(event,this): Enter → preventDefault + '
           'stopPropagation + blur — КЛЮЧЕВОЙ stopPropagation: без '
           'него ГЛОБАЛЬНЫЙ document-keydown «Обработчик Enter/Next — '
           'логичный переход между полями и расчёт» видит e.target '
           'ПОСЛЕ blur и возвращает фокус в следующее поле — '
           'клавиатура не закрывалась; (в) живой двусторонний расчёт '
           'по oninput не менялся; (г) ГРАНИЦЫ: блок расчёта таблицы '
           '(Task 495, min/max next×2) и глобальный Enter-переход '
           'остальных блоков — НЕ тронуты; (д) iOS: «done» сам '
           'клавиатуру не убирает — blur() закрывает и там. SW '
           'kipia-v519 → v520 (один инкремент). ТЕСТЫ kip8 6182/0 = '
           '6165+17: НОВЫЙ test-task496.js (MAP kipia-test-v720→'
           'kipia-v520; SRC HTML/границы/глоб; VM ×6 — стопит/гасит/'
           'blur; SW ×2); бамп guards v520→v521 ×149 / ассерты '
           'v519→v520 ×621 (618 + 3 истор. комментария run-all — '
           'восстановлены 493/494/495 «v519»); ОКНА kip8-геометрии '
           '(+249 симв.): 461/472/473/474/480/481(×2)/482(×2)/483/'
           '484/485/486 + LIMITS 461 ×7 / 474 ×6 + каскады 475/481/'
           '482/486. SMOKE task496-smoke-k8.py 21/21 (порт 9007, '
           'ключи БЕЗ префикса) + VLM ×5.')
update(PT8, LINE3_8,
       '> **Версия документа:** 2026-10-10 (post-Task 495 ПЕРЕНОС: «ДАТЧИКИ ТЕМПЕРАТУРЫ»',
       ' ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 — Task 496 ПЕРЕНЕСЁН (команда «Сразу '
       'вноси изменения и в kip8», прецедент 494/495), SW `kipia-v520` '
       '(guard v521), тесты 6182/0; kip8test @a3006907, SW '
       '`kipia-test-v720` (guard v721), тесты 6178/0 — Task 496 '
       'выкачан в ОБОИХ репо, открытых хвостов нет. Десктопы — '
       'CI-автосинк. Пользователям kip8: Ctrl+Shift+R ×1-2. '
       'СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 497.')

src = io.open(PT8, encoding='utf-8').read()
reps8 = [
    ('> **Текущая версия кэша:** `kipia-v519`',
     '> **Текущая версия кэша:** `kipia-v520`'),
    ('Формат: `kipia-test-v719` → `kipia-test-v720` (для kip8test) или '
     '`kipia-v519` → `kipia-v520` (для kip8)',
     'Формат: `kipia-test-v720` → `kipia-test-v721` (для kip8test) или '
     '`kipia-v520` → `kipia-v521` (для kip8)'),
    ('# Ожидается: 6165 passed, 0 failed (kip8; в kip8test — 6161 passed, '
     '0 failed — Task 495 ПЕРЕНЕСЁН одним инкрементом kipia-v518→v519)',
     '# Ожидается: 6182 passed, 0 failed (kip8; в kip8test — 6178 passed, '
     '0 failed — Task 496 ПЕРЕНЕСЁН одним инкрементом kipia-v519→v520)'),
]
for old, new in reps8:
    if src.count(old) != 1:
        print('ПРЕДУПРЕЖДЕНИЕ kip8: %r найдено %d' % (old[:60], src.count(old)))
    src = src.replace(old, new)
io.open(PT8, 'w', encoding='utf-8').write(src)
print('kip8: кэш/формат/ожидание обновлены')

# ===================== kip8test =====================
PTT = find_prompt(KT)
LINE3_T = ('> **Версия документа:** 2026-10-10 (post-Task 496 '
           'ПЕРЕНОС-зеркало: «ДАТЧИКИ ТЕМПЕРАТУРЫ» — ППР: ENTER '
           'ЗАКРЫВАЕТ КЛАВИАТУРУ (заявка: «В блоке произвольного '
           'расчёта, после ввода одного из данных и при нажатии '
           'подтверждения на клавиатуре, клавиатура должна '
           'закрываться, а не перемещаться по следующим полям '
           'ввода.» — выполнено в kip8test (SW kipia-test-v719→v720, '
           'тесты 6178/0 = 6161+17, новый test-task496.js, окна '
           'истории 474/481 + каскады, browser-check 24/24 (порт '
           '8984) + VLM ×5) и ПЕРЕНЕСЕНО в боевой kip8 ОДНИМ '
           'инкрементом SW kipia-v519→v520 (регламент Task 441; '
           'тесты kip8 6182/0, SMOKE 21/21 (порт 9007, ключи БЕЗ '
           'префикса) + VLM ×5; окна kip8-ГЕОМЕТРИИ — 21 окно + '
           'LIMITS + каскады; ДЕТАЛИ: DEPLOY-Task496-temp-sensors-'
           'ppr-enter-keyboard.md). КЛИЕНТ-ONLY.')
update(PTT, LINE3_T,
       '> **Версия документа:** 2026-10-10 (post-Task 495 ПЕРЕНОС-зеркало: «ДАТЧИКИ ТЕМПЕРАТУРЫ»',
       ' ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test @a3006907, SW `kipia-test-v720` '
       '(guard v721), тесты 6178/0; kip8 — Task 496 ПЕРЕНЕСЁН, SW '
       '`kipia-v520` (guard v521), тесты 6182/0. СЛЕДУЮЩИЙ НОМЕР '
       'ЗАДАЧИ: 497.')

src = io.open(PTT, encoding='utf-8').read()
repsT = [
    ('> **Текущая версия кэша:** `kipia-test-v719`',
     '> **Текущая версия кэша:** `kipia-test-v720`'),
    ('Формат: `kipia-test-v719` → `kipia-test-v720` (для kip8test) или '
     '`kipia-v518` → `kipia-v519` (для kip8)',
     'Формат: `kipia-test-v720` → `kipia-test-v721` (для kip8test) или '
     '`kipia-v519` → `kipia-v520` (для kip8)'),
    ('# Ожидается: 6161 passed, 0 failed (kip8test; в kip8 — 6150 passed, '
     '0 failed +15 после переноса Task 495 = 6165, одним инкрементом '
     'kipia-v518→v519)',
     '# Ожидается: 6178 passed, 0 failed (kip8test; в kip8 — 6165 passed, '
     '0 failed +17 после переноса Task 496 = 6182, одним инкрементом '
     'kipia-v519→v520)'),
]
for old, new in repsT:
    if src.count(old) != 1:
        print('ПРЕДУПРЕЖДЕНИЕ kip8test: %r найдено %d' % (old[:60], src.count(old)))
    src = src.replace(old, new)
io.open(PTT, 'w', encoding='utf-8').write(src)
print('kip8test: кэш/формат/ожидание обновлены')
