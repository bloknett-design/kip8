#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 475-477-transfer: перенос ПАРТИИ этапов 1-3 ОПТИМИЗАЦИИ из
# kip8test (@5374d401 Task 475 + @24eafb5f Task 476 + @2e6fa4d3 Task
# 477 + @21745f16 фикс тест-скрипта) в боевой kip8 ОДНИМ инкрементом
# SW kipia-v509 → v510 (регламент Task 441: партия = один инкремент;
# команда пользователя «этап 4 не выполнять, перенеси все последние
# изменения в боевой kip8»).
# Состав партии:
#   Task 475 — ЭТАП 1: SWR App Shell + персистентный DATA-кэш
#              data/*.json + офлайн-ветка входа (гостевой режим,
#              автоповтор) + сжатие logo/logo_black/Launch (~3.4 МБ);
#   Task 476 — ЭТАП 2: KipDB (IndexedDB) — двухслойный кэш серверных
#              данных (табель/каб. журнал/расходомеры/отметки
#              мероприятий) + storage.persist() + чистка при logout;
#   Task 477 — ЭТАП 3: KipPreload — фоновая предзагрузка всех данных
#              ПО ПРАВАМ РОЛИ (idle-очередь, по одному, паузы ≥1.5 с;
#              saveData/2g — пропуск).
# КЛИЕНТ-ONLY: .gs не тронуты (Apps Script без изменений).
# Метод (Task 292/401-406/429/437/441-474): де-изоляция + «дифф
# диффов». Якоря де-изоляции index.html: 15 из task473-474-transfer.py
# + 2 НОВЫХ (KipDB: имя БД + комментарий — партия их добавила).
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях (475/476/477
# подключены / v510 установлен) — лечение: git checkout -- . + rm
# новых файлов партии (DEPLOY-Task47[567]-*.md, scripts/
# task475-477-transfer.py) и один чистый прогон (подводный камень
# Task 471).
import io
import os
import re
import subprocess
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
assert os.path.isdir(K8T), 'репо kip8test не найдено: %s' % K8T

V_TEST = 'kipia-test-v'
fail = []


def chk(cond, msg):
    if cond:
        print('OK: %s' % msg)
    else:
        fail.append(msg)
        print('FAIL: %s' % msg)


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo] + list(args),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('git %s: %s' % (args, r.stderr[:400]))
    return r.stdout


def diff_lines(a_path, b_path, drop=None):
    r = subprocess.run(['diff', a_path, b_path],
                       capture_output=True, text=True)
    lines = [ln for ln in r.stdout.splitlines()
             if ln.startswith('<') or ln.startswith('>')]
    if drop:
        lines = [ln for ln in lines
                 if not any(p in ln for p in drop)]
    return lines


