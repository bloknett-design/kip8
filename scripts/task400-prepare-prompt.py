# -*- coding: utf-8 -*-
"""Task 400 — подготовка «Системного промта» боевого kip8 к переходу в новый чат.

Синхронизация post-Task 399: новая шапка-версия 2026-09-23 (старая post-Task 382 → «предыдущая»),
сводка перенесённого 384–399, актуализация метрик (строки/страницы/тесты/SW/позиции модулей),
файлы/эндпоинты Apps Script (PPEInit.gs + CRUD СИЗ, Task 392), общее правило кнопок Task 397
в секции _applyRoleToUI, «Последняя принятая партия» → Tasks 384–399.
Строгое якорное сопоставление: любой несовпавший якорь — ошибка, файл не пишется.
"""
import io, sys

PATH = '/home/z/my-project/kip8/Системный_промт_для_приложения_КИПиА.md'

NEW_HEADER = (
    "> **Версия документа:** 2026-09-23 (post-Task 399: ВСЕ задачи 384–399 выполнены в kip8test и "
    "ПЕРЕНЕСЕНЫ в боевой kip8 позадачно/пакетами; документация синхронизирована при подготовке к "
    "ПЕРЕХОДУ В НОВЫЙ ЧАТ. ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 @51daa9e, SW `kipia-v475` (guard v476), тесты "
    "3732/0 (113 файлов), index.html ~52.1 тыс. строк, живой прод https://bloknett-design.github.io/kip8/ ; "
    "kip8test @95ad62d, SW `kipia-test-v627` (guard v628), тесты 3726/0 (112 файлов); десктоп kip8-desktop "
    "(v2.1.8) — CI-автосинк/Build-Desktop. Следующий номер задачи: 400 (в обоих репо). ПЕРЕНЕСЕНО В ПРОД "
    "ЗА ПЕРИОД (сводка 384–399, детали — в шапке kip8test-версии промта и worklog.md): [Task 384 — карточка "
    "сотрудника табеля — ЦЕНТР ПРАВКИ по отдельности: «Правка данных…» (updateEmployee, таб. № readonly), "
    "✎/✕ отпусков (updateVacation/deleteVacation), «+ Мероприятие…»; серверные шаги задеплоены "
    "пользователем. Task 385 — страница «Работники»: полные карточки CRUD + кнопка в баре, карточка "
    "шахматки read-only, шторка «Легенда». Task 386 — «Обозначения»: шторка двух видов (230px/500px) + "
    "мобильная страница. Task 387 — КАНОН справочника кодов Т-12/Т-13 (порядок + полные наименования, "
    "нормализация на клиенте; серверная часть опциональна). Task 388 — сплошные миниатюры с цветом кода, "
    "итоги в сменном/дневном виде, значок раскрытия, вкладки «Работников» столбиком. Task 389 — прошедшие "
    "мероприятия = общий фон окна; численность работников (авто + штат) на «Общей» вкладке. Task 390 — "
    "строки штата/текущего момента ПО КАТЕГОРИЯМ (мастера по должности, дневные/сменные по типу), "
    "выделенная шапка, примыкающие ярлыки. Task 391 — формулировки в скобках, шрифт крупнее, акцентная "
    "кнопка «Добавить работника». Task 392 — раздел «СИЗ»: лист «СИЗ» табель_КИП_ИОС, секция в карточке "
    "работника, шторка с авто-датой окончания, серверные CRUD listPpe/addPpe/updatePpe/deletePpe + "
    "PPEInit.gs (задеплоено пользователем). Task 393 — карточка работника: ЧЕТЫРЕ блока-окна (профиль/"
    "отпуска/мероприятия/СИЗ). Task 394 — карточки десктоп сеткой 2×2; мероприятия НА ВЕСЬ ГОД; окно "
    "мероприятий месяца: секции «Отпуска» (через границу — в обоих) и «СИЗ» (срок истекает). Task 395 — "
    "кнопка «Работники» тулбара табеля скрыта уровням null/min (workschedule.view.min); блоки карточек "
    "фон светлее + рамки 2px; десктоп две колонки. Task 396 — ЗЕБРА строк блоков, компактные кнопки 26px "
    "в верхнем правом углу шапок, оглавления полосой .ws-whead. Task 397 — ОБЩЕЕ ПРАВИЛО ВСЕГО "
    "ПРИЛОЖЕНИЯ: кнопка раздела без доступа НЕ отображается (универсальный проход _applyRoleToUI по "
    "onclick-navigateTo → canAccess + карта JS_NAV_TARGETS + калькуляторы нижнего бара по доступу + бар "
    "скрыт без видимых кнопок). Task 398 — фикс CSS: [hidden]{display:none!important} — семантика "
    "атрибута восстановлена по всему приложению (авторский .ws-refresh-btn{display:inline-flex} перебивал "
    "UA-стиль). Task 399 — окно мероприятий табеля: уровень min (нет доступа к информации мастеров) НЕ "
    "видит записей мастеров — мероприятия/отпуска/СИЗ (тот же _isMasterKipia, что у сетки; счётчики/"
    "пустые состояния пересчитаны)]. ⚠️ ОТКРЫТЫЕ СЕРВЕРНЫЕ ДЕЙСТВИЯ (Apps Script, вручную пользователем; "
    "клиент работает и без них): Task 375 — FlowmeterArchive.gs («окно 1 часа» анти-дублей); Task 376 — "
    "FlowmeterArchive.gs И Flowmeter.gs (ретраи архива + честный archive_write_failed); статус у "
    "пользователя, инструкции DEPLOY-Task375/376-transfer-from-test.md. Задеплоены пользователем "
    "подтверждённо: Task 384 (updateEmployee/updateVacation), Task 392 (PPE CRUD + PPEInit.gs), Task 366 "
    "(дедуп архива). ПАТ: у пользователя (бессрочный; переотправлялся после отката песочницы — урок "
    "Task 396) — в новом чате запрашивать заново; ПЕРЕД записью в /home/z/.kip_pat проверять API /user "
    "(урок Task 365: ls-remote публичных репо всегда 200).)"
)

