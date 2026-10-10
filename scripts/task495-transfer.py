#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 495 — ПЕРЕНОС в kip8 (регламент Task 441, команда из заявки
«Сразу вноси изменения и в kip8»).

Переносит финальные (post-Task-495) регионы kip8test/index.html в
kip8/index.html — исходные блоки в обоих репо идентичны (проверено
diff-ами: HTML-блок, CSS-блок и openTempSensor совпадают дословно):
  R1. HTML: панель произвольного расчёта + НОВЫЙ блок таблицы
      (ts-calc-inset) — от комментария Task 373 до кнопки «Рассчитать».
  R2a. CSS: блок Task 494 (панель/поля) + новые правила углубления —
      от комментария Task 494 до светлого inset-правила.
  R2b. CSS: снятые правила чипа .ts-view-chip*.
  R3. JS: openTempSensor без чипа.
  SW: kipia-v518 → kipia-v519 + комментарий Task 495 (дословно из
      kip8test/sw.js).
"""
import io
import sys

KT = '/home/z/my-project/kip8test'
K8 = '/home/z/my-project/kip8'
OK = True


def fail(msg):
    global OK
    OK = False
    print('FAIL: ' + msg)


kts = io.open(KT + '/index.html', encoding='utf-8').read()
k8s = io.open(K8 + '/index.html', encoding='utf-8').read()
kt_sw = io.open(KT + '/sw.js', encoding='utf-8').read()
k8_sw = io.open(K8 + '/sw.js', encoding='utf-8').read()


def region(src, start, end, include_end=False):
    a = src.find(start)
    if a == -1:
        fail('маркер начала не найден: %r' % start[:60])
        return None
    if include_end:
        b = src.find(end, a)
        if b == -1:
            fail('маркер конца не найден: %r' % end[:60])
            return None
        b += len(end)
    else:
        b = src.find(end, a)
        if b == -1:
            fail('маркер конца не найден: %r' % end[:60])
            return None
    return src[a:b]


def line_end(src, marker):
    a = src.find(marker)
    if a == -1:
        fail('маркер не найден: %r' % marker[:60])
        return None
    b = src.find('\n', a)
    return src[a:b + 1]


# --- R1. HTML: панель ППР + новый блок таблицы -----------------------
r1_start = '                    <!-- Task 373: «Расчёт произвольных значений» (Task 371) —'
r1_end = ('            <button type="button" class="converter-convert-btn" '
          'onclick="calcTempSensor()">')
kt_r1 = region(kts, r1_start, r1_end)
k8_r1 = region(k8s, r1_start, r1_end)
if kt_r1 and k8_r1:
    if kt_r1 == k8_r1:
        fail('R1: регионы уже совпадают (перенос не нужен?)')
    else:
        k8s = k8s.replace(k8_r1, kt_r1, 1)
        print('OK R1: HTML-блок панели таблицы перенесён (%d → %d симв.)' %
              (len(k8_r1), len(kt_r1)))

# --- R2a. CSS: Task 494 + Task 495 (углубление) -----------------------
r2_start = '    /* Task 494: панель произвольного расчёта — эффект ВЫСТУПА по образцу'
kt_r2 = None
k8_r2 = None
a = kts.find(r2_start)
if a != -1:
    b = kts.find('\n', kts.find('[data-theme="light"] .ts-calc-panel.ts-calc-inset {'))
    kt_r2 = kts[a:b + 1]
else:
    fail('R2: нет начала Task 494 CSS в kip8test')
c = k8s.find(r2_start)
if c != -1:
    d = k8s.find('\n', k8s.find('[data-theme="light"] .ts-calc-field:focus {', c))
    k8_r2 = k8s[c:d + 1]
else:
    fail('R2: нет начала Task 494 CSS в kip8')
if kt_r2 and k8_r2:
    k8s = k8s.replace(k8_r2, kt_r2, 1)
    print('OK R2a: CSS-блок панелей перенесён (%d → %d симв.)' %
          (len(k8_r2), len(kt_r2)))

# --- R2b. CSS: снятые правила чипа ------------------------------------
chip_k8 = region(k8s,
                 '    /* Task 372: чип выбранного датчика на странице датчика */',
                 '    .ts-view-chip-meta {', include_end=False)
if chip_k8:
    chip_k8_full = line_end(k8s, '    .ts-view-chip-meta {')
    chip_k8 = k8s[k8s.find('    /* Task 372: чип выбранного датчика на странице датчика */'):
                  k8s.find('\n', k8s.find('    .ts-view-chip-meta {')) + 1]
chip_kt = region(kts,
                 '    /* Task 372: чип выбранного датчика — Task 495: чип удалён из',
                 '       CSS-правила чипа сняты как неиспользуемые. */\n',
                 include_end=True)
if chip_k8 and chip_kt:
    k8s = k8s.replace(chip_k8, chip_kt, 1)
    print('OK R2b: правила чипа сняты (%d → %d симв.)' %
          (len(chip_k8), len(chip_kt)))

# --- R3. JS: openTempSensor без чипа ----------------------------------
js_old = (
    "        let chip=document.getElementById('tempSensorViewChip');\n"
    '        // Task 373: бейдж ТС/ТП убран из чипа — только имя и параметры\n'
    "        if(chip){chip.innerHTML='<span class=\"ts-view-chip-name\">'"
    "+sel.name+'</span><span class=\"ts-view-chip-meta\">'+sel.meta"
    "+'</span>';}\n"
)
js_new = region(kts,
                '        // Task 495: чип типа датчика удалён из блока ввода — тип\n',
                '        // датчика виден в заголовке страницы\n',
                include_end=True)
n = k8s.count(js_old)
if n != 1:
    fail('R3: JS-чип найден %d раз (ожидался 1)' % n)
elif js_new:
    k8s = k8s.replace(js_old, js_new, 1)
    print('OK R3: openTempSensor — чип убран (%d → %d симв.)' %
          (len(js_old), len(js_new)))

io.open(K8 + '/index.html', 'w', encoding='utf-8').write(k8s)

# --- SW: версия + комментарий -----------------------------------------
sw_old = (
    "// Task 494: «Датчики температуры» — панель произвольного расчёта\n"
    "// (tempCustomCalcPanel) без заголовка/подсказки, эффект выступа\n"
    "// (рамка 2px + градиент + тень), поля крупнее и ярче. Клиент-only.\n"
    "const CACHE_VERSION = 'kipia-v518';"
)
c495 = region(kt_sw, '// Task 495: «Датчики температуры» — блок ввода данных расчёта\n',
              'const CACHE_VERSION =', include_end=False)
sw_new = (
    "// Task 494: «Датчики температуры» — панель произвольного расчёта\n"
    "// (tempCustomCalcPanel) без заголовка/подсказки, эффект выступа\n"
    "// (рамка 2px + градиент + тень), поля крупнее и ярче. Клиент-only.\n"
    + (c495 or '') +
    "const CACHE_VERSION = 'kipia-v519';"
)
if k8_sw.count(sw_old) != 1:
    fail('SW: якорь версии не найден (единожды)')
else:
    k8_sw = k8_sw.replace(sw_old, sw_new, 1)
    io.open(K8 + '/sw.js', 'w', encoding='utf-8').write(k8_sw)
    print('OK SW: kipia-v518 → v519 + комментарий Task 495 (%d симв.)' %
          len(c495 or ''))

# --- Контроли ---------------------------------------------------------
k8s2 = io.open(K8 + '/index.html', encoding='utf-8').read()
for gone in ['Тип датчика', 'Шаг расчёта таблицы в градусах Цельсия',
             'tempSensorViewChip', 'ts-view-chip']:
    if k8s2.count(gone):
        fail('в kip8/index.html осталось %r x%d' % (gone, k8s2.count(gone)))
    else:
        print('Контроль: %r отсутствует в kip8/index.html' % gone)
for must in ['ts-calc-inset', 'tempTableFormPanel',
             'class="ts-calc-panel ts-calc-inset"']:
    if not k8s2.count(must):
        fail('в kip8/index.html нет %r' % must)
    else:
        print('Контроль: %r есть (x%d)' % (must, k8s2.count(must)))

# идентичность перенесённых регионов между репо
kt2 = io.open(KT + '/index.html', encoding='utf-8').read()
for name, start, end in [
    ('R1', r1_start, r1_end),
    ('R2a', r2_start, '[data-theme="light"] .ts-calc-panel.ts-calc-inset {'),
]:
    a1, a2 = kt2.find(start), k8s2.find(start)
    if a1 == -1 or a2 == -1:
        fail('контроль %s: маркер не найден' % name)
        continue
    if name == 'R1':
        r_kt = kt2[a1:kt2.find(r1_end, a1)]
        r_k8 = k8s2[a2:k8s2.find(r1_end, a2)]
    else:
        r_kt = kt2[a1:kt2.find('\n', kt2.find(end, a1)) + 1]
        r_k8 = k8s2[a2:k8s2.find('\n', k8s2.find(end, a2)) + 1]
    if r_kt == r_k8:
        print('Контроль: регион %s идентичен kip8test' % name)
    else:
        fail('регион %s отличается от kip8test' % name)

# openTempSensor идентичен
def fn_of(src, name):
    i = src.find('function ' + name + '(')
    j = src.find('{', i)
    d = 0
    k = j
    while True:
        if src[k] == '{':
            d += 1
        elif src[k] == '}':
            d -= 1
            if d == 0:
                return src[i:k + 1]
        k += 1

if fn_of(kt2, 'openTempSensor') == fn_of(k8s2, 'openTempSensor'):
    print('Контроль: openTempSensor идентичен kip8test')
else:
    fail('openTempSensor отличается от kip8test')

print('RESULT: %s' % ('OK' if OK else 'FAIL'))
sys.exit(0 if OK else 1)