# ============================================================
# 0. База партии: kip8test@b1dfe3b3 (Task 473-474 ПЕРЕНОС —
#    состояние, синхронное kip8@7a2412c; далее 5374d401 (475) +
#    24eafb5f (476) + 2e6fa4d3 (477) + 21745f16 (фикс тест-скрипта)
#    — партия) ↔ kip8@HEAD (7a2412c — Task 473-474 ПЕРЕНОС docs)
# ============================================================
BASE_T = 'b1dfe3b3'
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '21745f16',
    'база: kip8test HEAD = %s (партия 475-477, ожидался 21745f16)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '7a2412c',
    'база: kip8 HEAD = %s (ожидался 7a2412c — Task 473-474 ПЕРЕНОС)'
    % HEAD_8)

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (15 якорей из
#    task473-474-transfer.py — партия изоляцию не трогала; + 2 НОВЫХ
#    якоря KipDB: имя БД kip8-cache-test-v1 и комментарий к нему)
# ============================================================
print('=== 1. index.html ===')
src = rd(os.path.join(K8T, 'index.html'))
orig = src


def rep1(old, new, tag, cnt=1):
    global src
    n = src.count(old)
    if n != cnt:
        fail.append('[index %s] вхождений %d, ожидалось %d' % (tag, n, cnt))
        print('FAIL [index %s]: вхождений %d, ожидалось %d' % (tag, n, cnt))
        return
    src = src.replace(old, new)
    print('OK [index %s]' % tag)


# 1.1 Комментарий Task 243 (transform)
rep1(
    '/* Task 243 (бекпорт из kip8): !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} (specificity '
    '#sidebar.active (1,1,0) > #sidebar (1,0,0)). В kip8test wsTrSheet уже '
    'правильно закрыт, но !important оставлен для надёжности и паритета '
    'с kip8 — чтобы при следующем переносе kip8test → kip8 не потерять '
    'фикс. */',
    '/* Task 243: !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} (specificity '
    '#sidebar.active (1,1,0) > #sidebar (1,0,0)) — фикс бага «hamburger не '
    'открывает sidebar на 377px viewport». Task 244: корневая причина — '
    'wsTrSheet не был закрыт, sidebar оказывался вложенным в него '
    '(position:fixed относительно wsTrSheet, имевшего transform). В kip8test '
    'wsTrSheet уже правильно закрыт, но !important оставлен для '
    'надёжности. */',
    'task243-transform')

# 1.2 Комментарий Task 243 (overlay)
rep1('/* Task 243 (бекпорт): то же самое для overlay */',
     '/* Task 243: то же самое для overlay */', 'task243-overlay')

# 1.3 Комментарий про ключи localStorage (2 строки)
rep1(
    '    // (в тестовом репо ключ автоматически получает префикс kip8test:\n'
    '    // через isolateLocalStorage). При первом запуске победы из старого',
    '    // (kip8 — основной репозиторий, ключи без префикса). При первом\n'
    '    // запуске победы из старого',
    'ls-comment')

# 1.4-1.6 Ключи телефонного справочника
rep1("'kip8test_phonebook_favorites'", "'kip8_phonebook_favorites'",
     'pb-fav')
rep1("'kip8test_phonebook_notes'", "'kip8_phonebook_notes'", 'pb-notes')
rep1("'kip8test_phonebook_cache'", "'kip8_phonebook_cache'",
     'pb-cache', 2)

# 1.7 Ключ кэша приборов
rep1("const DEV_CACHE_KEY = 'kip8test_devices_cache';",
     "const DEV_CACHE_KEY = 'kip8_devices_cache';", 'dev-cache-key')

# 1.8-1.10 Обращения к кэшу приборов без префикса
rep1("localStorage.setItem('kip8test:' + DEV_CACHE_KEY, "
     "JSON.stringify(devData));",
     "localStorage.setItem(DEV_CACHE_KEY, JSON.stringify(devData));",
     'dev-set')
rep1("localStorage.getItem('kip8test:' + DEV_CACHE_KEY)",
     "localStorage.getItem(DEV_CACHE_KEY)", 'dev-get')
rep1("localStorage.setItem('kip8test:' + DEV_CACHE_KEY, "
     "JSON.stringify(fresh));",
     "localStorage.setItem(DEV_CACHE_KEY, JSON.stringify(fresh));",
     'dev-set-fresh')

# 1.11 Удаление блока isolateLocalStorage (только kip8test)
ISO_BLOCK = (
    '    // ===== ТЕСТОВЫЙ РЕПОЗИТОРИЙ kip8test: изоляция localStorage =====\n'
    '    // localStorage общий для всего origin (bloknett-design.github.io).\n'
    '    // Чтобы настройки (тема, метод калибровки буя) из тестового '
    'репозитория\n'
    '    // не влияли на основной репозиторий kip8, добавляем префикс ко '
    'всем ключам.\n'
    '    // В основном репозитории kip8 этот блок ОТСУТСТВУЕТ — там ключи '
    'без префикса.\n'
    '    (function isolateLocalStorage() {\n'
    "        const PREFIX = 'kip8test:';\n"
    '        const origGetItem = localStorage.getItem.bind(localStorage);\n'
    '        const origSetItem = localStorage.setItem.bind(localStorage);\n'
    '        const origRemoveItem = '
    'localStorage.removeItem.bind(localStorage);\n'
    '        localStorage.getItem = function(key) '
    "{ return origGetItem(PREFIX + key); };\n"
    '        localStorage.setItem = function(key, value) '
    "{ return origSetItem(PREFIX + key, value); };\n"
    '        localStorage.removeItem = function(key) '
    "{ return origRemoveItem(PREFIX + key); };\n"
    '    })();\n'
)
rep1(ISO_BLOCK, '', 'isolate-block-remove')

# 1.12 Комментарий #page-id
rep1('// Если URL содержит #page-id (например, /kip8test/#exam-tickets),',
     '// Если URL содержит #page-id (например, /kip8/#exam-tickets),',
     'page-id')

# 1.13 Комментарий URL Apps Script (5-6 строк)
rep1(
    '        // URL Apps Script Web App.\n'
    '        // Task 284: URL развёртывания пользователя (AKfycbyt…) — пробы\n'
    '        // 2026-09-01 подтвердили: проект полный (Auth/Sessions/Admin/\n'
    '        // CableJournal/Flowmeter/ValidationRules/WorkSchedule) и код\n'
    '        // свежий (роутинг отпусков есть). Прежний URL (AKfycbzg…,\n'
    '        // Task 202) остался на старом снимке кода — до Task 274.',
    '        // URL Apps Script Web App (развёртывание AKfycbyt…, в kip8 с\n'
    '        // Task 245). Пробы 2026-09-01 (Task 284 в kip8test) '
    'подтвердили:\n'
    '        // проект полный (Auth/Sessions/Admin/CableJournal/Flowmeter/\n'
    '        // ValidationRules/WorkSchedule) и код свежий — роутинг '
    'отпусков\n'
    '        // (Task 274+) есть. kip8test синхронизирован с этим же URL.',
    'url-comment')

# 1.14 Комментарий Task 242
rep1(
    '        // Task 242 (бекпорт из kip8): усиление обновления SW — вместе '
    'с\n'
    '        // skipWaiting() в sw.js и reg.update() сразу при загрузке.',
    '        // Task 242: усиление обновления SW — вместе с skipWaiting() '
    'в sw.js\n'
    '        // и reg.update() сразу при загрузке.',
    'task242')

# 1.15 Комментарий реестра Task 458
rep1(
    '        // ключ localStorage ws_auto_dn_keys (префикс репозитория\n'
    '        // ставит isolateLocalStorage)\n',
    '        // ключ localStorage ws_auto_dn_keys (в тестовом репо\n'
    '        // ключ автоматически получает префикс)\n',
    'auto-dn-keys-comment')

# 1.16 НОВЫЙ якорь партии: имя БД KipDB + комментарий (Task 476)
rep1(
    "    // Имя БД kip8test; перенос в kip8 → 'kip8-cache-v1' (маппинг\n"
    "    // де-изоляции, как IMAGE_CACHE_VERSION kipia-images-*-v3)\n"
    "    var DB_NAME = 'kip8-cache-test-v1';",
    "    // Имя БД kip8 — основной репозиторий (в kip8test — "
    "'kip8-cache-test-v1';\n"
    "    // маппинг де-изоляции переносов, как IMAGE_CACHE_VERSION "
    "kipia-images-*-v3)\n"
    "    var DB_NAME = 'kip8-cache-v1';",
    'kipdb-name')

assert src != orig, 'index.html: ни одной трансформации не применилась'
# 5 исторических (Task 243 / Task 284 ×2 / «проект на kip8 и kip8test» /
# PlanEventsData-комментарий) + 1 новый исторический (комментарий KipDB
# «в kip8test — 'kip8-cache-test-v1'») = 6
chk(src.count('kip8test') == 6,
    'index.html: упоминаний kip8test после де-изоляции = 6 '
    '(5 исторических + 1 комментарий KipDB о маппинге): %d'
    % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))
