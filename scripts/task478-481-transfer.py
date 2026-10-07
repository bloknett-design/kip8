#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 478-481-transfer: перенос ПАРТИИ из kip8test (@74c13178 Task
# 478 + @48fd14f1 Task 479 + @59e26cce Task 480 + @0aa75018/@1bd17ef9/
# @e321b093 дополнения Task 480 + @22e25742/@0bee19f8/@819804ec
# авто-синки данных + @81dfdc42 Task 481) в боевой kip8 ОДНИМ
# инкрементом SW kipia-v510 → v511 (регламент Task 441: партия = один
# инкремент; команда пользователя «Всё работает, переноси все
# последние изменения в боевой kip8»).
# Состав партии:
#   Task 478 — ППР-индикация строки «Период ремонта» в карточке
#              прибора КИП ИОС: зелёный/красный (devPprStatusClass);
#   Task 479 — третий цвет «текущий месяц» (оранжево-золотистый
#              dev-ppr-warn) + те же цвета в столбце «Дата» табличного
#              вида (devices-table-desktop.js);
#   Task 480 — смена ID Google-таблицы «Перечень КИП ИОС рабочий.xlsx»
#              (в kip8test — 31 замена в 15 файлах; в kip8 — 27 в 14
#              файлах БЕЗ README.md: его в kip8 никогда не было;
#              данные из новой таблицы доставлены отдельным ручным
#              синком 4 sync-скриптов — см. chore-коммит);
#   Task 481 — вид ремонта «ТО»: сравнивается ТОЛЬКО ГОД даты
#              ремонта (текущий → зелёный, другой → красный).
# КЛИЕНТ-ONLY: .gs не тронуты (Apps Script без изменений);
# десктопы — CI-автосинк.
# Метод (Task 292/401-406/429/437/441-477): де-изоляция + «дифф
# диффов». Якоря де-изоляции index.html: те же 17 из
# task475-477-transfer.py (партия изоляцию не трогала).
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях (478-481 подключены
# в run-all / v511 установлен) — лечение: git checkout -- . + rm новых
# файлов партии (DEPLOY-Task47[89]/48[01]-*.md, scripts/
# task478-481-transfer.py) и один чистый прогон (подводный камень
# Task 471; «проверочные» перегоны — НЕ делать).
import io
import os
import re
import subprocess
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
assert os.path.isdir(K8T), 'репо kip8test не найдено: %s' % K8T

V_TEST = 'kipia-test-v'
OLD_ID = '1eUUwwulUvKUGWTgQ__XP-y7z1aEkt5Wy'
NEW_ID = '1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee'
NEW_URL = 'https://docs.google.com/spreadsheets/d/' + NEW_ID + '/edit'
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
# 0. База партии: kip8test@1a8dd4fe (кабельный авто-синк, ДО Task
#    478 — состояние, синхронное kip8@d7d9a2f) → партия кода до
#    @81dfdc42 (Task 481); авто-синки данных ПОСЛЕ него кода не
#    меняют. kip8@HEAD = d7d9a2f (5da84b8 docs post-475-477 +
#    d7d9a2f кабельный авто-синк).
# ============================================================
BASE_T = '1a8dd4fe'
BATCH_T = '81dfdc42'
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T in (BATCH_T, '819804ec', '0bee19f8', '22e25742'),
    'база: kip8test HEAD = %s (партия 478-481 + авто-синки данных)'
    % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == 'd7d9a2f',
    'база: kip8 HEAD = %s (ожидался d7d9a2f — post-475-477 docs + '
    'кабельный авто-синк)' % HEAD_8)
# авто-синки ПОСЛЕ партии не меняли кодовые файлы
for rel in ('index.html', 'sw.js', 'devices-table-desktop.js',
            'tests/run-all.js', 'tests/test-task478.js',
            'tests/test-task479.js', 'tests/test-task480.js',
            'tests/test-task481.js'):
    a = git(K8T, 'show', BATCH_T + ':' + rel)
    b = git(K8T, 'show', HEAD_T + ':' + rel)
    chk(a == b, 'киp8test: %s не менялся авто-синками (== @%s)' % (rel, BATCH_T))
