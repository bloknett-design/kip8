#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 486-transfer: перенос Task 486 из kip8test (@c0d241ee — фича;
# @39e7025b — docs: worklog/промт/DEPLOY, index.html и тесты НЕ менял)
# в боевой kip8 ОДНИМ инкрементом SW kipia-v513 → v514 (команда
# пользователя: «Перенеси в kip8»; регламент Task 441).
# Состав: Табель — ТИХОЕ обновление данных при открытии приложения
# (заявка: «помимо ручного обновления»): WorkSchedule.silentRefresh
# из KipAuth._schedulePreload (5 путей старта, 4 с, canAccess) — 7
# read-only экшенов, копия в ОБА слоя (LS + KipDB), тихая
# перерисовка открытого раздела, троттлинг 5 мин, KipPreload.ws-
# координация. КЛИЕНТ-ONLY: .gs не тронуты; данные не менялись.
# МЕТОД (Task 292/441-485): index.html — wholesale де-изоляция (те
# же 16 rep1/17 якорей из task478-481-transfer.py — партия 486
# изоляцию НЕ трогала; «дифф диффов» сходится); sw.js — шапка kip8 +
# перенос-метка + комментарий Task 486 ДОСЛОВНО + kipia-v514, ТЕЛО
# идентично; тесты — ЗЕРКАЛЬНЫЕ операции (bump v513→v514 ассерты /
# v514→v515 guards, те же окна task486-windows.py, WS_CLIENT ×8,
# срез 477, НОВЫЙ test-task486.js с MAP, run-all); шапки тестов
# 483/484/485 — ИСТОРИЧЕСКИЕ версии kip8-посадки (485-header
# v514→v513 после бампа — прецедент 485-переноса, где 483/484
# вернули на v512). ОДНОРАЗОВЫЙ: лечение при сбое —
# git checkout -- . + чистый прогон.
import glob
import io
import os
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


def rep_file(path, pairs, tag):
    """Точечные замены с контролем счётчиков; порядок пар ВАЖЕН."""
    s = rd(path)
    for old, new, cnt in pairs:
        n = s.count(old)
        assert n == cnt, '%s: %r найдено %d (ожидалось %d)' % (
            tag, old[:60], n, cnt)
        s = s.replace(old, new)
    wr(path, s)
    print('OK [%s]: %d замен' % (tag, len(pairs)))


def diff_lines(p1, p2):
    # Нормализация: только строки < / > (без @@-заголовков —
    # смещения номеров строк между репо из-за изоляции;
    # прецедент task482-484-transfer.py)
    r = subprocess.run(['diff', p1, p2], capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines()
            if ln.startswith('<') or ln.startswith('>')]


# ============================================================
# 0. База: kip8test HEAD = 39e7025b (docs поверх фичи c0d241ee),
#    kip8 HEAD = 019ba8c, рабочие деревья чистые
# ============================================================
print('=== 0. База ===')
BASE_T = '592bce57'   # kip8test до Task 486 (post-485-перенос docs)
BATCH_T = 'c0d241ee'  # kip8test Task 486 (фича)
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '39e7025b', 'база: kip8test HEAD = %s (ожидался 39e7025b)'
    % HEAD_T)
chk(git(K8T, 'show', '%s:index.html' % BATCH_T) ==
    git(K8T, 'show', '%s:index.html' % HEAD_T),
    'база: index.html в docs-коммите не менялся (== фиче)')
chk(git(K8T, 'show', '%s:sw.js' % BATCH_T) ==
    git(K8T, 'show', '%s:sw.js' % HEAD_T),
    'база: sw.js в docs-коммите не менялся')
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '019ba8c', 'база: kip8 HEAD = %s (ожидался 019ba8c)'
    % HEAD_8)
st = git(K8, 'status', '--porcelain').strip()
noise = [ln for ln in st.splitlines() if ln.startswith('??')
         and ('task486-transfer' in ln or '__pycache__' in ln)]
real = [ln for ln in st.splitlines() if ln not in noise]
chk(not real, 'kip8: рабочее дерево чистое: %r' % (real[:4],))

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (16 rep1 / 17 якорей;
#    партия 486 изоляцию не трогала) + «дифф диффов»
# ============================================================
print('=== 1. index.html ===')
src = git(K8T, 'show', '%s:index.html' % HEAD_T)
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
    '(5 исторических + 1 комментарий KipDB): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))
chk("var DB_NAME = 'kip8-cache-v1';" in src,
    'index.html: DB_NAME = kip8-cache-v1 (Task 476)')
chk(src.count("'kip8-cache-test-v1'") == 1,
    'index.html: kip8-cache-test-v1 ровно 1 — в комментарии маппинга: %d'
    % src.count("'kip8-cache-test-v1'"))

# Маркеры партии 486
for m in ('Task 486', 'silentRefresh: function', '_silentTs: 0',
          '_silentBusy: false', 'WorkSchedule.silentRefresh()',
          'KipPreload._preloadWs', '_preloadWs()'):
    chk(m in src, 'index.html: маркер партии (486) %r' % (m[:44],))
# Живые задачи прошлых партий — не размыло переносом
for m in ('function devPprStatusClass',       # 478-481
          '_barExpMaxH', 'evStateCls',        # 482
          'var KipDB = (function() {', 'var KipPreload = (function() {',
          '_schedulePreload', '_startOfflineTokenRetry'):
    chk(m in src, 'index.html: якорь живой задачи %r' % (m[:44],))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
TMP = '/home/z/my-project/scripts/.k8t-486-tmp'
os.makedirs(TMP, exist_ok=True)
base_t = os.path.join(TMP, 'k8t-index-base.html')
base8 = os.path.join(TMP, 'k8-index-base.html')
head_t = os.path.join(TMP, 'k8t-index-head.html')
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '%s:index.html' % BASE_T))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
with io.open(head_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '%s:index.html' % HEAD_T))
d_new = diff_lines(k8_index_new, head_t)
d_base = diff_lines(base8, base_t)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d)' % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new)
d_taskT = diff_lines(base_t, head_t)
chk(d_task8 == d_taskT,
    'index.html: дифф задач (486) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

print('\n===== ЧАСТЬ 1 (index.html) ЗАВЕРШЕНА: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: python3 scripts/task486-transfer2.py (sw.js + тесты)')