chk("var DB_NAME = 'kip8-cache-v1';" in src,
    'index.html: DB_NAME = kip8-cache-v1 (Task 476)')
chk(src.count("'kip8-cache-test-v1'") == 1,
    'index.html: kip8-cache-test-v1 ровно 1 — в комментарии маппинга '
    '(де-изоляция): %d' % src.count("'kip8-cache-test-v1'"))

# Маркеры партии 475-477 (index.html)
for m in ('Task 475', 'Task 476', 'Task 477'):
    chk(m in src, 'index.html: маркер %r присутствует' % m)
for m in ('var KipDB = (function() {',          # 476: модуль
          'var KipPreload = (function() {',     # 477: модуль
          '_startOfflineTokenRetry',            # 475: офлайн-вход
          'resetSectionDataCache',              # 475: сброс in-memory
          "DATA_REFRESHED",                     # 475: слушатель SW
          '_wipeLocalServerData',               # 476: чистка logout
          '_requestPersistentStorage',          # 476: storage.persist
          '_schedulePreload',                   # 477: запуск preload
          "kip8_pe_marks_v1",                   # 476: копия отметок
          'Нет связи с сервером — открыт гостевой режим',  # 475: тост
          'Вход восстановится автоматически',   # 475: продолжение тоста
          'Данные обновлены'):                  # 475: тост SWR
    chk(m in src, 'index.html: маркер партии %r' % (m[:44],))