REPLACEMENTS = [
    # --- шапка: новая версия + старая post-Task 382 становится «предыдущей» (обрабатывается отдельно) ---
    ("__HEADER__", None),

    # --- маркеры текущих версий в шапке ---
    ("> **Текущая версия кэша:** `kipia-v424`",
     "> **Текущая версия кэша:** `kipia-v475`"),
    ("| `kip8` | PWA + APK | `kipia-v424` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |",
     "| `kip8` | PWA + APK | `kipia-v475` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |"),
    ("| `kip8test` | PWA | `kipia-test-v577` | — | Активная разработка, проверка перед боем |",
     "| `kip8test` | PWA | `kipia-test-v627` | — | Активная разработка, проверка перед боем |"),

    # --- Apps Script: состав файлов + WEB_APP_URL ---
    ("Код Apps Script (`Code.gs`, `Utils.gs`, `CableJournal.gs`, `Flowmeter.gs`, `FlowmeterArchive.gs`, "
     "`WorkSchedule.gs`, `ValidationRules.gs`, `VacationsInit.gs`/`VacationsDiagnose.gs`, `RoleMatrix.gs`, "
     "`RoleMatrixGate.gs`, `RoleMatrixInit.gs` — одноразовый init матрицы) **физически не находится** в "
     "репозиториях. Он редактируется напрямую в Google Apps Script Web App (script.google.com). В "
     "репозиториях хранится только URL `WEB_APP_URL` (в `index.html`, ~строка 32 100), а серверные `.gs` "
     "файлы — в `scripts/` как справочные копии.",
     "Код Apps Script (`Code.gs`, `Auth.gs`, `Sessions.gs`, `SessionsDevicePolicy.gs`, `Utils.gs`, "
     "`Flowmeter.gs`, `FlowmeterArchive.gs`, `FlowmeterInit.gs`, `WorkSchedule.gs`, `ValidationRules.gs`, "
     "`VacationsInit.gs`/`VacationsDiagnose.gs`, `RoleMatrix.gs`, `RoleMatrixGate.gs`, "
     "`RoleMatrixInit.gs` (одноразовый init матрицы), `RoleMatrixTask340Init.gs` (одноразовый init "
     "уровней view.min), `StatusCodesInit.gs` (одноразовая замена листа «Коды_статусов», Task 299), "
     "`TabNumbersFix.gs` (разовая починка таб_№), `PPEInit.gs` (одноразовый init листа «СИЗ», Task 392)) "
     "**физически не находится** в репозиториях. Он редактируется напрямую в Google Apps Script Web App "
     "(script.google.com). В репозиториях хранится только URL `WEB_APP_URL` (в `index.html`, ~строка "
     "33 025, `KipAuth.WEB_APP_URL` — развёртывание AKfycbyt…/exec, которым управляет пользователь), а "
     "серверные `.gs` файлы — в `scripts/` как справочные копии."),

    # --- Apps Script: эндпоинты workSchedule ---
    ("| `workSchedule.*` | График работы: шахматка / сотрудники / инструктажи / отпуска "
     "(`listEntries`/`listEmployees`/`listTrainings`/`listVacations`/`generateMonth`/`addTraining`/`addVacation` "
     "/ … — Tasks 201-306; гейт `workschedule.view`/`workschedule.edit`). |",
     "| `workSchedule.*` | График работы/табель: шахматка / сотрудники / инструктажи / отпуска / СИЗ — "
     "`listEntries`/`listEmployees`/`listTrainings`/`listVacations`/`listPpe` (СИЗ, Task 392)/`generateMonth`/"
     "`getPatterns`/`getStatusCodes`/`addEmployee`/`updateEmployee` (Task 384)/`dismissEmployee`/"
     "`addTraining`/`deleteTraining`/`addVacation`/`updateVacation` (Task 384)/`deleteVacation`/"
     "`addPpe`/`updatePpe`/`deletePpe` (Task 392)/`setManualEntry`/`deleteEntry` — Tasks 201-399; гейт "
     "`workschedule.view`/`workschedule.view.min`/`workschedule.edit`). |"),

    # --- технологический стек ---
    ("весь код в одном `index.html` (~49.6 тыс. строк, ~3.1 MB)",
     "весь код в одном `index.html` (~52.1 тыс. строк, ~3.2 MB)"),
    ("SPA, 93 страницы (`page-*`), шевроны ‹‹ для навигации",
     "SPA, 95 страниц (`page-*`), шевроны ‹‹ для навигации"),
    ("(`tests/`, 3294 теста, 95 тест-файлов, `node tests/run-all.js`)",
     "(`tests/`, 3732 теста, 113 тест-файлов, `node tests/run-all.js`)"),

    # --- структура проекта ---
    ("# Весь HTML + CSS + JS (single-file, ~49.6 тыс. строк, ~3.1 MB)",
     "# Весь HTML + CSS + JS (single-file, ~52.1 тыс. строк, ~3.2 MB)"),
    ("# 93 страницы (page-*), включая:",
     "# 95 страниц (page-*), включая:"),
    ("Модуль KipAuth (Email+OTP + серверная карта прав, ~строка 32 094)",
     "Модуль KipAuth (Email+OTP + серверная карта прав, ~строка 33 019)"),
    ("Модуль KipCableJournal (редактирование кабелей, ~строка 35 101)",
     "Модуль KipCableJournal (редактирование кабелей, ~строка 36 100)"),
    ("Модуль KipFav (избранное, ~строка 33 743) — v2.0.0",
     "Модуль KipFav (избранное, ~строка 34 742) — v2.0.0"),
    ("Модуль FlowmeterData + FlowFav (расходомеры, ~строка 36 967)",
     "Модуль FlowmeterData + FlowFav (расходомеры, ~строка 37 966)"),
    ("Модуль WorkSchedule (график работы/табель, ~строка 40 227)",
     "Модуль WorkSchedule (график работы/табель, ~строка 41 232)"),

    # --- Защита _applyRoleToUI: ОБЩЕЕ ПРАВИЛО Task 397 + семантика hidden Task 398 ---
    ("4. **Админ-страницы** — двойная защита: CSS + JS-проверка при `navigateTo()`",
     "4. **Админ-страницы** — двойная защита: CSS + JS-проверка при `navigateTo()`\n"
     "5. **ОБЩЕЕ ПРАВИЛО (Task 397):** любой элемент с `onclick=\"navigateTo('…')\"` виден ⟺ "
     "`canAccess(page)` (хлебные крошки — исключение); карта `JS_NAV_TARGETS` покрывает 8 кнопок с "
     "`addEventListener`-навигацией; «Инженерные калькуляторы» нижнего бара — по `calc.view`; "
     "нижний бар скрыт целиком, если видимых кнопок нет; симметрично при смене роли\n"
     "6. **Семантика `hidden` (Task 398):** CSS-правило `[hidden]{display:none!important}` в начале "
     "`<style>` — атрибут `hidden` ВСЕГДА прячет элемент, даже если авторский CSS задаёт `display` "
     "(показ — только снятием атрибута)"),

    # --- правила работы: ожидания тестов + формат бампа ---
    ("ожидается `3294 passed, 0 failed` (для kip8; в kip8test — `3288 passed, 0 failed`)",
     "ожидается `3732 passed, 0 failed` (для kip8; в kip8test — `3726 passed, 0 failed`)"),
    ("Формат: `kipia-test-v611` → `kipia-test-v612` (для kip8test) или `kipia-v459` → `kipia-v460` (для kip8)",
     "Формат: `kipia-test-v627` → `kipia-test-v628` (для kip8test) или `kipia-v475` → `kipia-v476` (для kip8)"),

    # --- «Последняя принятая партия» ---
    ("> **Последняя принятая партия:** Tasks 375–382 (печать табеля gap 10px + 4 слоя анти-дублей "
     "расходомеров; фикс потери строки архива №12 — ретраи 10с+4с+4с + честный archive_write_failed + "
     "day-дедуп флаша по архиву; усиление «сегодня» в шахматке + полосы светлой темы = цветам тёмной; "
     "итоги: нули→пустые/линии/перекрестье → откат фона «как до белого» (прозрачные td + зебра); "
     "шахматка: пустые ячейки значений светлой темы #FFFFFF; окна бара: значок полного раскрытия + "
     "оверлей вниз (бар 95px) + значки приколоты при прокрутке + общий сплошной фон «Мероприятий» с "
     "датозависимыми зонами; user-select:none на мобиле; мобильные итоги «Месяц» — колонка фамилий ПО "
     "ТЕКСТУ) — перенесено из kip8test (источники: 78412e8→fadcacb→395d5b3→8a16d3e→deedbde→33dd957→"
     "e2eddb0→811d963), SW kipia-v452→v459, паритет тестов 3294/0 (2026-09-18). Плюс Tasks 371–374 — "
     "«Датчики температуры» (каталог карточками, избранное TempFav, ТХК, расчёт произвольных значений). "
     "⚠️ Серверные части Task 375/376 (FlowmeterArchive.gs/Flowmeter.gs) — РУЧНАЯ замена в Apps Script "
     "пользователем, инструкции в scripts/DEPLOY-Task375/376-transfer-from-test.md.",
     "> **Последняя принятая партия:** Tasks 384–399 (карточка сотрудника — ЦЕНТР ПРАВКИ данных/"
     "отпусков/мероприятий по отдельности; страница «Работники» с CRUD-карточками, «Обозначениями» и "
     "вкладками столбиком; канон справочника кодов; окно мероприятий — фон прошедших + секции "
     "«Отпуска»/«СИЗ»; строки штата/момента по категориям; раздел «СИЗ» с серверным CRUD + PPEInit.gs; "
     "карточка — ЧЕТЫРЕ блока-окна с зеброй/компактными кнопками/оглавлениями; десктоп 2×2 + мероприятия "
     "на весь год; кнопка «Работники» по уровню доступа + ОБЩЕЕ ПРАВИЛО ВСЕХ кнопок-разделов по "
     "доступу (Task 397) + фикс семантики [hidden] (Task 398); окно мероприятий без мастеров для уровня "
     "min (Task 399)) — перенесено из kip8test позадачно (источники: c0ed8d7→5952d60→99464ba→ae70fc5→"
     "442d1a4→cb4f6b0→8d11ff7→febce3e→6826330→771f014→90a024c→35c68c2), SW kipia-v459→v475, паритет "
     "тестов 3732/0 (2026-09-23). ⚠️ Серверные части Task 375/376 (FlowmeterArchive.gs/Flowmeter.gs) — "
     "РУЧНАЯ замена в Apps Script пользователем, инструкции в scripts/DEPLOY-Task375/376-transfer-from-"
     "test.md; серверные части Task 384/392 задеплоены пользователем подтверждённо."),

    # --- инструкция для новых чатов ---
    ("# Ожидается: 3294 passed, 0 failed (kip8; в kip8test — 3288 passed, 0 failed)",
     "# Ожидается: 3732 passed, 0 failed (kip8; в kip8test — 3726 passed, 0 failed)"),
    ("❌ Заново читать весь `index.html` (~49.6 тыс. строк)",
     "❌ Заново читать весь `index.html` (~52.1 тыс. строк)"),

    # --- полезные команды: ожидание страниц ---
    ("# Подсчёт страниц в index.html\ngrep -c 'id=\"page-' index.html\n# ожидается: 93 (включая 3 страницы графика работы)",
     "# Подсчёт страниц в index.html\ngrep -c 'id=\"page-' index.html\n# ожидается: 95 (включая 5 страниц модуля табеля/«Работников»)"),
]

