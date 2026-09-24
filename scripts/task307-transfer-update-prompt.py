# -*- coding: utf-8 -*-
# Обновление системного промта kip8 до post-Task 307 (перенос из kip8test@7ec7612)
with open('Системный_промт_для_приложения_КИПиА.md') as f:
    lines = f.readlines()

new3 = '''> **Версия документа:** 2026-09-03 (post-Task 307: ПЕРЕНОС Task 307 из kip8test@7ec7612 в боевой kip8 одним инкрементом SW kipia-v411→v412 — заявка пользователя: «В разделе "График работы" убери вкладку сотрудники, а кнопку "Добавить сотрудника" перемести в бар над шахматкой к остальным кнопкам». СОДЕРЖАНИЕ: 1) СТРАНИЦА «Сотрудники» #page-work-schedule-employees УДАЛЕНА ЦЕЛИКОМ (див, субнав-кнопки, хук navigateTo→initEmployeesPage, записи PAGE_PARENTS/PAGE_LABELS, 'work-schedule-employees' из _WORK_SCHEDULE_PAGES, JS initEmployeesPage/loadEmployees/_renderEmployees, мёртвый CSS .ws-emp-card*/.ws-emp-card-header/.ws-employees-list; _loadEmployees жив — loadGrid/инструктажи/отпуска); СУБНАВИГАЦИЯ — 3 полосы × 3 кнопки (Шахматка/Инструктажи/Отпуска); справочник виден в строках шахматки/попапе ячейки/селектах форм. 2) КНОПКА «+ Сотрудник» (#wsEmpBtn .ws-addemp-btn) в ws-toolbar-main над шахматкой — после селектов, ДО «Сформировать»; нейтральный стиль селектов, 34px (правило Task 269 расширено), title «Добавить сотрудника»; видимость по _canEdit в init() КАК У «Сформировать» («ИТР8 pro» — скрыта); клик → прежний bottom-sheet #wsEmpSheet; .ws-toolbar-main flex-wrap: wrap (мобильный складывается в 2 строки); светлая тема — в тон селектов. 3) submitEmployeeForm после добавления → loadGrid() (НОВАЯ СТРОКА сотрудника в шахматке) вместо удалённого loadEmployees(). ПЕРЕНЕСЕНО: index.html — патч 348 строк (git apply, чисто; верификация: diff(kip8test@7ec7612, kip8-новый) == базовый изоляционный дифф 55 строк — префиксы kip8test_/isolateLocalStorage/комментарии Task 243, зоны Task 307 не затронуты); sw.js kipia-v411→v412 + комментарий; tests/ — test-work-schedule.js копия из kip8test@7ec7612 с адаптацией версий (kipia-test-v546→v412, v545→v411, v539→v410) + 8 файлов с бампом kipia-v411→v412; scripts/: НОВЫЕ task307-browser-check.py (порт 8928) + DEPLOY-Task307-subnav-employees.md + пруфы task307-proof-*.png. СЕРВЕР WorkSchedule.gs и листы НЕ менялись — Apps Script НЕ трогать (единственный инкремент SW). Тесты: 1433 → 1444 passed / 0 failed (ПАРитет с kip8test@7ec7612). Верификация: node --check sw.js; scripts/task307-browser-check.py — 22/22 PASS на РЕАЛЬНОМ kip8/index.html (субнав 3 кнопки; «+ Сотрудник» в тулбаре до «Сформировать» 34px, видна Админу; шторка «Новый сотрудник» с фокусом; submit → addEmployee(042 «Сидоров») → тост → НОВАЯ СТРОКА в шахматке; инструктажи/отпуска живы; navigateTo('work-schedule-employees') не падает; 375px без горизонтального скролла; десктоп «ИТР8 pro» — кнопка и «Сформировать» скрыты; 0 JS-ошибок; localStorage БЕЗ префикса kip8test:). АКТУАЛИЗАЦИЯ: 92 страницы, ~39.7 тыс. строк, тесты 1444 (26 тест-файлов .js), пример CACHE_VERSION kipia-v412. ДЕПЛОЙ ПОЛЬЗОВАТЕЛЯ: ТОЛЬКО фронтенд — GitHub Pages подхватит сам (1–3 мин после push), затем Ctrl+Shift+R ×1–2 (SW v412); Apps Script и листы НЕ трогать (сервер не менялся с Task 306) — см. scripts/DEPLOY-Task307-subnav-employees.md. kip8-desktop синхронизируется АВТОМАТИЧЕСКИ расширенным sync-to-desktop.yml (index.html + sw.js + tests — Task 306-десктоп). Последнее изменение КОДА: Task 307.)
'''

assert lines[2].startswith('> **Версия документа:**')
lines.insert(2, new3 if new3.endswith('\n') else new3 + '\n')
prev = [i for i, l in enumerate(lines[:30]) if l.startswith('> **Версия документа (предыдущая):**')]
while len(prev) > 12:
    del lines[prev[-1]]
    prev = [i for i, l in enumerate(lines[:30]) if l.startswith('> **Версия документа (предыдущая):**')]
print('Строка 3 вставлена; цепочка «предыдущих»:', len(prev))

src = ''.join(lines)