# Живые задачи прошлых партий — не размыло переносом
for m in ('<textarea id="peWorkInput" class="pe-works-input" rows="1"',
          'id="pePrevYearBtn"', 'var PlanWorksData = {'):
    chk(m in src, 'index.html: якорь живой задачи %r' % (m[:44],))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» (с фильтром НОВЫХ якорей KipDB:
#     их нет в базовом репо-диффе — партия их добавила) ---
DB_FILTER = ['kip8-cache', 'Имя БД', 'де-изоляции']
base_t = '/tmp/k8t-index-base475.html'
base8 = '/tmp/k8-index-base475.html'
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', BASE_T + ':index.html'))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
d_new = diff_lines(k8_index_new, os.path.join(K8T, 'index.html'), DB_FILTER)
d_base = diff_lines(base8, base_t, DB_FILTER)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d; якоря KipDB отфильтрованы — проверены отдельно)'
    % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new, DB_FILTER)
d_taskT = diff_lines(base_t, os.path.join(K8T, 'index.html'), DB_FILTER)
chk(d_task8 == d_taskT,
    'index.html: дифф задач (475-477) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. sw.js — шапка kip8 (полная история задач) + комментарий
#    партии + v510; ТЕЛО из kip8test (код SWR/DATA-кэша идентичен,
#    кодовые различия баз = только версии кэшей)
# ============================================================
print('=== 2. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1,
    'sw.js (kip8): якорь IMAGE_CACHE_VERSION найден')
chk(swt.count(ANCHOR_IMG_T) == 1,
    'sw.js (kip8test): якорь IMAGE_CACHE_VERSION найден')
head8 = sw8[:sw8.index(ANCHOR_IMG_8) + len(ANCHOR_IMG_8)]
body_t = swt[swt.index(ANCHOR_IMG_T) + len(ANCHOR_IMG_T):]

# Де-изоляция тела: персистентный DATA-кэш без -test-
n_data = body_t.count("'kipia-data-test-v1'")
chk(n_data == 1,
    'sw.js (тело): kipia-data-test-v1 вхождений 1 (%d)' % n_data)
body_t = body_t.replace("'kipia-data-test-v1'", "'kipia-data-v1'")
chk('kip8test' not in body_t and V_TEST not in body_t,
    'sw.js (тело): тест-специфики не осталось')

# Комментарий партии в шапке kip8 (перед CACHE_VERSION) + бамп v509→v510
COMMENT = (
    '// Task 475-477 (перенос партии из kip8test@21745f16; этапы 1-3\n'
    '// оптимизации): Task 475 — SWR: навигация (App Shell) и локальные\n'
    '// ассеты из кэша СРАЗУ, сеть догружает фоном; data/*.json — в\n'
    '// персистентном DATA_CACHE_NAME (переживает инкременты; при\n'
    '// изменении содержимого — DATA_REFRESHED вкладкам); офлайн-ветка\n'
    '// входа (index.html: гостевой режим + автоповтор); logo/logo_black\n'
    '// сжаты 2048→256px и в ASSETS. Task 476 — KipDB (IndexedDB) в\n'
    '// index.html: кэш серверных данных (табель/каб. журнал/\n'
    '// расходомеры/отметки мероприятий) рядом с localStorage +\n'
    '// storage.persist() + чистка копий при logout. sw.js логики\n'
    '// не менял (кэш статический) — только версия.\n'
    '// Task 477 (этап 3 оптимизации): KipPreload в index.html — фоновая\n'
    '// предзагрузка всех данных ПО ПРАВАМ РОЛИ (idle-очередь по одному,\n'
    '// паузы ≥1.5 с; saveData/2g — пропуск; sw.js логики не менял —\n'
    '// только версия).\n'
)
old_v = "const CACHE_VERSION = 'kipia-v509';"
new_v = "const CACHE_VERSION = 'kipia-v510';"
chk(head8.count(old_v) == 1,
    'sw.js: CACHE_VERSION v509 найден в шапке (%d)' % head8.count(old_v))
head8 = head8.replace(old_v, COMMENT + new_v)
chk(head8.count(new_v) == 1, 'sw.js: v510 установлен в шапке')

sw_new = head8 + body_t
wr(P_SW, sw_new)

# Тело sw.js: код после IMAGE_CACHE_VERSION идентичен kip8test HEAD
# (единственная допустимая разница — де-изоляция kipia-data-test-v1;
# шапки репо исторически разные — полная история kip8 против
# сокращённой kip8test, это НОРМА переносов, не проверяется)
# Проверка выполняется НИЖЕ (после записи p8n/ptn на диск).

# Проверки содержимого
for m in ("const CACHE_VERSION = 'kipia-v510';",
          "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'function notifyDataChanged',
          "'./images/logo.png',        // Task 475",
          "'./images/logo_black.png',  // Task 475",
          'STALE-WHILE-REVALIDATE',
          'includeUncontrolled: true'):
    chk(m in sw_new, 'sw.js: маркер %r' % (m[:44],))
chk(sw_new.count('kipia-v510') == 1,
    'sw.js: kipia-v510 ровно один (%d)' % sw_new.count('kipia-v510'))
chk('kipia-v509' not in sw_new, 'sw.js: kipia-v509 не осталось')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = базовые исторические шапки kip8 + 1 '
    'перенос-метка партии (%d против %d+1)'
    % (sw_new.count('kip8test'), sw8.count('kip8test')))

