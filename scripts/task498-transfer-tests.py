#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 498: адаптация тестов kip8 ПЕРЕД бампом версии (урок 497).

(1) Заголовки Task 498 (только тип датчика): test-task372/373/495.
(2) Окна истории sw.js по ЗАМЕРУ kip8-геометрии (после комментария
    498, +317 симв.): 461@13204 471@10751 472@10199 473@9824
    474@9690 478@8628 479@8048 480@8034 481@7790 482@4811
    (_barExpMaxH@7384) 483@6676 484@6771 485@6337 486@5595
    488@4377 493@1557 494@1381 495@1182.
    НЕ расширяются (проходят с малым запасом — прецедент «запас 18»):
    474 9700 (запас 10), 472 10300 (101), 480 8100 (66),
    482 7400 (16), 483 6700 (24), 486 5600 (5).
(3) Каскады синхронизации (475/481/486) — под новые литералы.
"""
import io

T = '/home/z/my-project/kip8/tests/'


def apply(fname, edits, must=True):
    path = T + fname
    s = io.open(path, encoding='utf-8').read()
    for old, new in edits:
        n = s.count(old)
        if must:
            assert n >= 1, '%s: НЕТ якоря %r' % (fname, old[:60])
        if n:
            s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('OK', fname, '(правок: %d)' % len(edits))


# ---------- (1) заголовки Task 498 ----------
apply('test-task372.js', [
    ("assertEqual(vmw.els['tempSensorViewTitle'].textContent, '50М (Cu50) — термометр сопротивления',",
     "assertEqual(vmw.els['tempSensorViewTitle'].textContent, '50М (Cu50) α = 0,00428 °C⁻¹',"),
    ("assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТХА (K) — термопара', 'заголовок ТП');",
     "assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТХА (K)', 'заголовок ТП');"),
    ("assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТПР (B) — термопара', 'новый заголовок');",
     "assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТПР (B)', 'новый заголовок');"),
    ("assertTrue(INDEX_SRC.indexOf('updateDesktopBreadcrumb(null, s372.name)') !== -1,\n            'крошки: имя датчика вместо статической метки');",
     "assertTrue(INDEX_SRC.indexOf('updateDesktopBreadcrumb(null, l498)') !== -1,\n            'крошки: тип датчика (Task 498: с α) вместо статической метки');"),
])
apply('test-task373.js', [
    ("assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТХК (L) — термопара', 'заголовок');",
     "assertEqual(vmw.els['tempSensorViewTitle'].textContent, 'ТХК (L)', 'заголовок');"),
])
apply('test-task495.js', [
    ("assertEqual(vmw.els['tempSensorViewTitle'].textContent,\n            '50М (Cu50) — термометр сопротивления',",
     "assertEqual(vmw.els['tempSensorViewTitle'].textContent,\n            '50М (Cu50) α = 0,00428 °C⁻¹',"),
])

# ---------- (2) окна истории (по kip8-геометрии) ----------
W = {}
W['test-task461.js'] = [('i - 13200', 'i - 14000'), ('< 13200', '< 14000')]        # 461@13204
W['test-task471.js'] = [('i - 10600', 'i - 11200'), ('< 10600', '< 11200')]        # 471@10751
W['test-task472.js'] = [('i - 10600', 'i - 11200'), ('< 10600', '< 11200')]        # 471@10751
W['test-task473.js'] = [('i - 9700', 'i - 10600'), ('< 9700', '< 10600')]          # 473@9824
W['test-task474.js'] = [('i - 10600', 'i - 11200'), ('< 10600', '< 11200'),
                        ('i - 13200', 'i - 14000'), ('< 13200', '< 14000')]        # 471/461
W['test-task476.js'] = [('i - 9600', 'i - 10400'), ('< 9600', '< 10400'),          # 474@9690
                        ('i - 9900', 'i - 10800'), ('< 9900', '< 10800'),          # 472@10199
                        ('i - 10600', 'i - 11200'), ('< 10600', '< 11200'),
                        ('i - 13200', 'i - 14000'), ('< 13200', '< 14000')]
W['test-task477.js'] = W['test-task476.js']
W['test-task478.js'] = [('i - 8400', 'i - 9200'), ('< 8400', '< 9200')] + W['test-task476.js']
W['test-task479.js'] = W['test-task478.js']
W['test-task481.js'] = [('i - 7500', 'i - 8300'), ('< 7500', '< 8300')] + W['test-task478.js']
W['test-task482.js'] = [('i - 8400', 'i - 9200'), ('< 8400', '< 9200')] + \
                       [('i - 9600', 'i - 10400'), ('< 9600', '< 10400'),
                        ('i - 9900', 'i - 10800'), ('< 9900', '< 10800'),
                        ('i - 10600', 'i - 11200'), ('< 10600', '< 11200'),
                        ('i - 13200', 'i - 14000'), ('< 13200', '< 14000')]
W['test-task484.js'] = [('i - 6700', 'i - 7500'), ('< 6700', '< 7500')]            # 484@6771
W['test-task485.js'] = [('i - 6300', 'i - 7000'), ('< 6300', '< 7000')]            # 485@6337
W['test-task488.js'] = [('i - 4100', 'i - 5000'), ('< 4100', '< 5000')]            # 488@4377
W['test-task493.js'] = [('i - 1400', 'i - 2100'), ('< 1400', '< 2100')]            # 493@1557
W['test-task494.js'] = [('i - 1200', 'i - 1900'), ('< 1200', '< 1900')]            # 494@1381
W['test-task495.js'] = W['test-task495.js'] if 'test-task495.js' in W else \
    [('i - 900', 'i - 1600'), ('< 900', '< 1600')]                                  # 495@1182

for f, edits in W.items():
    # 495 уже получила правку заголовка выше — применяем окна отдельно
    apply(f, edits, must=False)

# ---------- (3) каскады ----------
apply('test-task475.js', [
    ("assertTrue(s.indexOf('i - 13200') !== -1, 'окно 12400 (Task 492)');",
     "assertTrue(s.indexOf('i - 14000') !== -1, 'окно 14000 (Task 498)');"),
    ("assertTrue(s1.indexOf('i - 10600') !== -1, 'test-task471: 10600 (Task 495)');",
     "assertTrue(s1.indexOf('i - 11200') !== -1, 'test-task471: 11200 (Task 498)');"),
    ("assertTrue(s2.indexOf('i - 10600') !== -1, 'test-task472: 10600 (Task 495)');",
     "assertTrue(s2.indexOf('i - 11200') !== -1, 'test-task472: 11200 (Task 498)');"),
])
# 481-каскады покрыты W-циклом (литералы 'i - 13200'/'i - 10600' в его
# sync-тесте совпадают с оконными — заменились вместе); проверяем:
apply('test-task481.js', [
    ("assertTrue(s461.indexOf('i - 13200') !== -1,",
     "assertTrue(s461.indexOf('i - 14000') !== -1,"),
    ("assertTrue(s471.indexOf('i - 10600') !== -1,",
     "assertTrue(s471.indexOf('i - 11200') !== -1,"),
], must=False)
apply('test-task486.js', [
    ("assertTrue(s475.indexOf(\"'i - 13200'\") !== -1, 'каскад 475: 461 → 13200 (Task 496)');",
     "assertTrue(s475.indexOf(\"'i - 14000'\") !== -1, 'каскад 475: 461 → 14000 (Task 498)');"),
    ("assertTrue(s482.indexOf(\"'i - 8400'\") !== -1, 'каскад 482: 478/479 → 8400 (Task 495)');",
     "assertTrue(s482.indexOf(\"'i - 9200'\") !== -1, 'каскад 482: 478/479 → 9200 (Task 498)');"),
    ("assertTrue(s484.indexOf('i - 6700') !== -1, '484: собственное окно (Task 487/490/491/494)');",
     "assertTrue(s484.indexOf('i - 7500') !== -1, '484: собственное окно (Task 487/490/491/494/498)');"),
])

print('Адаптации kip8 готовы (бамп версии — следующим скриптом).')