chk(git(K8, 'show', HEAD_8 + ':index.html') ==
    git(K8, 'show', '5da84b8:index.html'),
    'киp8: index.html не менялся кабельным авто-синком (== @5da84b8)')

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (17 якорей из
#    task475-477-transfer.py; партия изоляцию не трогала)
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

# 1.16 Якорь партии 475-477: имя БД KipDB + комментарий (Task 476)
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

# Маркеры партии 478-481 (index.html; «Task 480»-метки в index.html
# НЕТ — правка 480 = 3 комментария источников с новым ID, без ярлыка)
for m in ('Task 478', 'Task 479', 'Task 481'):
    chk(m in src, 'index.html: маркер %r присутствует' % m)
for m in ('function devPprStatusClass',       # 478/479/481: функция
          'dev-ppr-ok',                        # 478: класс
          'dev-ppr-warn',                      # 479: третий цвет
          'dev-ppr-bad',                       # 478: класс
          'parseInt(m[1], 10) === now.getFullYear()',  # 481: правило года
          'тот же файл, что и для приборов'):   # 480: пояснение источника
    chk(m in src, 'index.html: маркер партии %r' % (m[:44],))
chk(src.count(NEW_ID) == 3,
    'index.html: новый ID таблицы ровно 3 (комментарии источников '
    'Task 480): %d' % src.count(NEW_ID))
chk(OLD_ID not in src, 'index.html: старого ID нет (Task 480)')
# Живые задачи прошлых партий — не размыло переносом
for m in ('<textarea id="peWorkInput" class="pe-works-input" rows="1"',
          'var KipDB = (function() {', 'var KipPreload = (function() {',
          '_schedulePreload', '_startOfflineTokenRetry'):
    chk(m in src, 'index.html: якорь живой задачи %r' % (m[:44],))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» (новых якорей партия не добавляла —
#     фильтр не нужен) ---
base_t = '/tmp/k8t-index-base478.html'
base8 = '/tmp/k8-index-base478.html'
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', BASE_T + ':index.html'))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
d_new = diff_lines(k8_index_new, os.path.join(K8T, 'index.html'))
d_base = diff_lines(base8, base_t)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d; якорей партия не добавляла)'
    % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new)
d_taskT = diff_lines(base_t, os.path.join(K8T, 'index.html'))
chk(d_task8 == d_taskT,
    'index.html: дифф задач (478-481) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. sw.js — шапка kip8 (полная история задач) + перенос-метка +
#    4 комментария партии Task 478/479/480/481 ИЗ kip8test ДОСЛОВНО
#    (окна 700/1400 и тексты ассертов test-task478/479/480/481
#    рассчитаны ровно на них) + v511; ЛОГИКА SW НЕ МЕНЯЛАСЬ —
#    ТЕЛО от IMAGE-якоря идентично kip8test HEAD
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

# Комментарии партии: от '// Task 478: карточка прибора' до CACHE_VERSION
C_START = '// Task 478: карточка прибора'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v705';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n') and
    BATCH_COMMENT.count('Task 478') == 1 and
    BATCH_COMMENT.count('Task 479') == 2 and
    BATCH_COMMENT.count('Task 480') == 1 and
    BATCH_COMMENT.count('Task 481') == 1,
    'sw.js: извлечены 4 комментария партии (478 ×1, 479 ×2 — ярлык +'
    ' «(десктоп, Task 479)», 480 ×1, 481 ×1), %d симв.'
    % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарий партии версионно-нейтрален')

# Перенос-метка kip8 (прецедент Task 470-477) + бамп v510→v511
MARK = '// Task 478-481 (перенос партии из kip8test@81dfdc42):\n'
old_v = "const CACHE_VERSION = 'kipia-v510';"
new_v = "const CACHE_VERSION = 'kipia-v511';"
chk(sw8.count(old_v) == 1,
    'sw.js: CACHE_VERSION v510 найден (%d)' % sw8.count(old_v))
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)

for m in (new_v, "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'STALE-WHILE-REVALIDATE', 'function notifyDataChanged'):
    chk(m in sw_new, 'sw.js: маркер %r' % (m[:44],))
chk(sw_new.count(new_v) == 1,
    'sw.js: kipia-v511 ровно один (%d)' % sw_new.count(new_v))
chk('kipia-v510' not in sw_new, 'sw.js: kipia-v510 не осталось')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = исторические шапки kip8 + 1 '
    'перенос-метка партии (%d против %d+1)'
    % (sw_new.count('kip8test'), sw8.count('kip8test')))
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')