reps = [
    ('> **Текущая версия кэша:** `kipia-v411`', '> **Текущая версия кэша:** `kipia-v412`'),
    ('| `kip8` | PWA + APK | `kipia-v411` |', '| `kip8` | PWA + APK | `kipia-v412` |'),
    ('| Архитектура | SPA, 93 страницы (`page-*`), шевроны', '| Архитектура | SPA, 92 страницы (`page-*`), шевроны'),
    ('# 93 страницы (page-*), включая:', '# 92 страницы (page-*), включая:'),
    ('весь код в одном `index.html` (~39.8 тыс.', 'весь код в одном `index.html` (~39.7 тыс.'),
    ('# Весь HTML + CSS + JS (single-file, ~39.8 тыс. строк, ~2.4 MB)', '# Весь HTML + CSS + JS (single-file, ~39.7 тыс. строк, ~2.4 MB)'),
    ('| Тесты | Node.js + кастомный фреймворк (`tests/`, 1433 теста, `node tests/run-all.js`)', '| Тесты | Node.js + кастомный фреймворк (`tests/`, 1444 теста, `node tests/run-all.js`)'),
    ('# 1433 юнит-теста (Node.js, 20 файлов)', '# 1444 юнит-теста (Node.js, 26 файлов)'),
    ('`CACHE_VERSION` (например, `kipia-v411`)', '`CACHE_VERSION` (например, `kipia-v412`)'),
]
for old, new in reps:
    n = src.count(old)
    assert n == 1, (old, n)
    src = src.replace(old, new)
print('Счётчики обновлены (%d замен)' % len(reps))

old260 = '- Модуль «График работы» (шахматка сменного и дневного персонала ИОС на месяц) — ЧЕТЫРЕ страницы (субнавигация: Шахматка/Сотрудники/Инструктажи/Отпуска):'
new260 = '- Модуль «График работы» (шахматка сменного и дневного персонала ИОС на месяц) — ТРИ страницы (субнавигация: Шахматка/Инструктажи/Отпуска; Task 307: вкладка/страница «Сотрудники» удалена — добавление кнопкой «+ Сотрудник» в тулбаре над шахматкой):'
assert old260 in src
src = src.replace(old260, new260)
print('Строка 260 (состав модуля) обновлена')

old722 = '> **Последняя принятая партия:** Tasks 298-306 (коды статусов Т-12/Т-13, мероприятия И/ОБ/ПЗ/ПР/*, таб_№ текстом, отпуск + плановая смена бейджем, одна кнопка «Сформировать») из kip8test@4fc48bc — kipia-v411, паритет тестов 1433/0 (Task 306-перенос, 2026-09-03; Apps Script: WorkSchedule.gs заменить + «Новая версия» AKfycbyt…, если ещё не задеплоен из kip8test — сервер менялся в Tasks 298/303/304/306).'
new722 = '> **Последняя принятая партия:** Tasks 298-307 (коды статусов Т-12/Т-13, мероприятия И/ОБ/ПЗ/ПР/*, таб_№ текстом, отпуск + плановая смена бейджем, одна кнопка «Сформировать», удаление вкладки «Сотрудники» + кнопка «+ Сотрудник» в тулбаре) — Task 307 из kip8test@7ec7612, kipia-v412, паритет тестов 1444/0 (Task 307-перенос, 2026-09-03; Apps Script НЕ трогать — сервер не менялся в Task 307; листы не трогать).'
assert old722 in src
src = src.replace(old722, new722)
print('Строка 722 (последняя партия) обновлена')

# Новая запись в секции модуля (после блока партии 298-306, перед '---' секции)
lines2 = src.split('\n')
insert_at = None
for i, l in enumerate(lines2):
    if l.startswith('- **Перенос партии Tasks 298-306:'):
        j = i + 1
        while j < len(lines2) and not lines2[j].startswith('---'):
            j += 1
        insert_at = j
        break
assert insert_at is not None, 'секция партии 298-306 не найдена'
entry = ('- **Перенос Task 307: вкладка «Сотрудники» удалена, кнопка «+ Сотрудник» в тулбаре над шахматкой** (Task 307-перенос из kip8test@7ec7612, один инкремент SW kipia-v411→v412, сервер/листы не менялись): страница #page-work-schedule-employees удалена целиком (див/субнав/хук navigateTo/PAGE_PARENTS/PAGE_LABELS/_WORK_SCHEDULE_PAGES; JS initEmployeesPage+loadEmployees+_renderEmployees; мёртвый CSS .ws-emp-card*); субнавигация 3 полосы × 3 кнопки (Шахматка/Инструктажи/Отпуска); кнопка «+ Сотрудник» (#wsEmpBtn .ws-addemp-btn) в ws-toolbar-main (после селектов, до «Сформировать»), нейтральный стиль селектов, 34px, видимость по _canEdit как у «Сформировать», клик → прежний bottom-sheet #wsEmpSheet, submit → loadGrid() (новая строка в сетке); .ws-toolbar-main flex-wrap: wrap (мобильный). Верификация: патч index.html 348 строк чисто (изоляционный дифф 55 строк — базовый), тесты 1433→1444/0 (паритет), task307-browser-check 22/22 на реальном kip8/index.html, VLM ×2. ДЕПЛОЙ: только GitHub Pages + Ctrl+Shift+R ×1–2 (SW v412); Apps Script/листы не трогать; kip8-desktop — автосинк. См. scripts/DEPLOY-Task307-subnav-employees.md')
lines2.insert(insert_at, entry)
src = '\n'.join(lines2)
print('Запись Task 307 добавлена в секцию модуля (строка %d)' % insert_at)

with open('Системный_промт_для_приложения_КИПиА.md', 'w') as f:
    f.write(src)
print('Промт kip8 записан:', len(src), 'символов')
