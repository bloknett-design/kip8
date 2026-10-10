#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 493: обновление системных промтов ОБОИХ репо после переноса.
kip8: post-Task 493 ПЕРЕНОС — кэш v517, формат v517→v518, тесты
6138/201 файлов, ожидание 6138/6134.
kip8test: post-Task 493 ПЕРЕНОС-зеркало — кэш v717, формат
v717→v718, тесты 6134/201 файлов, ожидание 6134/6138 (Task 493
ПЕРЕНЕСЁН одним инкрементом kipia-v516→v517), СЛЕДУЮЩИЙ 494.
"""
import glob
import io
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
K8TP = glob.glob('/home/z/my-project/kip8test/Системный*.md')[0]

# ================= kip8 =================
VER8_NEW = (
    '> **Версия документа:** 2026-10-10 (post-Task 493 ПЕРЕНОС: кнопка '
    '«Табель учёта рабочего времени», закрепляемая на главную (реестр '
    'SUBSECTIONS → renderPinnedItems) и стоящая на «Документации ИОС» '
    '(#workScheduleMenuBtn), переименована короче — «Табель учёта»; '
    'заголовок страницы, крошки PAGE_LABELS и пункт сайдбара — прежние '
    'полные имена; субметка/id/права не тронуты; заявка: «Кнопку '
    '"Табель учёта рабочего времени" установленную на главную страницу '
    'назови короче "Табель учёта". Перенос в kip8.») перенесена из '
    'kip8test@e833ef2e в боевой kip8 ОДНИМ инкрементом SW '
    'kipia-v516→v517 (регламент Task 441); КЛИЕНТ-ONLY (Apps Script '
    'не тронут); тесты kip8 6138/0 = 6128+10 (новый test-task493.js с '
    'MAP kipia-test-v717→kipia-v517; адаптации 321/work-schedule — '
    'реестр и кнопка; окно 482 6600→6800 — комментарий 493 +173 симв. '
    'вытеснил 480@6650); SMOKE 16/16 (порт 9007, ключи БЕЗ префикса — '
    'де-изоляция) + VLM ×4; первый прогон 1 падение (окно 482), '
    'фикс — расширение окна\n')

s8 = rd(K8P)
first_ver = s8.index('> **Версия документа:**')
line_end = s8.index('\n', first_ver)
cur = s8[first_ver:line_end]
cur_demoted = cur.replace('> **Версия документа:**',
                          '> **Версия документа (предыдущая):**', 1)
s8 = s8[:first_ver] + VER8_NEW + cur_demoted + s8[line_end:]
wr(K8P, s8)
print('OK [k8-версия]')

rep(K8P,
    '> **Текущая версия кэша:** `kipia-v516`',
    '> **Текущая версия кэша:** `kipia-v517`', 'k8-кэш')
rep(K8P,
    'Формат: `kipia-test-v716` → `kipia-test-v717` (для kip8test) или '
    '`kipia-v516` → `kipia-v517` (для kip8)',
    'Формат: `kipia-test-v717` → `kipia-test-v718` (для kip8test) или '
    '`kipia-v516` → `kipia-v517` (для kip8)', 'k8-формат')
rep(K8P,
    '(`tests/`, 6128 тестов, 200 тест-файлов, `node tests/run-all.js`)',
    '(`tests/`, 6138 тестов, 201 тест-файл, `node tests/run-all.js`)',
    'k8-тесты')
rep(K8P,
    '# Ожидается: 6128 passed, 0 failed (kip8; в kip8test — 6124 '
    'passed, 0 failed)',
    '# Ожидается: 6138 passed, 0 failed (kip8; в kip8test — 6134 '
    'passed, 0 failed — Task 493 ПЕРЕНЕСЁН одним инкрементом '
    'kipia-v516→v517)', 'k8-ожидается')

# ================= kip8test (зеркало) =================
VER_T = (
    '> **Версия документа:** 2026-10-10 (post-Task 493 ПЕРЕНОС-зеркало: '
    'кнопка «Табель учёта рабочего времени» на главной (закрепление из '
    'SUBSECTIONS) и в «Документации ИОС» — короче «Табель учёта»; '
    'заголовок страницы/крошки/сайдбар — прежние полные имена), '
    'kip8test @e833ef2e (v717, 6134/0), по команде пользователя '
    '«Перенос в kip8» (в той же заявке) выкачана в боевой kip8 '
    '@d181482 ОДНИМ инкрементом SW kipia-v516→v517 (регламент '
    'Task 441): тесты kip8 6138/0 = 6128+10, SMOKE 16/16 (порт 9007, '
    'ключи БЕЗ префикса) + VLM ×4; DEPLOY-Task493 скопирован с '
    'kip8-адаптацией; kip8test — код уже выкачан, кэш kipia-test-v717. '
    'ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test @e833ef2e, SW `kipia-test-v717` '
    '(guard v718), тесты 6134/0; kip8 @d181482+docs, SW `kipia-v517` '
    '(guard v518), тесты 6138/0 — Task 493 ПЕРЕНЕСЁН, открытых '
    'хвостов нет; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: '
    '494.\n')

st = rd(K8TP)
first_ver_t = st.index('> **Версия документа:**')
line_end_t = st.index('\n', first_ver_t)
cur_t = st[first_ver_t:line_end_t]
cur_t_demoted = cur_t.replace('> **Версия документа:**',
                              '> **Версия документа (предыдущая):**', 1)
st = st[:first_ver_t] + VER_T + cur_t_demoted + st[line_end_t:]
wr(K8TP, st)
print('OK [k8t-версия]')

rep(K8TP,
    '> **Текущая версия кэша:** `kipia-test-v716`',
    '> **Текущая версия кэша:** `kipia-test-v717`', 'k8t-кэш')
rep(K8TP,
    'Формат: `kipia-test-v716` → `kipia-test-v717` (для kip8test) или '
    '`kipia-v515` → `kipia-v516` (для kip8)',
    'Формат: `kipia-test-v717` → `kipia-test-v718` (для kip8test) или '
    '`kipia-v516` → `kipia-v517` (для kip8)', 'k8t-формат')
rep(K8TP,
    '(`tests/`, 6124 тестов, 200 тест-файлов, `node tests/run-all.js`)',
    '(`tests/`, 6134 тестов, 201 тест-файл, `node tests/run-all.js`)',
    'k8t-тесты')
rep(K8TP,
    '# Ожидается: 6124 passed, 0 failed (kip8test; в kip8 — 6128 '
    'passed, 0 failed — партия 490/491/492 ПЕРЕНЕСЕНА в kip8 одним '
    'инкрементом kipia-v515→v516)',
    '# Ожидается: 6134 passed, 0 failed (kip8test; в kip8 — 6138 '
    'passed, 0 failed — Task 493 ПЕРЕНЕСЁН в kip8 одним инкрементом '
    'kipia-v516→v517)', 'k8t-ожидается')

print('\n===== UPDATE-PROMPT ЗАВЕРШЕН: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
