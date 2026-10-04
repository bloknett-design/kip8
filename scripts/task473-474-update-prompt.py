#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 473-474: обновление системного промта kip8 (post-Task 473-474
# ПЕРЕНОС партии из kip8test@d9efdd0f).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 472: ПЕРЕНОС'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-04 (post-Task 473-474: ПЕРЕНОС партии из kip8test@d9efdd0f в kip8@30c4339 — ОДНИМ инкрементом SW kipia-v508→v509; заявка 474: «В разделе КИП ИОС, в подробной карточке прибора размер текста типа прибора, расположенного перед картинкой прибора, сделай в полтора раза больше. И текст "№ прибора" и "Место установки" смести немного ниже от верхней границы карточки. Перенеси изменения в боевой kip8.» — команда переноса ПОЛУЧЕНА (473 ждал «по команде» с прошлой сессии; регламент Task 441): Task 473 — график ППР «Приборы» (Графики КИП ИОС, только десктоп): КОРНЕВОЙ фикс зрительной невидимости столбцов (.ppr-bars-row align-items:flex-end→stretch — height:% схлопывался в min-height:2px, ВСЕ столбцы были 2px из 165px) + значение над КАЖДЫМ столбцом («0» пустых месяцев у основания) + ВСПОМОГАТЕЛЬНАЯ ПРАВАЯ ОСЬ 0–50 для малых серий К/П (SECONDARY_SHARE=0.25, data-scale, легенда «(правая ось)»); «Блокировки» — единая шкала, без правой оси; Task 474 — подробная карточка прибора (devRenderDetail — рендер один для десктоп-панели #detailPanel и мобильной #page-device-detail): текст Типа прибора на картинке («перед картинкой») в ПОЛТОРА раза крупнее — .dev-detail-type-overlay font-size 12px→18px (12×1.5=18; вес 600/переносы не тронуты; светлая тема размер не переопределяет) + «№ прибора»/«Место установки» ниже от верхней границы карточки — .dev-detail-meta padding-top 2px→12px (десктопное #detailPanel .dev-detail-meta задаёт только left/right 14px — смещение действует везде); структура карточки/липкий верх Task 334/335/336 НЕ менялись. КЛИЕНТ-ONLY — Apps Script не менялся, серверных шагов НЕТ; тесты 5467/0 = паритет 5461 + 6 task344 (маппинг v698→v509 (540)/v699→v510 (125)/негативы партии v697→v508 + v696→v508 (4)/исторические v695→v507 и далее как в 472; адаптация шапки test-task474 под kip8: «SW: kipia-v508 → v509» + названия тестов v509/v508/v510; test-task344 v508→v509; run-all +473+474; окна истории из kip8test: test-task461 3800/test-task471+472 1300 — дистанции kip8: Task 461 3623 (запас 177), Task 471 1170 (запас 130)), де-изоляция ×15, «дифф диффов» сходится (репо-дифф 59 == эталону kip8test@1bf83f0d↔kip8@98797f3; дифф задач 14 идентичен; charts-desktop.js на базе ИДЕНТИЧЕН — простая копия), SMOKE task473-474-smoke-k8.py 23/23 (порт 8997, ключи без префикса: карточка — computed 18px + смещение ~12px, светлая + мобайл 375; график — 35+1 значений, столбцы видимы К-48≈96%/П-15≈30%/ТО-500=100%, правая ось 50..0; SW kipia-v509; 0 JS ×3), VLM ×2 (карточка: Тип крупный ~18–20px, подписи с отступом, критических дефектов нет; график: числа над столбцами читаются, серии различимы). ПОДВОДНЫЕ КАМНИ: (а) перенос-скрипт ОДНОРАЗОВЫЙ — повторный прогон на применённом состоянии вставляет ДУБЛИКАТЫ require в run-all.js (норма: git checkout -- . + rm новых файлов партии + один чистый прогон; при заботе о чистоте вывода — НЕ перегонять скрипт «для галочки»: каждый лишний прогон добавляет дубль require, удалять вручную); (б) шапка kip8test-файла test-task474 «SW: kipia-test-v697 → v698.» — маппинг версий заменяет только ПОЛНУЮ форму (kipia-test-v697→kipia-v508), короткий хвост «v698» и названия тестов остаются — точечная адаптация fixes[] в перенос-скрипте (4 замены). DEPLOY-Task474-device-card-type-x15-meta-lower.md скопирован (КЛИЕНТ-ONLY; для Task 473 DEPLOY-файла нет — статический ассет). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v509` (guard v510), тесты 5467/0; kip8test @d9efdd0f SW `kipia-test-v698` (guard v699), тесты 5461/0 — партия 473+474 выкачана в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 475 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-472')
    sys.exit(1)

n_prev_before = src.count(PREV_MARK)

i3 = src.index(CUR_MARK)
i3end = src.index('\n', i3)
old_line3 = src[i3:i3end]

# (а) удалить самую старую строку «предыдущая» (храним 2 последних)
if src.count(PREV_MARK) > 2:
    iprev = src.rindex(PREV_MARK)
    iprev_end = src.index('\n', iprev)
    src = src[:iprev] + src[iprev_end + 1:]

# (б) строка 3 → новая версия + «предыдущая» из старой строки 3
new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
src = src[:i3] + NEW_LINE3 + '\n' + new_prev + src[i3end:]

# (в) «Текущая версия кэша» v508 → v509
old_cache = '> **Текущая версия кэша:** `kipia-v508`'
new_cache = '> **Текущая версия кэша:** `kipia-v509`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v696` → `kipia-test-v697` (для kip8test) или `kipia-v507` → `kipia-v508` (для kip8)'
new_inc = 'Формат: `kipia-test-v698` → `kipia-test-v699` (для kip8test) или `kipia-v509` → `kipia-v510` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5399/5393 → 5467/5461
old_exp = '# Ожидается: 5399 passed, 0 failed (kip8; в kip8test — 5393 passed, 0 failed)'
new_exp = '# Ожидается: 5467 passed, 0 failed (kip8; в kip8test — 5461 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# проверки
checks = [
    ('post-Task 473-474: ПЕРЕНОС партии из kip8test@d9efdd0f', 1),
    ('Версия документа (предыдущая):** 2026-10-03 (post-Task 472: ПЕРЕНОС', 1),
    ('5467 passed, 0 failed (kip8', 1),
    ('kipia-v509', None),
    ('СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 475', 1),
    ('font-size 12px→18px', None),
    ('padding-top 2px→12px', None),
]
for marker, cnt in checks:
    c = src.count(marker)
    if cnt is not None and c != cnt:
        print('ОШИБКА: маркер %r найден %d раз (ожидалось %s)' % (marker[:60], c, cnt))
        sys.exit(1)
    if cnt is None and c == 0:
        print('ОШИБКА: маркер не найден: %r' % marker[:60])
        sys.exit(1)
if src.count(PREV_MARK) != n_prev_before:
    print('ОШИБКА: длина цепочки «предыдущих» изменилась (%d → %d)' %
          (n_prev_before, src.count(PREV_MARK)))
    sys.exit(1)

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('промт kip8: post-473-474 ПЕРЕНОС записан (кэш v509, тесты 5467/0, '
      'следующий 475)')
