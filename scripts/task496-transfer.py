#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 496 — ПЕРЕНОС из kip8test@f1e9be83→a3006907 в kip8
# (регламент Task 441: ОДИН инкремент SW kipia-v519 → v520).
#
# Заявка: «В блоке произвольного расчёта, после ввода одного из
# данных и при нажатии подтверждения на клавиатуре, клавиатура
# должна закрываться, а не перемещаться по следующим полям ввода.»
#
# Регионы-трансплантаты (проверено: ППР pre-496 kip8test ==
# ППР kip8, JS-якорь 371 идентичен):
#   R1 — ППР HTML (комментарий 373/494/496 + панель ППР):
#        '<!-- Task 373:' … до 'id="tempTableFormPanel"';
#   R2 — JS-хелпер tempQueryEnterBlur (preventDefault +
#        stopPropagation + blur) перед '// Task 371: живой расчёт';
#   R3 — sw.js: комментарий Task 496 + kipia-v519 → v520.
import io

T8 = '/home/z/my-project/kip8test/index.html'
K8 = '/home/z/my-project/kip8/index.html'
SWT = '/home/z/my-project/kip8test/sw.js'
SWK = '/home/z/my-project/kip8/sw.js'

t8 = io.open(T8, encoding='utf-8').read()
k8 = io.open(K8, encoding='utf-8').read()


def region(src, a, b):
    i = src.find(a)
    j = src.find(b, i)
    assert i != -1 and j != -1, (a[:40], b[:40])
    return src[i:j], i, j


# ---------- R1: ППР HTML ----------
A, B = '<!-- Task 373:', 'id="tempTableFormPanel"'
new_ppr, _, _ = region(t8, A, B)
old_ppr, i, j = region(k8, A, B)
assert old_ppr != new_ppr, 'ППР уже перенесён?'
assert 'tempQueryEnterBlur(event,this)' in new_ppr
assert 'enterkeyhint="done"' in new_ppr
assert 'enterkeyhint="next">' not in new_ppr  # тег-форма; в комментарии упоминание старого next законно
assert 'Task 496' in new_ppr
k8 = k8[:i] + new_ppr + k8[j:]
print('R1: ППР HTML (комментарий + панель) трансплантирован '
      '(%d → %d симв.)' % (len(old_ppr), len(new_ppr)))

# ---------- R2: JS-хелпер ----------
i = t8.find('    // Task 496 (заявка): в блоке произвольного')
j = t8.find('    // Task 371: живой расчёт «температура')
fn496 = t8[i:j]
assert 'function tempQueryEnterBlur(e, el){' in fn496
assert 'stopPropagation' in fn496
anchor = '    // Task 371: живой расчёт «температура → R/E» (ввод в поле температуры)\n    function tempQueryFromTemp(){'
assert k8.count(anchor) == 1, 'якорь 371: %d' % k8.count(anchor)
assert 'function tempQueryEnterBlur' not in k8  # до R2 функции нет (атрибуты уже вставлены R1)
k8 = k8.replace(anchor, fn496 + anchor)
print('R2: JS-хелпер tempQueryEnterBlur вставлен (%d симв.)' % len(fn496))

io.open(K8, 'w', encoding='utf-8').write(k8)

# ---------- R3: sw.js ----------
sw = io.open(SWK, encoding='utf-8').read()
old_sw = """// Task 495: «Датчики температуры» — блок ввода данных расчёта
// таблицы: поле типа датчика (чип) с подписью и подсказка про шаг
// пересчёта удалены; блок оформлен как панель произвольного
// расчёта, но с эффектом УГЛУБЛЕНИЯ (ts-calc-inset). Клиент-only.
const CACHE_VERSION = 'kipia-v519';"""
new_sw = """// Task 495: «Датчики температуры» — блок ввода данных расчёта
// таблицы: поле типа датчика (чип) с подписью и подсказка про шаг
// пересчёта удалены; блок оформлен как панель произвольного
// расчёта, но с эффектом УГЛУБЛЕНИЯ (ts-calc-inset). Клиент-only.
// Task 496: «Датчики температуры» — панель произвольного расчёта:
// кнопка подтверждения («Готово»/Enter) мобильной клавиатуры
// закрывает клавиатуру (enterkeyhint done + tempQueryEnterBlur),
// а не перескакивает на следующее поле. Клиент-only.
const CACHE_VERSION = 'kipia-v520';"""
assert sw.count(old_sw) == 1, 'sw.js: %d' % sw.count(old_sw)
sw = sw.replace(old_sw, new_sw)
io.open(SWK, 'w', encoding='utf-8').write(sw)
print('R3: sw.js kipia-v519 → v520 + комментарий Task 496')

# ---------- Контроли ----------
chk = io.open(K8, encoding='utf-8').read()
ppr = region(chk, A, B)[0]
assert ppr == new_ppr, 'R1: регион не равен донору'
assert ppr.count('tempQueryEnterBlur(event,this)') == 2  # атрибуты (в комментарии — без (event,this))
assert ppr.count('enterkeyhint="done">') == 2  # теги; в комментарии 496 упоминания done — законны
assert 'enterkeyhint="next">' not in ppr
tbl = region(chk, '<div class="ts-calc-panel ts-calc-inset" id="tempTableFormPanel">',
             'onclick="calcTempSensor()"')[0]
assert tbl.count('enterkeyhint="next"') == 2, 'блок таблицы не тронут (next×2)'
assert 'tempQueryEnterBlur' not in tbl
assert chk.count('function tempQueryEnterBlur') == 1
glob = chk[chk.find('// Обработчик Enter/Next на клавиатуре'):
           chk.find('// Обработчик Enter/Next на клавиатуре') + 1400]
assert "fields[idx + 1].focus();" in glob, 'глобальный Enter-переход жив'
swk = io.open(SWK, encoding='utf-8').read()
assert "const CACHE_VERSION = 'kipia-v520'" in swk
assert 'kipia-v519' not in swk
# соответствие kip8test: JS-функция идентична донору
assert fn496 in chk
print('Контроли: ППР done×2 + onkeydown×2 + stopPropagation; блок таблицы '
      'next×2 НЕ тронут; глобальный переход жив; SW v520. Всё ок.')