# ТЕЛО: от IMAGE-якоря до конца файла идентично kip8test HEAD
# (единственные допустимые различия — версии персистентных кэшей)
pbn = '/tmp/k8-sw-body-new478.js'
pbh = '/tmp/k8t-sw-body-head478.js'
wr(pbn, sw_new[sw_new.index(ANCHOR_IMG_8):])
wr(pbh, swt[swt.index(ANCHOR_IMG_T):])
d_body = diff_lines(pbn, pbh, ['kipia-data', 'kipia-images'])
chk(d_body == [],
    'sw.js: ТЕЛО идентично kip8test HEAD (от IMAGE-якоря, %d строк '
    'расхождений после фильтра версий кэшей)' % len(d_body))

# Окна истории (окна из kip8test-тестов 461/471/472/474 — после
# расширений Task 478/481: 6800/4200/3600/3100)
i_new_v = sw_new.index(new_v)
for task_no, window in ((474, 3100), (472, 3600), (471, 4200), (461, 6800)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window,
        'sw.js: дистанция до комментария Task %d = %d (< %d — окно '
        'test-task%d, запас %d)' % (task_no, dist, window, task_no,
                                    window - dist))

# Комментарии партии в окнах тестов (ассерты test-task478/479/480/481)
w700 = sw_new[i_new_v - 700:i_new_v]
w1400 = sw_new[i_new_v - 1400:i_new_v]
chk(w700.count('Task 481') == 1 and 'ГОД' in w700 and
    'золотистого для ТО' in w700,
    'sw.js: комментарий Task 481 в окне 700 (правило года)')
chk(w700.count('Task 480') == 1 and NEW_ID in w700 and
    '«Перечень КИП ИОС рабочий.xlsx»' in w700 and
    '1291/531/320/268' in w700 and 'Логики SW не менял' in w700,
    'sw.js: комментарий Task 480 в окне 700 (новый ID таблицы)')
chk(w1400.count('Task 479') >= 1 and 'оранжево-золотистый' in w1400 and
    'dev-ppr-warn' in w1400 and 'столбце «Дата»' in w1400,
    'sw.js: комментарий Task 479 в окне 1400 (третий цвет)')
chk(w1400.count('Task 478') >= 1 and 'Период ремонта' in w1400 and
    'ЗЕЛЁНЫЙ' in w1400 and 'КРАСНЫЙ' in w1400,
    'sw.js: комментарий Task 478 в окне 1400 (цвета ППР)')

wr(P_SW, sw_new)

# ============================================================
# 3. devices-table-desktop.js — простая копия (базы обоих репо
#    идентичны с переноса Task 473-474; репо-специфики в модуле нет)
# ============================================================
print('=== 3. devices-table-desktop.js ===')
import shutil
src_mod = os.path.join(K8T, 'devices-table-desktop.js')
dst_mod = os.path.join(K8, 'devices-table-desktop.js')
mod = rd(src_mod)
chk(git(K8T, 'show', BASE_T + ':devices-table-desktop.js') ==
    git(K8, 'show', HEAD_8 + ':devices-table-desktop.js'),
    'devices-table: базы репо идентичны (BASE_T == kip8 HEAD)')
chk('kip8test' not in mod and V_TEST not in mod,
    'devices-table: репо-специфики нет')
for m in ('Task 479', 'Task 481', 'devPprStatusClass',
          'dev-ppr-ok', 'dev-ppr-warn', 'dev-ppr-bad', 'Дата'):
    chk(m in mod, 'devices-table: маркер партии %r' % (m[:44],))
shutil.copyfile(src_mod, dst_mod)