# Окна истории версий (тесты kip8 скопированы с окнами kip8test):
# дистанции kip8 не должны превысить окна 5300/2700/2100/1700
i_new_v = sw_new.index(new_v)
for task_no, window in ((461, 5300), (471, 2700), (472, 2100), (474, 1700)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window,
        'sw.js: дистанция до комментария Task %d = %d (< %d — окно '
        'test-task%d, запас %d)' % (task_no, dist, window, task_no,
                                    window - dist))

# Верификация sw.js (шапки репо исторически разные — полная история
# kip8 против сокращённой kip8test, поэтому «дифф диффов» здесь
# неприменим; вместо него — ДВА инварианта):
# (1) ТЕЛО после IMAGE_CACHE_VERSION идентично kip8test HEAD
#     (кроме де-изоляции kipia-data-test-v1 — новый якорь партии);
# (2) шапка kip8 = прежняя шапка kip8 + комментарий партии + v510
#     (история задач kip8 не размыта — проверено маркерами ниже).
sw8_base = git(K8, 'show', 'HEAD:sw.js')
p8n, ptn = '/tmp/k8-sw-new475.js', '/tmp/k8t-sw-head475.js'
for p, s in ((p8n, sw_new), (ptn, swt)):
    wr(p, s)

# (1) тело: от IMAGE-якоря до конца файла
body_new = sw_new[sw_new.index(ANCHOR_IMG_8):]
body_head = swt[swt.index(ANCHOR_IMG_T):]
pbn, pbh = '/tmp/k8-sw-body-new.js', '/tmp/k8t-sw-body-head.js'
for p, s in ((pbn, body_new), (pbh, body_head)):
    wr(p, s)
d_body = diff_lines(pbn, pbh, ['kipia-data', 'kipia-images'])
chk(d_body == [],
    'sw.js: ТЕЛО идентично kip8test HEAD (от IMAGE-якоря, %d строк '
    'расхождений после фильтра kipia-data)' % len(d_body))

# (2) шапка: прежняя шапка kip8 не размыта (базовые строки на месте,
#     COMMENT вставлен перед CACHE_VERSION, v509→v510)
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')
chk(old_v not in sw_new and COMMENT in sw_new,
    'sw.js: v509 заменён на v510, комментарий партии вставлен')

# ============================================================
# 3. images/ — сжатые картинки Task 475 (бинарная копия)
# ============================================================
print('=== 3. images/ ===')
import shutil
for img, max_kb in (('logo.png', 60), ('logo_black.png', 60),
                    ('Launch.png', 400)):
    src_img = os.path.join(K8T, 'images', img)
    dst_img = os.path.join(K8, 'images', img)
    shutil.copyfile(src_img, dst_img)
    kb = os.path.getsize(dst_img) // 1024
    chk(kb <= max_kb and kb > 0,
        'images/%s: %d КБ (порог %d КБ; было 1450/1450/996)'
        % (img, kb, max_kb))
    chk(os.path.getsize(src_img) == os.path.getsize(dst_img),
        'images/%s: байт-в-байт с kip8test' % img)

