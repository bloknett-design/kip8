#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 442-transfer — обновление системного промта kip8:
новая шапка post-442 (перенос задачи), прежняя post-441 →
«(предыдущая)», версии v480→v481, счётчики тестов 4592→4608 /
4586→4602, формат бампа v481→v482."""
import io

P = '/home/z/my-project/kip8/Системный_промт_для_приложения_КИПиА.md'
s = io.open(P, encoding='utf-8').read()

NEW_HEAD = '''> **Версия документа:** 2026-09-28 (post-Task 442: ПЕРЕНОС Task 442 из kip8test@c614f6e в боевой kip8 ОДНИМ инкрементом SW kipia-v480→v481 — по регламенту заявки Task 441 «Переноси все изменения в боевой репозиторий kip8» (после приёмки задачи в kip8test). Заявка Task 442: «На распечатываемом графике работы убери мини значки мероприятий в шахматке и столбец с кодами, и внешний контур линий выходных календарных дней в шахматке сделай толще, а выделять их фоном не нужно, и даты выходных жирнее». Задача ПОЛНОСТЬЮ КЛИЕНТСКАЯ: index.html + sw.js + тесты, WorkSchedule.gs/Code.gs НЕ тронуты (srvVer 427; проверено байт-в-байт) — СЕРВЕРНЫЕ ШАГИ НЕ ТРЕБУЮТСЯ: GitHub Pages подхватит сам (1–3 мин после push), затем Ctrl+Shift+R ×1–2 (SW kipia-v480→v481). СОСТАВ Task 442 (во всех ТРЁХ представлениях печати HTML/PDF/Excel): (1) МИНИ-ЗНАЧКИ МЕРОПРИЯТИЙ в шахматке УДАЛЕНЫ (Task 361 возвращал, Task 343 убирал): CSS .wsp-ev-wrap/.wsp-ev сняты; _printCell (НОВЫЙ 5-й параметр isLastRow) и _printModel больше НЕ зовут _eventsAt — статус-мероприятия (И/ОБ/ПЗ/ПР/*) печатаются ПУСТЫМИ ячейками, события раскрываются списком «Мероприятия» под таблицей (жив); точка переработки (красная, правый верхний угол), пунктир плана отпуска и ЭКРАННАЯ сетка приложения — НЕ тронуты; (2) СТОЛБЕЦ КОДОВ УДАЛЕН (легенда Tasks 360–441): HTML — .wsp-legend/.wsp-legend-t/.wsp-legend-cols/.wsp-lg/.wsp-lg i сняты вместе с flex-рядом .wsp-bottom (зазор 10px Tasks 375/440 — с рядом) и сбором usedCodes — нижняя секция = ТОЛЬКО список мероприятий на всю ширину листа; PDF — зоны codeW 235pt/colGap 7.5pt/codeX и страницы-codes сняты, метод _printCodesData УДАЛЁН, evW = W − 2M (мероприятия на всю ширину, перенос до края листа); Excel — колонки D/«Коды:» (s7/s8 indent) НЕТ, блок мероприятий только A/B, база цветных стилей 9→7, _buildTabelWorkbook — цвета из клеток, counts без codes; (3) ПОЛОСЫ ВЫХОДНЫХ КАЛЕНДАРНЫХ ДНЕЙ — ТОЛСТЫЙ ВНЕШНИЙ КОНТУР БЕЗ ЗАЛИВКИ (полоса = подряд идущие нерабочие дни производственного календаря, Сб+Вс — ОДИН контур; внутренние линии тонкие; серые заливки #dfe5e9/#e2e8ec УДАЛЕНЫ; статусные ячейки сохраняют цвет кода): HTML — .wsp-day.wsp-off { border-top: 2px solid #8f99a3 } + края .wsp-off-edge-l/r (offArr по соседям) в шапке, тело — маркер wsp-cell-off у ВСЕХ клеток полосы + края + wsp-off-edge-b (низ последней строки; !important — выше пунктира .wsp-vac); PDF — strokeRect полос ctx.lineWidth 1.4 (сетка 0.5), цвет #8f99a3, от gridTop (верх ленты дней) до низа последней строки; Excel — MEDIUM-границы FF8F99A3, 13 границ: шапка T/TL/TR/TLR, дни недели L/R/LR, тело L/R/LR/B/BL/BR/BLR — обычные + ЦВЕТНЫЕ (7 на цвет); (4) ДАТЫ ВЫХОДНЫХ ЖИРНЕЕ: HTML — .wsp-day { font-weight: 400 } (снята ДЕФОЛТНАЯ жирность th браузера — прежде ВСЕ числа были жирными) + .wsp-day.wsp-off { font-weight: 700 } (день недели под числом — 400); PDF — ctx.font = (day.off ? '700 ' : '') + '7px Arial'; Excel — числа выходных прежний жирный s=1 с контурными вариантами, будни — НОВЫЙ стиль regDate (fontId 6, НЕ жирный); НОВАЯ карта стилей _wsTabelStyleMap(nColors) — единая для _wsTabelStylesXml/_wsTabelRows (coloredBase 7, headC 7+C T/TL/TR/TLR, dowsC +4 L/R/LR, bodyC +3 L/R/LR/B/BL/BR/BLR, colC +7 цветные-контуры ×7, regDate colC+7C; cellXfs count = 22+8C; fonts 7, borders 13). МЕТОД ПЕРЕНОСА (scripts/task442-transfer.py, паттерн Task 292/429/437/441): index.html — копия kip8test@c614f6e + 14 де-изоляционных трансформаций, верификация «дифф диффов» (репо-дифф 55 строк == эталону Task 429/437/441; дифф задачи 1001 строка идентичен обоим репо; kip8test-упоминаний 4 исторических, kipia-test-v 0); WorkSchedule.gs/Code.gs — kip8-версии сохранены; тесты — 150 test-*.js с маппингом kipia-test-v666→kipia-v481 (432) / v667→v482 (97) / v665→v480 (2) / v663→v478 (1) / v660+634/640/641/642→v478 (6), test-task344.js бамп v480→v481 (3), run-all.js + 344 + 438–442. ПРОГОН kip8: 4608 passed / 0 failed (150 тест-файлов — паритет kip8test 4602/0 + 6 task344); node --check sw.js OK; SMOKE браузер scripts/task442-smoke-k8.py 10/10 (порт 8944: график открывается, диалог печати — легенды/бейджи 0, мероприятия живы, контур Сб 2px, даты 700/400, клетка Сб в полосе с краем, PDF %PDF-1.4/DCTDecode/842×595, Excel без «Коды:»/13 границ medium/regDate, 0 JS-ошибок). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v481` (guard v482), тесты 4608/0 (150 тест-файлов, включая kip8-специфичный test-task344.js); kip8test @c614f6e, SW `kipia-test-v666` (guard v667), тесты 4602/0 (150 тест-файлов). ⚠ ГЛАВНАЯ ЗАМЕТКА (Tasks 425/427/429): разделы «Инструктажи» и «Мероприятия» — ПОЛНОСТЬЮ НЕЗАВИСИМЫЕ разделы (НИКАК не связаны): разные листы табель_КИП_ИОС, РАЗДЕЛЬНЫЕ id-последовательности (Task 427), инструктажи — АВТОСОЗДАНИЕ повторных по правилам периодичности (Tasks 419–423), мероприятия — ТОЛЬКО ручной ввод; смешивание id — ЗАПРЕЩЕНО. Следующий номер задачи: 443 (в обоих репо).)
'''

# 1) новая шапка, прежняя post-441 → «(предыдущая)»
lines = s.split('\n')
assert lines[2].startswith('> **Версия документа:** 2026-09-28 (post-Task 441'), \
    'строка 3 не post-441'
old_head = lines[2]
demoted = old_head.replace(
    '> **Версия документа:**', '> **Версия документа (предыдущая):**', 1)
lines[2] = NEW_HEAD.rstrip('\n') + '\n' + demoted
s = '\n'.join(lines)

# 2) текущая версия кэша v480 → v481
old = '> **Текущая версия кэша:** `kipia-v480`'
new = '> **Текущая версия кэша:** `kipia-v481`'
assert s.count(old) == 1
s = s.replace(old, new)

# 3) таблица репозиториев
old = '| `kip8` | PWA + APK | `kipia-v480` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |'
new = '| `kip8` | PWA + APK | `kipia-v481` | — | Боевой сайт + сборка APK (TWA через Bubblewrap) |'
assert s.count(old) == 1
s = s.replace(old, new)

# 4) пример версии в правиле SW
old = '- `CACHE_VERSION` (например, `kipia-v480`) + `IMAGE_CACHE_VERSION`'
new = '- `CACHE_VERSION` (например, `kipia-v481`) + `IMAGE_CACHE_VERSION`'
if s.count(old) == 1:
    s = s.replace(old, new)
else:
    # альтернативная формулировка из kip8test-промта
    old2 = '- `CACHE_VERSION` (например, `kipia-v480`)'
    assert s.count(old2) == 1, 'пример CACHE_VERSION не найден'
    s = s.replace(old2, '- `CACHE_VERSION` (например, `kipia-v481`)')

# 5) формат бампа в правиле
old = "Формат: `kipia-test-v665` → `kipia-test-v666` (для kip8test) или `kipia-v480` → `kipia-v481` (для kip8)"
new = "Формат: `kipia-test-v666` → `kipia-test-v667` (для kip8test) или `kipia-v481` → `kipia-v482` (для kip8)"
assert s.count(old) == 1
s = s.replace(old, new)

# 6) счётчик тестов
old = "# Ожидается: 4592 passed, 0 failed (kip8; в kip8test — 4586 passed, 0 failed)"
new = "# Ожидается: 4608 passed, 0 failed (kip8; в kip8test — 4602 passed, 0 failed)"
assert s.count(old) == 1
s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8').write(s)
print('OK: промт kip8 post-442 (шапка + v481 + 4608/4602 + бамп v482)')