# ============================================================
# 4. Task 480: URL-замена в kip8-собственных файлах (sync-скрипты +
#    workflows + data + промт; index.html уже приехал копией;
#    README.md в kip8 НЕ существует — его никогда не было, в отличие
#    от kip8test, где он описывает изоляцию тестового репо)
# ============================================================
print('=== 4. Task 480: URL-замена ===')
URL_FILES = [
    # (путь, ожидаемое число замен старого ID)
    ('scripts/sync-devices.py', 3),
    ('scripts/sync-lockouts.py', 3),
    ('scripts/sync-valves.py', 3),
    ('scripts/sync-regulators.py', 3),
    ('.github/workflows/sync-devices.yml', 1),
    ('.github/workflows/sync-lockouts.yml', 1),
    ('.github/workflows/sync-valves.yml', 1),
    ('.github/workflows/sync-regulators.yml', 1),
    ('data/devices.json', 1),
    ('data/lockouts.json', 1),
    ('data/valves.json', 1),
    ('data/regulators.json', 1),
    ('Системный_промт_для_приложения_КИПиА.md', 4),
]
tot_url = 0
for rel, cnt in URL_FILES:
    p = os.path.join(K8, rel)
    s = rd(p)
    n = s.count(OLD_ID)
    if n != cnt:
        fail.append('[url %s] старый ID: %d, ожидалось %d' % (rel, n, cnt))
        print('FAIL [url %s]: старый ID %d, ожидался %d' % (rel, n, cnt))
        continue
    s = s.replace(OLD_ID, NEW_ID)
    wr(p, s)
    tot_url += n
    print('OK [url %s]: %d замен' % (rel, n))
chk(tot_url == 24,
    'Task 480: всего замен в kip8 = 24 (12 sync + 4 workflows + 4 data '
    '+ 4 промт; index.html — 3 из копии; README в kip8 нет): %d' % tot_url)
chk(not os.path.exists(os.path.join(K8, 'README.md')),
    'Task 480: README.md в kip8 отсутствует (норма — тест 480 '
    'адаптирован: README-тесты исключены)')
p_promt = os.path.join(K8, 'Системный_промт_для_приложения_КИПиА.md')
sp = rd(p_promt)
chk(sp.count('`' + NEW_ID + '`') == 4,
    'промт: 4 записи таблицы «Источники данных» с новым ID: %d'
    % sp.count('`' + NEW_ID + '`'))
i_sec = sp.index('### Источники данных')
j_sec = sp.index('###', i_sec + 10)
chk(OLD_ID not in sp[i_sec:j_sec],
    'промт: в секции «Источники данных» старого ID нет')

