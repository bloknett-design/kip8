#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492-update-prompt: обновление промтов ОБОИХ репо после
# переноса партии 490+491+492 в kip8 (kipia-v515→v516).
# kip8: версия документа (новая строка + демotion текущей), кэш
# v516, формат v516→v517, тесты 6128/200 файлов, «Ожидается».
# kip8test: версия-зеркало переноса, «Ожидается» — kip8 6128/0,
# партия ПЕРЕНЕСЕНА.
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
VER8_NEW = ('> **Версия документа:** 2026-10-10 (post-Task 490-492 '
            'ПЕРЕНОС: партия «Датчики температуры» (Task 490 — '
            'мобильная сетка: кнопки-карточки по ДВЕ в строке, пары '
            'одинаковых градуировок рядом, ТХА (K)+ТХК (L) вместе, на '
            'кнопках ТС только градуировка + α, у ТП наименование с '
            'градуировкой; Task 491 — пары 50М+50М (α 0,00428/0,00426) '
            'и 100М+100М, автооткрытие вкладки «Избранное» при наличии '
            'избранного — датчики температуры + расходомеры '
            'хозрасчётные; Task 492 — табы «Все/Избранные» смещены '
            'ВНИЗ в фиксированный бар #tsBottomBar по образцу '
            'расходомеров, шрифт 19/12px (≤400px 17) у ВСЕХ '
            'кнопок-карточек, featured-выступ (рамка 2px + тень + '
            'градиент) — у кнопок В ИЗБРАННОМ) перенесена из '
            'kip8test@ae8cbd34 в боевой kip8 ОДНИМ инкрементом SW '
            'kipia-v515→v516 — команда из заявки: «Перенос в kip8»; '
            'КЛИЕНТ-ONLY (Apps Script не тронут); тесты kip8 '
            '6128/0 = 6069+59, SMOKE 41/41 (порт 9007, ключи БЕЗ '
            'префикса) + VLM ×4; 3-way merge 174 файла + 3 новых '
            'теста; шапки-посадки 483-486; окна истории — kip8-'
            'геометрия)\n')
s8 = rd(K8P)
first_ver = s8.index('> **Версия документа:**')
# демotion: текущая строка версии → «(предыдущая)»
line_end = s8.index('\n', first_ver)
cur = s8[first_ver:line_end]
cur_demoted = cur.replace('> **Версия документа:**',
                          '> **Версия документа (предыдущая):**', 1)
s8 = s8[:first_ver] + VER8_NEW + cur_demoted + s8[line_end:]
wr(K8P, s8)
print('OK [k8-версия]')

rep(K8P,
    '> **Текущая версия кэша:** `kipia-v515`',
    '> **Текущая версия кэша:** `kipia-v516`', 'k8-кэш')
rep(K8P,
    'Формат: `kipia-test-v710` → `kipia-test-v711` (для kip8test) или '
    '`kipia-v515` → `kipia-v516` (для kip8)',
    'Формат: `kipia-test-v716` → `kipia-test-v717` (для kip8test) или '
    '`kipia-v516` → `kipia-v517` (для kip8)', 'k8-формат')
rep(K8P,
    '(`tests/`, 6069 тестов, 197 тест-файлов, `node tests/run-all.js`)',
    '(`tests/`, 6128 тестов, 200 тест-файлов, `node tests/run-all.js`)',
    'k8-тесты')
rep(K8P,
    '# Ожидается: 6069 passed, 0 failed (kip8; в kip8test — 6065 '
    'passed, 0 failed)',
    '# Ожидается: 6128 passed, 0 failed (kip8; в kip8test — 6124 '
    'passed, 0 failed)', 'k8-ожидается')

# ================= kip8test (зеркало) =================
VER_T = ('> **Версия документа:** 2026-10-10 (post-Task 490-492 '
         'ПЕРЕНОС-зеркало: партия «Датчики температуры» (Task 490 — '
         'мобильная сетка 2-в-ряд; Task 491 — пары 50М+50М/100М+100М + '
         'автотаб «Избранное»; Task 492 — нижний бар табов + единый '
         'крупный шрифт + feat=избранное), kip8test @ae8cbd34 '
         '(v716, 6124/0), по команде пользователя «Перенос в kip8» '
         'выкачана в боевой kip8 ОДНИМ инкрементом SW kipia-v515→v516 '
         '(регламент Task 441): тесты kip8 6128/0 = 6069+59, SMOKE '
         '41/41 + VLM ×4, 3-way merge 174 файла (7 конфликтов — '
         'окна/данные/шапки, keep-ours + пост-патч), DEPLOY-Task490/'
         '491/492 скопированы с kip8-адаптацией; kip8test — БЕЗ '
         'изменений кода, кэш kipia-test-v716)\n')
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
    '# Ожидается: 6124 passed, 0 failed (kip8test; в kip8 — 6069 '
    'passed, 0 failed — Tasks 490/491/492 НЕ переносились)',
    '# Ожидается: 6124 passed, 0 failed (kip8test; в kip8 — 6128 '
    'passed, 0 failed — партия 490/491/492 ПЕРЕНЕСЕНА в kip8 одним '
    'инкрементом kipia-v515→v516)', 'k8t-ожидается')

print('\n===== UPDATE-PROMPT ЗАВЕРШЕН: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