def main():
    with io.open(PATH, encoding='utf-8') as f:
        text = f.read()

    errors = []
    # 1) шапка: новая версия пост-Task 399 строкой 3; старая post-Task 382 → «предыдущая» (строкой 4)
    lines = text.split('\n')
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith('> **Версия документа:** 2026-09-18 (post-Task 382'):
            header_idx = i
            break
    if header_idx is None:
        errors.append('HEADER: строка "> **Версия документа:** 2026-09-18 (post-Task 382…" не найдена')
    else:
        old = lines[header_idx]
        old_prev = old.replace('> **Версия документа:**', '> **Версия документа (предыдущая):**', 1)
        lines[header_idx] = NEW_HEADER
        lines.insert(header_idx + 1, old_prev)
        text = '\n'.join(lines)

    # 2) точечные замены
    for old, new in [(o, n) for (o, n) in REPLACEMENTS if o != '__HEADER__']:
        if old not in text:
            errors.append('ANCHOR NOT FOUND: %s' % old[:90].replace('\n', '\\n'))
            continue
        if text.count(old) != 1:
            errors.append('ANCHOR NOT UNIQUE (%d): %s' % (text.count(old), old[:90].replace('\n', '\\n')))
            continue
        text = text.replace(old, new)

    if errors:
        print('ОШИБКИ ЯКОРЕЙ (%d):' % len(errors))
        for e in errors:
            print('  - ' + e)
        sys.exit(1)

    with io.open(PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print('OK: Системный промт боевого kip8 синхронизирован к post-Task 399 (версия 2026-09-23).')
    print('Замен: шапка (новая + прежняя→«предыдущая») + %d точечных.' % (len(REPLACEMENTS) - 1))

if __name__ == '__main__':
    main()