# ============================================================
# 5. tests/ — копия всех test-*.js из kip8test с MAP + точечные
#    fixes (партия 478-481 в kip8 = ОДИН инкремент v510→v511)
# ============================================================
print('=== 5. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (партия 478-481 — в kip8 ОДИН инкремент v510→v511)
    ('kipia-test-v705', 'kipia-v511'),
    # guards следующей версии
    ('kipia-test-v706', 'kipia-v512'),
    # негативы партии + шапки: все kip8test-версии партии (v701 до
    # v704 — «до партии» и промежуточные) в kip8 = v510
    ('kipia-test-v704', 'kipia-v510'),
    ('kipia-test-v703', 'kipia-v510'),
    ('kipia-test-v702', 'kipia-v510'),
    ('kipia-test-v701', 'kipia-v510'),
    # партия прошлого переноса 475-477: «до партии» = v509
    ('kipia-test-v700', 'kipia-v509'),
    ('kipia-test-v699', 'kipia-v509'),
    ('kipia-test-v698', 'kipia-v509'),
    # партия переноса 473-474: «до партии» = v508
    ('kipia-test-v697', 'kipia-v508'),
    ('kipia-test-v696', 'kipia-v508'),
    # исторические негативы (маппинг переносов 472/471/470/... — как в
    # task475-477-transfer.py, без изменений)
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
    if tot.get(old, 0):
        print('  %s → %s: %d замен' % (old, new, tot.get(old, 0)))
chk(tot.get('kipia-test-v705', 0) > 500,
    'тесты: текущие ассерты v705 → v511 перекрыты (%d)'
    % tot.get('kipia-test-v705', 0))
chk(tot.get('kipia-test-v706', 0) > 100,
    'тесты: guards v706 → v512 перекрыты (%d)'
    % tot.get('kipia-test-v706', 0))
for v, tag in (('kipia-test-v701', '478'), ('kipia-test-v702', '479'),
               ('kipia-test-v703', '480'), ('kipia-test-v704', '481')):
    chk(tot.get(v, 0) == 3,
        'тесты: негатив партии %s %s → v510 три (шапка + assert + '
        'сообщение, %d)' % (tag, v, tot.get(v, 0)))
for v, tag in (('kipia-test-v698', '475'), ('kipia-test-v699', '476'),
               ('kipia-test-v700', '477')):
    chk(tot.get(v, 0) == 3,
        'тесты: негатив партии 475-477 %s → v509 три (%d)'
        % (v, tot.get(v, 0)))
chk(tot.get('kipia-images-test-v3', 0) >= 2,
    'тесты: кэш картинок kipia-images-test-v3 → v3 перекрыт (%d)'
    % tot.get('kipia-images-test-v3', 0))
chk(tot.get('kip8-cache-test-v1', 0) == 3,
    'тесты: kip8-cache-test-v1 → kip8-cache-v1 три (476: тест БД + '
    '2 ассерта, %d)' % tot.get('kip8-cache-test-v1', 0))
chk(tot.get('kipia-data-test-v1', 0) == 5,
    'тесты: kipia-data-test-v1 → kipia-data-v1 пять (475: шапка + '
    'assert + сообщение; 480: 2 ассерта персистентного DATA-кэша, %d)'
    % tot.get('kipia-data-test-v1', 0))


def apply_fixes(path, fixes, tag):
    s = rd(path)
    ok = True
    for old_f, new_f in fixes:
        n = s.count(old_f)
        if n != 1:
            fail.append('[%s] якорь %r найден %d раз (ожидался 1)'
                        % (tag, old_f[:44], n))
            print('FAIL [%s]: якорь %r × %d' % (tag, old_f[:44], n))
            ok = False
            continue
        s = s.replace(old_f, new_f)
    if ok:
        print('OK [%s]: точечные fixes применены' % tag)
    wr(path, s)
    return s


# --- 5.1 Шапки «SW: ...» партии: MAP схлопнул оба конца в v510 →
#     v510 (кроме 481 — у него правый конец v705 → v511 сам); хвосты
#     без префикса kipia-test- не мапятся — точечные fixes
p478 = os.path.join(TDIR_8, 'test-task478.js')
chk(os.path.exists(p478), 'test-task478.js скопирован в kip8')
s478 = apply_fixes(p478, [
    # правый конец шапки — БЕЗ префикса kipia-test- (MAP не трогает)
    ('SW: kipia-v510 → v702.', 'SW: kipia-v510 → v511.'),
    ("'SW поднят до v702 (Task 478)'", "'SW поднят до v511 (Task 478)'"),
    ("test('прежняя версия v701 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v703 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task478')
for m in ("const CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v510') === -1",
          'kipia-v512', 'devPprStatusClass', 'dev-ppr-ok', 'dev-ppr-bad',
          'SW: kipia-v510 → v511'):
    chk(m in s478, 'test-task478.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s478,
    'test-task478.js: kip8test-версий не осталось')

p479 = os.path.join(TDIR_8, 'test-task479.js')
chk(os.path.exists(p479), 'test-task479.js скопирован в kip8')
s479 = apply_fixes(p479, [
    ('SW: kipia-v510 → v703 (комментарий',
     'SW: kipia-v510 → v511 (комментарий'),
    ("'SW поднят до v703 (Task 479)'", "'SW поднят до v511 (Task 479)'"),
    ("test('прежняя версия v702 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v704 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task479')
for m in ("const CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v510') === -1",
          'kipia-v512', 'dev-ppr-warn', 'devices-table-desktop.js',
          'SW: kipia-v510 → v511'):
    chk(m in s479, 'test-task479.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s479,
    'test-task479.js: kip8test-версий не осталось')

p480 = os.path.join(TDIR_8, 'test-task480.js')
chk(os.path.exists(p480), 'test-task480.js скопирован в kip8')
s480 = apply_fixes(p480, [
    ('SW: kipia-v510 → v704 (index.html',
     'SW: kipia-v510 → v511 (index.html'),
    ("test('несуществующая v705 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task480-шапка')

# --- 5.2 kip8-АДАПТАЦИЯ test-task480 (два отличия боевого репо):
#     (а) README.md в kip8 НЕТ (read() упал бы на загрузке) —
#         README_SRC и 2 README-теста исключены;
#     (б) cron-расписания kip8 (PROD) на 2 ч РАНЬШЕ kip8test (PROD
#         работает первым) — мапа WORKFLOWS переведена на kip8-кроны
fixes480 = [
    # (а) README — комментарий шапки «в 15 файлах» и перечень
    ('новый 1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee в 15 файлах:',
     'новый 1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee в 14 файлах (в kip8 '
     'БЕЗ README.md — его в боевом репо никогда не было):'),
    ('//     data/*.json ×4 (source-поле — метаданные синка), README.md\n'
     '//     (таблица источников), Системный_промт (таблица «Источники\n'
     '//     данных»: один файл на 4 листа Приборы/Блокировки/Клапана/\n'
     '//     Регуляторы _app).',
     '//     data/*.json ×4 (source-поле — метаданные синка), '
     'Системный_промт\n'
     '//     (таблица «Источники данных»: один файл на 4 листа\n'
     '//     Приборы/Блокировки/Клапана/Регуляторы _app). kip8-ПЕРЕНОС:\n'
     '//     README.md в kip8 отсутствует — README-тесты исключены; cron\n'
     '//     kip8 (PROD) на 2 ч раньше kip8test (мапа WORKFLOWS ниже).'),
    # (а) README_SRC — не читать
    ("const README_SRC = read('README.md');\n",
     "// kip8: README.md отсутствует — README-тесты исключены при "
     "переносе\n"),
    # (а) README-тесты в секции 6 — исключены (Промт-тесты остаются)
    ("    test('README: 4 строки таблицы синков с новым ID', () => {\n"
     "        assertEqual(countOf(README_SRC, NEW_ID), 4,\n"
     "            '4 записи: devices/lockouts/valves/regulators');\n"
     "        ['sync-devices.py', 'sync-lockouts.py', "
     "'sync-valves.py', 'sync-regulators.py']\n"
     "            .forEach((s) => assertTrue(README_SRC.indexOf(s) !== -1,\n"
     "                'скрипт ' + s + ' в таблице'));\n"
     "    });\n"
     "\n"
     "    test('README: старый ID отсутствует', () => {\n"
     "        assertTrue(README_SRC.indexOf(OLD_ID) === -1, "
     "'старая ссылка убрана');\n"
     "    });\n"
     "\n",
     "    // kip8 (перенос): README.md в боевом репо отсутствует —\n"
     "    // документация источника = таблица «Источники данных» промта\n"
     "\n"),
    # (б) cron-мапа kip8
    ("const WORKFLOWS = {\n"
     "    '.github/workflows/sync-devices.yml':    "
     "{ script: 'scripts/sync-devices.py',    cron: '0 6 * * *' },\n"
     "    '.github/workflows/sync-lockouts.yml':   "
     "{ script: 'scripts/sync-lockouts.py',   cron: '10 3 * * *' },\n"
     "    '.github/workflows/sync-valves.yml':     "
     "{ script: 'scripts/sync-valves.py',     cron: '20 3 * * *' },\n"
     "    '.github/workflows/sync-regulators.yml': "
     "{ script: 'scripts/sync-regulators.py', cron: '30 3 * * *' }\n"
     "};",
     "// kip8 (перенос): cron-расписания ПРОД-репо — на 2 ч раньше\n"
     "// kip8test (PROD работает первым; см. комментарии в yml)\n"
     "const WORKFLOWS = {\n"
     "    '.github/workflows/sync-devices.yml':    "
     "{ script: 'scripts/sync-devices.py',    cron: '0 4 * * *' },\n"
     "    '.github/workflows/sync-lockouts.yml':   "
     "{ script: 'scripts/sync-lockouts.py',   cron: '10 1 * * *' },\n"
     "    '.github/workflows/sync-valves.yml':     "
     "{ script: 'scripts/sync-valves.py',     cron: '20 1 * * *' },\n"
     "    '.github/workflows/sync-regulators.yml': "
     "{ script: 'scripts/sync-regulators.py', cron: '30 1 * * *' }\n"
     "};"),
]
s480 = apply_fixes(p480, fixes480, 'test-task480-kip8')
for m in ("const CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v510') === -1",
          'kipia-v512', "IMAGE_CACHE_VERSION = 'kipia-images-v3'",
          "DATA_CACHE_VERSION = 'kipia-data-v1'",
          "const NEW_ID = '" + NEW_ID + "'",
          "cron: '0 4 * * *'", "cron: '10 1 * * *'",
          "cron: '20 1 * * *'", "cron: '30 1 * * *'",
          'SW: kipia-v510 → v511'):
    chk(m in s480, 'test-task480.js: маркер %r' % (m[:44],))
chk('README_SRC' not in s480,
    'test-task480.js: README-ссылок не осталось (kip8 без README)')
chk('kipia-test-v' not in s480,
    'test-task480.js: kip8test-версий не осталось')

p481 = os.path.join(TDIR_8, 'test-task481.js')
chk(os.path.exists(p481), 'test-task481.js скопирован в kip8')
s481 = apply_fixes(p481, [
    # левый конец шапки MAP заменил (v704→v510), правый (v705) —
    # БЕЗ префикса, фиксим вручную
    ('sw.js kipia-v510 → v705 + комментарий',
     'sw.js kipia-v510 → v511 + комментарий'),
    ("'SW поднят до v705 (Task 481)'", "'SW поднят до v511 (Task 481)'"),
    ("test('прежняя версия v704 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v706 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task481')
for m in ("const CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v510') === -1",
          'kipia-v512', 'kipia-v510 → v511',
          'i - 6800', 'i - 4200', 'i - 3600', 'i - 3100'):
    chk(m in s481, 'test-task481.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s481,
    'test-task481.js: kip8test-версий не осталось')

# --- 5.3 Точечные fixes тестов прошлого переноса 475-477 (копия
#     свежих kip8test-файлов затёрла kip8-адаптации — восстановлены;
#     fixes дословно из task475-477-transfer.py)
p475 = os.path.join(TDIR_8, 'test-task475.js')
s475 = apply_fixes(p475, [
    ('//   SW: kipia-v509 → v699.', '//   SW: kipia-v509 → v510.'),
], 'test-task475')
for m in ("CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v509') === -1",
          'kipia-v512', "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'SW: kipia-v509 → v510', 'notifyDataChanged',
          'resetSectionDataCache', '_startOfflineTokenRetry'):
    chk(m in s475, 'test-task475.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s475,
    'test-task475.js: kip8test-версий не осталось')

p476 = os.path.join(TDIR_8, 'test-task476.js')
s476 = apply_fixes(p476, [
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
], 'test-task476')
for m in ("CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v509') === -1",
          'kipia-v512', "var DB_NAME = 'kip8-cache-v1';",
          'SW: kipia-v509 → v510', '_wipeLocalServerData',
          '_requestPersistentStorage', 'mkFakeIdb',
          '_restoreFromObj', '_idbRestoreView'):
    chk(m in s476, 'test-task476.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s476,
    'test-task476.js: kip8test-версий не осталось')
chk('kip8-cache-test-v1' in s476,
    'test-task476.js: тест БД хранит имя тестового репо (маппинг)')

p477 = os.path.join(TDIR_8, 'test-task477.js')
s477 = apply_fixes(p477, [
    ('//   SW: kipia-v509 → v701 (логика sw.js не менялась —',
     '//   SW: kipia-v509 → v510 (логика sw.js не менялась —'),
], 'test-task477')
chk('SW: kipia-v509 → v510' in s477,
    'test-task477.js: шапка «SW: kipia-v509 → v510» после фикса')
for m in ("CACHE_VERSION = 'kipia-v511'", "indexOf('kipia-v509') === -1",
          'kipia-v512', 'var KipPreload = (function() {',
          'canAccess: function', '_schedulePreload', 'saveData'):
    chk(m in s477, 'test-task477.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s477,
    'test-task477.js: kip8test-версий не осталось')

# --- 5.4 Повтор фиксов прошлого переноса в test-task474 (MAP не
#     разруливает короткие хвосты «v698/v699»)
p474 = os.path.join(TDIR_8, 'test-task474.js')
s474 = apply_fixes(p474, [
    ('//   SW: kipia-v508 → v698.', '//   SW: kipia-v508 → v509.'),
    ("'текущая версия v698'", "'текущая версия v509'"),
    ('версия до партии (v697) отсутствует',
     'версия до партии (v508) отсутствует'),
    ('v699 в sw.js отсутствует', 'v510 в sw.js отсутствует'),
], 'test-task474')
chk('kipia-test-v' not in s474,
    'test-task474.js: kip8test-версий не осталось')

# --- 5.5 Остатки kipia-test-v6xx в kip8 после маппинга
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

# --- 5.6 test-task344.js (kip8-специфичный) — бамп v510→v511
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v510')
chk(n == 3, 'test-task344.js: ассертов kipia-v510 = 3 (%d)' % n)
s = s.replace('kipia-v510', 'kipia-v511')
wr(P344, s)

# --- 5.7 run-all.js (kip8) — + require 478/479/480/481 после 477
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task477.js');\n"
B = ("require('./test-task477.js');\n"
     "// Task 478 — карточка прибора (КИП ИОС): строка «Период ремонта»\n"
     "// цветная по состоянию ППР — зелёный (в гр. ППР, вид ТО/К/П, срок\n"
     "// не просрочен) / красный (просрочен) / обычный (остальные);\n"
     "// devPprStatusClass + CSS dev-ppr-ok/dev-ppr-bad.\n"
     "require('./test-task478.js');\n"
     "// Task 479 — ППР-индикация: третий цвет (срок просрочен, но месяц\n"
     "// срока — ТЕКУЩИЙ календарный месяц → оранжево-золотистый\n"
     "// dev-ppr-warn); те же цвета — в столбце «Дата» табличного вида\n"
     "// приборов (десктоп-модуль devices-table-desktop.js).\n"
     "require('./test-task479.js');\n"
     "// Task 480 — новый ID Google-таблицы «Перечень КИП ИОС рабочий.xlsx»\n"
     "// (1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee): sync-скрипты + workflows +\n"
     "// data/*.json (source) + index.html-комментарии + промт (в kip8\n"
     "// без README — его нет в боевом репо); данные и структура листов\n"
     "// те же (1291/531/320/268).\n"
     "require('./test-task480.js');\n"
     "// Task 481 — ППР-индикация, вид ремонта «ТО»: сравнивается ТОЛЬКО\n"
     "// ГОД даты ремонта (текущий → зелёный, не текущий → красный;\n"
     "// период/месяц НЕ учитываются, warn для ТО невозможен) — карточка\n"
     "// + столбец «Дата» таблицы (одна devPprStatusClass).\n"
     "require('./test-task481.js');\n")
chk(s.count(A) == 1, "run-all.js: якорь test-task477 найден (%d)"
    % s.count(A))
chk('test-task478' not in s and 'test-task479' not in s and
    'test-task480' not in s and 'test-task481' not in s,
    'run-all.js (kip8): 478/479/480/481 ещё не подключены')
s = s.replace(A, B)
for n_ in range(438, 481):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# --- 5.8 после всего: версии в тестах kip8 — семантика kip8
left510 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v510')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v510' in rd(os.path.join(TDIR_8, name))}
chk(left510 == {'test-task478.js': 3, 'test-task479.js': 3,
                'test-task480.js': 3, 'test-task481.js': 3},
    'тесты kip8: kipia-v510 остался только в партии 478-481 (негатив '
    'assert+сообщение + шапка «v510 → v511»): %s' % left510)
left509 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v509')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v509' in rd(os.path.join(TDIR_8, name))}
chk(left509 == {'test-task475.js': 3, 'test-task476.js': 3,
                'test-task477.js': 3},
    'тесты kip8: kipia-v509 остался только в партии 475-477 прошлой '
    'партии (не размыто): %s' % left509)
n511 = sum(rd(os.path.join(TDIR_8, name)).count('kipia-v511')
           for name in os.listdir(TDIR_8)
           if name.startswith('test-'))
chk(n511 > 500,
    'тесты kip8: текущих ассертов kipia-v511 > 500 (%d)' % n511)
chk('kipia-test-v7' not in ''.join(
        rd(os.path.join(TDIR_8, name))
        for name in os.listdir(TDIR_8)
        if name.startswith('test-')),
    'тесты kip8: kipia-test-v7xx не осталось вообще')

# ============================================================
# 6. DEPLOY-доки партии — копия из kip8test (как есть: версии внутри
#    описывают историю kip8test-бампов, инструкция по откату общая)
# ============================================================
print('=== 6. DEPLOY-доки партии ===')
for dep in ('DEPLOY-Task478-device-card-ppr-period-color.md',
            'DEPLOY-Task479-ppr-third-color-table-dates.md',
            'DEPLOY-Task480-sheet-url-replace.md',
            'DEPLOY-Task481-ppr-to-year-only.md'):
    wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
    chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: партия 478-481 (ППР-индикация ×3 цвета + «ТО» по году + '
    'смена ID Google-таблицы) перенесена в kip8 (SW kipia-v511), '
    'клиент-only, серверных шагов нет')
