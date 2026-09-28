#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 441-transfer — обновление системного промта kip8:
новая шапка post-441 (перенос партии 438–441), прежняя post-437 →
«(предыдущая)», версии v479→v480, счётчики тестов 4472→4592 /
4466→4586, формат бампа v480→v481.
"""
import io

P = '/home/z/my-project/kip8/Системный_промт_для_приложения_КИПиА.md'
s = io.open(P, encoding='utf-8').read()

NEW_HEAD = '''> **Версия документа:** 2026-09-28 (post-Task 441: ПЕРЕНОС ПАРТИИ Tasks 438–441 из kip8test@8ae7549 в боевой kip8 ОДНИМ инкрементом SW kipia-v479→v480 — по заявке пользователя «Во всех трёх представлениях печати коды сделай в один столбец. Переноси все изменения в боевой репозиторий kip8» (часть 1 заявки — коды одним столбцом — вошла в партию как Task 441). Партия ПОЛНОСТЬЮ КЛИЕНТСКАЯ: index.html + sw.js + тесты, WorkSchedule.gs/Code.gs НЕ тронуты (srvVer 427; проверено байт-в-байт) — СЕРВЕРНЫЕ ШАГИ НЕ ТРЕБУЮТСЯ: GitHub Pages подхватит сам (1–3 мин после push), затем Ctrl+Shift+R ×1–2 (SW kipia-v479→v480). СОСТАВ ПАРТИИ 438–441: Task 438 — печать табеля: шапка из двух строк «График работы / ‹Месяц› ‹год› г. · вид табеля: …» (норма wsp-meta и штамп «Распечатано» wsp-printed убраны), сноска wsp-foot удалена, колонка «Часы» удалена, «Перераб.» — только дни, коды — сокращённые (short, фолбэк name); «Сохранить PDF» (canvas ×2 → JPEG → мини-писатель PDF 1.4 DCTDecode, пагинация A4-альбом 842×595, _printModel/_printPdfLayout/_printPdfPaintPage/_buildPdfDocument/_savePrintPdf) и «Сохранить Excel» (писатель XLSX Task 430: _wsTabelStylesXml/_wsTabelRows/_wsTabelSheetXml/_buildTabelWorkbook/_savePrintXlsx, цветные ячейки кодов, freeze) ВМЕСТО HTML-файла; Task 439 — блок кодов СПРАВА от мероприятий (HTML flex-ряд .wsp-legend 92 мм, PDF зоны codeW 235pt, Excel колонка D), колонка работников — ТОЛЬКО ФИО и Тип (_empTipLine, _posLabel удалён; ширина по самому большому тексту: HTML кламп 12–48 мм, PDF 46–150pt, Excel по длине ФИО+Тип wrapText), мобильная шахматка — дедуп легаси-«.» (_normalizeStatusCodes «точечные» коды не в хвост; _renderCellPopup без дубля «Выходной, плановый выходной день»); Task 440 — зазор мероприятия↔коды РОВНО 10px во всех трёх представлениях (HTML gap 10px + .wsp-mev flex 0 1 auto — коды за ТЕКСТОМ мероприятий; PDF colGap 7.5pt = 10 CSS-px + codeX = min(evRightMax + colGap, край листа) по measureText; Excel indent="1" у кодов в D ~7px — точные 10px недостижимы, колонка C общая с сеткой), кнопка «следующий год» карточки — ПО ЗАПИСЯМ раздела (_wtabYearMax(tabNo, fam) — баг-фикс: прежде max(now, год табеля) гасил › при записях следующего года; «Мероприятия» fam 0 — тот же фикс; учитывает дата_окончания), блок «ОТПУСКА» — СВОЯ навигация ‹год› (fam 2, _wtabYearVac; пул _VAC_YEARS {год:[записи]}, границы по записям _vacYearRange, лениво _vacYearEnsure — окно [год табеля ±3] + соседи, по одному году за вызов listVacations, без повторов; дни периода по ГОДУ БЛОКА wYearVac; CRUD/«Обновить» сбрасывают; пул в локальной копии Task 314); Task 441 — коды ОДНИМ СТОЛБЦОМ во всех трёх представлениях (HTML .wsp-legend-cols grid-template-columns 1fr 1fr → 1fr, column-gap снят, класс и разметка сохранены, .wsp-lg прежние; PDF _printPdfLayout codeRows = Math.max(1, n) — прежде ceil(n/2); _printPdfPaintPage colW2/perCol УДАЛЕНЫ — lx = codeX, ly = y + lc × codeRowH сквозным столбцом; при нехватке места коды своей страницей, записи не теряются; Excel — один столбец D и прежде, без изменений). МЕТОД ПЕРЕНОСА (scripts/task441-transfer.py, паттерн Task 292/401-406/429/437): index.html — копия kip8test HEAD + 14 де-изоляционных трансформаций (isolateLocalStorage, префиксы kip8test:/kip8test_*, комментарии Task 242/243/284, /kip8test/#…), верификация «дифф диффов» (репо-дифф 55 строк == эталону Task 429/437; дифф задач 1775 строк идентичен обоим репо; упоминаний kip8test = 4 исторических, kipia-test-v = 0); WorkSchedule.gs/Code.gs — kip8-версии сохранены; тесты — 149 test-*.js с маппингом kipia-test-v665→kipia-v480 (432) / v666→v481 (97 guards) / v664→v479 (1 негатив) / v663→v478 (1) / v660+634/640/641/642→v478 (6), test-task344.js бамп v479→v480 (3), run-all.js + 344 + 438/439/440/441. ПРОГОН kip8: 4592 passed / 0 failed (150 тест-файлов — точный паритет kip8test 4586/0 + 6 task344); node --check sw.js OK; SMOKE браузер 6/6 (порт 8942: приложение грузится, 0 JS-ошибок, диалог печати — коды одним столбцом [1 трек, разброс ≤1px, 4 записи], реальные скачивания PDF [%PDF-1.4/DCTDecode/842×595] и Excel [.xlsx]). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v480` (guard v481), тесты 4592/0 (150 тест-файлов, включая kip8-специфичный test-task344.js); kip8test @8ae7549, SW `kipia-test-v665` (guard v666), тесты 4586/0 (149 тест-файлов). ⚠ ГЛАВНАЯ ЗАМЕТКА (Tasks 425/427/429): разделы «Инструктажи» и «Мероприятия» — ПОЛНОСТЬЮ НЕЗАВИСИМЫЕ разделы (НИКАК не связаны): разные листы табель_КИП_ИОС, РАЗДЕЛЬНЫЕ id-последовательности (Task 427), инструктажи — АВТОСОЗДАНИЕ повторных по правилам периодичности (Tasks 419–423), мероприятия — ТОЛЬКО ручной ввод; смешивание id — ЗАПРЕЩЕНО. Следующий номер задачи: 442 (в обоих репо).)
'''

# 1) новая шапка
lines = s.split('\n')
assert lines[2].startswith('> **Версия документа:** 2026-09-27 (post-Task 437'), \
    'строка 3 не post-437'
old_head = lines[2]
demoted = old_head.replace(
    '> **Версия документа:**', '> **Версия документа (предыдущая):**', 1)
lines[2] = NEW_HEAD.rstrip('\n') + '\n' + demoted
s = '\n'.join(lines)

# 2) текущая версия кэша v479 → v480
old = '> **Текущая версия кэша:** `kipia-v479`'
new = '> **Текущая версия кэша:** `kipia-v480`'
assert s.count(old) == 1
s = s.replace(old, new)

# 3) таблица репозиториев
old = '| `kip8` | PWA + APK | `kipia-v479` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |'
new = '| `kip8` | PWA + APK | `kipia-v480` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |'
assert s.count(old) == 1
s = s.replace(old, new)

# 4) пример версии в правиле SW
old = '- `CACHE_VERSION` (например, `kipia-v479`) + `IMAGE_CACHE_VERSION`'
new = '- `CACHE_VERSION` (например, `kipia-v480`) + `IMAGE_CACHE_VERSION`'
assert s.count(old) == 1
s = s.replace(old, new)

# 5) формат бампа в правиле
old = "Формат: `kipia-test-v661` → `kipia-test-v662` (для kip8test) или `kipia-v479` → `kipia-v480` (для kip8)"
new = "Формат: `kipia-test-v665` → `kipia-test-v666` (для kip8test) или `kipia-v480` → `kipia-v481` (для kip8)"
assert s.count(old) == 1
s = s.replace(old, new)

# 6) счётчик тестов
old = "# Ожидается: 4472 passed, 0 failed (kip8; в kip8test — 4466 passed, 0 failed)"
new = "# Ожидается: 4592 passed, 0 failed (kip8; в kip8test — 4586 passed, 0 failed)"
assert s.count(old) == 1
s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8').write(s)
print('OK: промт kip8 post-441 (шапка + v480 + 4592/4586 + бамп v481)')
