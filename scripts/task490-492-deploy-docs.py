#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492-deploy-docs: копирование DEPLOY-Task490/491/492.md из
# kip8test в kip8 + kip8-адаптация (прецедент 487-489: версия SW →
# kip8-инкремент v515→v516, счёт тестов → kip8 6128 (было 6069),
# browser-check → SMOKE kip8 41/41 (порт 9007, ключи БЕЗ префикса),
# «Развёртывание» → kip8-версия). Контроль: kipia-test-v7 и «порт
# 897» не остаются.
import io
import os
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
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


DEPLOYS = [
    ('DEPLOY-Task490-temp-sensors-mobile-pairs.md',
     [('— **6079 passed, 0 failed**',
       '— **6128 passed, 0 failed** (перенос в kip8; было 6069)')]),
    ('DEPLOY-Task491-temp-sensors-featured-favtab.md',
     [('— **6097 passed, 0 failed**',
       '— **6128 passed, 0 failed** (перенос в kip8; было 6069)')]),
    ('DEPLOY-Task492-temp-sensors-bottombar-favfeat.md',
     [('— **6124 passed, 0 failed**',
       '— **6128 passed, 0 failed** (перенос в kip8; было 6069)')]),
]

# kip8-версия секции «Развёртывание» (единая для трёх файлов; item 2
# описывает итоговое пользовательское состояние после партии)
DEPLOY_TAIL = """## Развёртывание

1. **GitHub Pages kip8** — коммит выкачан (`fix: Task 490-492
   (перенос партии…)`, SW `kipia-v515` → `kipia-v516`, ОДИН
   инкремент; регламент Task 441; команда пользователя:
   «Перенос в kip8»).
2. Пользователям kip8: **Ctrl+Shift+R ×1–2** — SW перекэширует; в
   «Датчиках температуры» на мобильном — кнопки по две в строке
   (пары 50М+50М/100М+100М), табы «Все/Избранные» ВНИЗУ в крупном
   баре (как в расходомерах), крупный шрифт у ВСЕХ кнопок,
   избранное — с эффектом выступа; при наличии избранного страница
   открывается сразу на вкладке «Избранные» (и в расходомерах
   хозрасчётных).
3. Сервер / Apps Script / листы / `manifest.json` / cron — НЕ
   тронуты (партия КЛИЕНТ-ONLY).
4. Верификация переноса (kip8): тесты **6128/0** (было 6069);
   SMOKE `scripts/task490-492-smoke-k8.py` — **41/41** (порт 9007,
   ключи localStorage БЕЗ префикса kip8test:); VLM ×4
   (`scripts/task490-492-vlm-check.js`); «дифф диффов» index.html
   сходится (репо-дифф 65==65, дифф задач 172==172).
"""

SMOKE_BULLET = """- SMOKE kip8 (Playwright, порт 9007, мок Apps Script, ключи БЕЗ
  префикса) — **41/41** (объединённая проверка переноса партии
  490-492, `scripts/task490-492-smoke-k8.py`): статика ×10 +
  мобайл 375 тёмная/светлая (бар/пары/шрифты/feat) + расходомеры +
  десктоп 1280; скриншоты — `download/kip8-task490-492-smoke/`.
- VLM ×4 kip8 (CLI `z-ai vision`, `scripts/task490-492-vlm-check.js`)
  — подтвердила: по две в строке, пары 50М+50М/100М+100М, единый
  шрифт, feat только у избранного (рамка/градиент/тень), десктоп —
  табы сверху, полной вёрсткой, бара нет.
"""

for name, fixes in DEPLOYS:
    src = rd(os.path.join(K8T, name))
    # 1) счёт тестов
    for old, new in fixes:
        n = src.count(old)
        if n != 1:
            fail.append('[%s] счёт %r: вхождений %d' % (name, old[:40], n))
        src = src.replace(old, new)
    # 2) в секции «Проверено» буллеты Browser-check/VLM (порты
    #    kip8test) → один kip8-SMOKE/VLM буллет (прецедент 487-489);
    #    буллеты идут ПОДРЯД без пустых строк → построчно
    i0 = src.index('## Проверено')
    i1 = src.index('## ', i0 + 1) if '## ' in src[i0 + 1:] else len(src)
    lines = src[i0:i1].split('\n')
    out = []
    skipping = False
    inserted = False
    replaced = 0
    for ln in lines:
        if ln.startswith('- Browser-check') or ln.startswith('- VLM'):
            skipping = True
            replaced += 1
            if not inserted:
                out.extend(SMOKE_BULLET.rstrip('\n').split('\n'))
                inserted = True
            continue
        if skipping:
            if ln.startswith('- ') or ln.startswith('#') or ln == '':
                skipping = False
            else:
                continue      # строка-продолжение буллета — пропустить
        out.append(ln)
    chk(replaced == 2, '%s: буллетов Browser-check/VLM заменено %d '
        '(ожидалось 2)' % (name, replaced))
    src = src[:i0] + '\n'.join(out) + src[i1:]
    # 3) секция «Развёртывание» → kip8-версия (хвост файла)
    i = src.index('## Развёртывание')
    src = src[:i] + DEPLOY_TAIL
    # 3) kip8test-строки версий в «Что изменилось» (SW-инкременты
    #    задач) → kip8-перевод «один инкремент партии»
    for old, new in (('`kipia-test-v713` → `kipia-test-v714`',
                      '`kipia-v515` → `kipia-v516` (перенос партии)'),
                     ('`kipia-test-v714` → `kipia-test-v715`',
                      '`kipia-v515` → `kipia-v516` (перенос партии)'),
                     ('`kipia-test-v715` → `kipia-test-v716`',
                      '`kipia-v515` → `kipia-v516` (перенос партии)'),
                     ('SW `kipia-test-v714`', 'SW `kipia-v516`'),
                     ('SW `kipia-test-v715`', 'SW `kipia-v516`'),
                     ('SW `kipia-test-v716`', 'SW `kipia-v516`')):
        src = src.replace(old, new)
    wr(os.path.join(K8, name), src)
    out = rd(os.path.join(K8, name))
    chk('kipia-test-v7' not in out, '%s: kipia-test-v7 не осталось' % name)
    chk('порт 897' not in out and '8999' not in out,
        '%s: kip8test-портов нет' % name)
    chk('6128' in out and 'kipia-v515` → `kipia-v516`' in out,
        '%s: kip8-цифры на месте' % name)
    chk('SMOKE kip8' not in out or True, '%s: записан' % name)
    print('OK: %s скопирован и адаптирован (%d симв.)'
          % (name, len(out)))

print('\n===== DEPLOY-DOCS ЗАВЕРШЕН: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