# ============================================================
# 4. tests/ — копия всех test-*.js из kip8test с MAP + fixes
# ============================================================
print('=== 4. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (партия 475-477 — в kip8 ОДИН инкремент v509→v510)
    ('kipia-test-v701', 'kipia-v510'),
    # guards следующей версии
    ('kipia-test-v702', 'kipia-v511'),
    # негативы партии + шапки: версии ДО партии в kip8 = v509
    # (475: «не осталось v698»; 476: v699; 477: v700 — в kip8 все
    #  промежуточные версии партии не существуют, «до партии» = v509)
    ('kipia-test-v700', 'kipia-v509'),
    ('kipia-test-v699', 'kipia-v509'),
    ('kipia-test-v698', 'kipia-v509'),
    # партия прошлого переноса 473-474: «до партии» = v508
    ('kipia-test-v697', 'kipia-v508'),
    ('kipia-test-v696', 'kipia-v508'),
    # исторические негативы (маппинг переносов 472/471/470/469/468/467/
    # 466/465 — как в task473-474-transfer.py)
    ('kipia-test-v695', 'kipia-v507'),
    ('kipia-test-v694', 'kipia-v506'),
    ('kipia-test-v693', 'kipia-v505'),
    ('kipia-test-v692', 'kipia-v504'),
    ('kipia-test-v691', 'kipia-v503'),
    ('kipia-test-v690', 'kipia-v502'),
    ('kipia-test-v689', 'kipia-v501'),
    ('kipia-test-v687', 'kipia-v499'),
    ('kipia-test-v685', 'kipia-v498'),
    ('kipia-test-v684', 'kipia-v498'),
    ('kipia-test-v683', 'kipia-v498'),
    ('kipia-test-v681', 'kipia-v496'),
    ('kipia-test-v680', 'kipia-v495'),
    ('kipia-test-v679', 'kipia-v494'),
    ('kipia-test-v665', 'kipia-v481'),
    ('kipia-test-v663', 'kipia-v478'),
    ('kipia-test-v660', 'kipia-v478'),
    ('kipia-test-v642', 'kipia-v478'),
    ('kipia-test-v641', 'kipia-v478'),
    ('kipia-test-v640', 'kipia-v478'),
    ('kipia-test-v634', 'kipia-v478'),
    # кэши kip8 (без -test-)
    ('kipia-images-test-v3', 'kipia-images-v3'),
    ('kip8-cache-test-v1', 'kip8-cache-v1'),
    ('kipia-data-test-v1', 'kipia-data-v1'),
]
tot = {}
changed = 0
for name in sorted(os.listdir(TDIR_T)):
    if not name.startswith('test-') or not name.endswith('.js'):
        continue
    s = rd(os.path.join(TDIR_T, name))
    for old, new in MAP:
        if old in s:
            tot[old] = tot.get(old, 0) + s.count(old)
            s = s.replace(old, new)
    dst = os.path.join(TDIR_8, name)
    if not os.path.exists(dst) or rd(dst) != s:
        wr(dst, s)
        changed += 1
print('  test-*.js: скопировано с маппингом, изменено на диске %d' % changed)
for old, new in MAP:
    print('  %s → %s: %d замен' % (old, new, tot.get(old, 0)))
chk(tot.get('kipia-test-v701', 0) > 150,
    'тесты: текущие ассерты v701 → v510 перекрыты (%d)'
    % tot.get('kipia-test-v701', 0))
chk(tot.get('kipia-test-v702', 0) > 100,
    'тесты: guards v702 → v511 перекрыты (%d)'
    % tot.get('kipia-test-v702', 0))
for v, tag in (('kipia-test-v698', '475'), ('kipia-test-v699', '476'),
               ('kipia-test-v700', '477')):
    chk(tot.get(v, 0) == 3,
        'тесты: негатив партии %s %s → v509 три (шапка + assert + '
        'сообщение, %d)' % (tag, v, tot.get(v, 0)))
chk(tot.get('kipia-images-test-v3', 0) >= 2,
    'тесты: кэш картинок kipia-images-test-v3 → v3 перекрыт (%d)'
    % tot.get('kipia-images-test-v3', 0))
chk(tot.get('kip8-cache-test-v1', 0) == 3,
    'тесты: kip8-cache-test-v1 → kip8-cache-v1 три (476: тест БД + '
    '2 ассерта, %d)' % tot.get('kip8-cache-test-v1', 0))
chk(tot.get('kipia-data-test-v1', 0) == 3,
    'тесты: kipia-data-test-v1 → kipia-data-v1 три (475: шапка + '
    'assert + сообщение, %d)' % tot.get('kipia-data-test-v1', 0))

# --- 4.1 Точечные fixes: шапки «SW: ...» партии (MAP схлопнул оба
#     конца строки в v509 → v509) и тест БД в 476 ---
p475 = os.path.join(TDIR_8, 'test-task475.js')
chk(os.path.exists(p475), 'test-task475.js скопирован в kip8')
s475 = rd(p475)
fixes475 = [
    ('//   SW: kipia-v509 → v699.', '//   SW: kipia-v509 → v510.'),
]
for old_f, new_f in fixes475:
    chk(s475.count(old_f) == 1,
        'test-task475.js: якорь %r найден (%d)'
        % (old_f[:40], s475.count(old_f)))
    s475 = s475.replace(old_f, new_f)
wr(p475, s475)
for m in ("CACHE_VERSION = 'kipia-v510'", "indexOf('kipia-v509') === -1",
          'kipia-v511', "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'SW: kipia-v509 → v510', 'notifyDataChanged',
          'resetSectionDataCache', '_startOfflineTokenRetry'):
    chk(m in s475, 'test-task475.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s475,
    'test-task475.js: kip8test-версий не осталось')

p476 = os.path.join(TDIR_8, 'test-task476.js')
chk(os.path.exists(p476), 'test-task476.js скопирован в kip8')
s476 = rd(p476)
fixes476 = [
    ('//   SW: kipia-v509 → v700 (логика sw.js не менялась — статический',
     '//   SW: kipia-v509 → v510 (логика sw.js не менялась — статический'),
    # тест БД: kip8-вариант (де-изоляция DB_NAME)
    ("    test('имя БД kip8test с миграцией в kip8', () => {\n"
     '        const i = INDEX_SRC.indexOf("var DB_NAME = '
     "'kip8-cache-v1';\");\n"
     "        assertTrue(i !== -1, 'DB_NAME = kip8-cache-v1');\n"
     '        assertTrue(INDEX_SRC.slice(i - 200, i).indexOf("'
     "kip8 → 'kip8-cache-v1'\") !== -1,\n"
     "            'комментарий о маппинге имени при переносе в kip8');\n"
     '    });',
     "    test('имя БД kip8 (без -test-)', () => {\n"
     '        const i = INDEX_SRC.indexOf("var DB_NAME = '
     "'kip8-cache-v1';\");\n"
     "        assertTrue(i !== -1, 'DB_NAME = kip8-cache-v1');\n"
     '        assertTrue(INDEX_SRC.slice(i - 200, i).indexOf("'
     "'kip8-cache-test-v1'\") !== -1,\n"
     "            'комментарий хранит имя тестового репо (маппинг "
     "переноса)');\n"
     '    });'),
]
for old_f, new_f in fixes476:
    chk(s476.count(old_f) == 1,
        'test-task476.js: якорь %r найден (%d)'
        % (old_f[:40], s476.count(old_f)))
    s476 = s476.replace(old_f, new_f)
wr(p476, s476)
for m in ("CACHE_VERSION = 'kipia-v510'", "indexOf('kipia-v509') === -1",
          'kipia-v511', "var DB_NAME = 'kip8-cache-v1';",
          'SW: kipia-v509 → v510', '_wipeLocalServerData',
          '_requestPersistentStorage', 'mkFakeIdb',
          '_restoreFromObj', '_idbRestoreView'):
    chk(m in s476, 'test-task476.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s476,
    'test-task476.js: kip8test-версий не осталось')
chk('kip8-cache-test-v1' in s476,
    'test-task476.js: тест БД хранит имя тестового репо (маппинг)')

p477 = os.path.join(TDIR_8, 'test-task477.js')
chk(os.path.exists(p477), 'test-task477.js скопирован в kip8')
s477 = rd(p477)
fixes477 = [
    ('//   SW: kipia-v509 → v701 (логика sw.js не менялась —',
     '//   SW: kipia-v509 → v510 (логика sw.js не менялась —'),
]
for old_f, new_f in fixes477:
    chk(s477.count(old_f) == 1,
        'test-task477.js: якорь %r найден (%d)'
        % (old_f[:40], s477.count(old_f)))
    s477 = s477.replace(old_f, new_f)
wr(p477, s477)
chk('SW: kipia-v509 → v510' in s477,
    'test-task477.js: шапка «SW: kipia-v509 → v510» после фикса')
for m in ("CACHE_VERSION = 'kipia-v510'", "indexOf('kipia-v509') === -1",
          'kipia-v511', 'var KipPreload = (function() {',
          'canAccess: function', '_schedulePreload', 'saveData'):
    chk(m in s477, 'test-task477.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s477,
    'test-task477.js: kip8test-версий не осталось')

# --- 4.2 Точечные fixes test-task474 (ПОВТОР переносов прошлой
#     партии: MAP не разруливает короткие хвосты «v698/v699») ---
p474 = os.path.join(TDIR_8, 'test-task474.js')
s474 = rd(p474)
fixes474 = [
    ('//   SW: kipia-v508 → v698.', '//   SW: kipia-v508 → v509.'),
    ("'текущая версия v698'", "'текущая версия v509'"),
    ('версия до партии (v697) отсутствует',
     'версия до партии (v508) отсутствует'),
    ('v699 в sw.js отсутствует', 'v510 в sw.js отсутствует'),
]
for old_f, new_f in fixes474:
    chk(s474.count(old_f) == 1,
        'test-task474.js: якорь адаптации %r найден (%d)'
        % (old_f[:40], s474.count(old_f)))
    s474 = s474.replace(old_f, new_f)
wr(p474, s474)
chk('kipia-test-v' not in s474,
    'test-task474.js: kip8test-версий не осталось')

# --- 4.3 Остатки kipia-test-v6xx в kip8 после маппинга ---
hist = {}
for name in sorted(os.listdir(TDIR_8)):
    if not name.startswith('test-'):
        continue
    for ln in rd(os.path.join(TDIR_8, name)).splitlines():
        if V_TEST in ln:
            for m in re.findall(r'kipia-test-v\d+', ln):
                hist[m] = hist.get(m, 0) + 1
bad_hist = {k: v for k, v in hist.items()
            if int(k.rsplit('v', 1)[1]) >= 634}
chk(not bad_hist,
    'тесты kip8: незамапленные kipia-test-v6xx отсутствуют: %s' % bad_hist)
print('  исторические kipia-test-v* (общие, не тронуты): %s'
      % dict(sorted(hist.items())))

# --- 4.4 test-task344.js (kip8-специфичный) — бамп v509→v510 ---
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v509')
chk(n == 3, 'test-task344.js: ассертов kipia-v509 = 3 (%d)' % n)
s = s.replace('kipia-v509', 'kipia-v510')
wr(P344, s)

# --- 4.5 run-all.js (kip8) — + require 475/476/477 после 474 ---
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task474.js');\n"
B = ("require('./test-task474.js');\n"
     "require('./test-task475.js');\n"
     "// Task 476 — ЭТАП 2 ОПТИМИЗАЦИИ: KipDB (IndexedDB) — кэш "
     "серверных\n"
     "// данных (табель/каб. журнал/расходомеры/отметки мероприятий) "
     "рядом\n"
     "// с localStorage (квота ~5 МБ не режет копии) + storage.persist() "
     "+\n"
     "// чистка копий при logout.\n"
     "require('./test-task476.js');\n"
     "// Task 477 — ЭТАП 3 ОПТИМИЗАЦИИ: KipPreload — фоновая "
     "предзагрузка\n"
     "// всех данных ПО ПРАВАМ РОЛИ после входа (idle-очередь по "
     "одному,\n"
     "// паузы ≥1.5 с; статика через SWR + серверные копии в KipDB;\n"
     "// saveData/2g — пропуск; logout — стоп).\n"
     "require('./test-task477.js');\n")
chk(s.count(A) == 1, "run-all.js: якорь test-task474 найден (%d)"
    % s.count(A))
chk('test-task475' not in s and 'test-task476' not in s and
    'test-task477' not in s,
    'run-all.js (kip8): 475/476/477 ещё не подключены')
s = s.replace(A, B)
for n_ in range(438, 477):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# --- 4.6 после всего: версии в тестах kip8 — семантика kip8 ---
left509 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v509')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v509' in rd(os.path.join(TDIR_8, name))}
chk(left509 == {'test-task475.js': 3, 'test-task476.js': 3,
                'test-task477.js': 3},
    'тесты kip8: kipia-v509 остался только в партии 475-477 (негатив '
    'assert+сообщение + шапка «v509 → v510»; в 474 шапка «v508 → v509» '
    'историческая — хвост без префикса kipia-): %s' % left509)
left508 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v508')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v508' in rd(os.path.join(TDIR_8, name))}
chk(left508 == {'test-task473.js': 1, 'test-task474.js': 3},
    'тесты kip8: kipia-v508 остался ТОЛЬКО в партии 473+474 прошлой '
    'партии (не размыто): %s' % left508)

# ============================================================
# 5. DEPLOY-доки партии — копия из kip8test (как есть: версии внутри
#    описывают историю kip8test-бампов, инструкция по откату общая)
# ============================================================
print('=== 5. DEPLOY-доки партии ===')
for dep in ('DEPLOY-Task475-optimization-stage1-swr-offline.md',
            'DEPLOY-Task476-optimization-stage2-idb-server-cache.md',
            'DEPLOY-Task477-optimization-stage3-preload-by-role.md'):
    wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
    chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: партия 475-477 (этапы 1-3 оптимизации) перенесена в kip8 '
    '(SW kipia-v510), клиент-only, серверных шагов нет')
