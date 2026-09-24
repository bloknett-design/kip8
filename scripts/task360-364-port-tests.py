#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task360-364-port-tests.py — перенос тестов Tasks 360–364 из
# kip8test в kip8 (запускать из корня kip8).
# Версионный маппинг (5 задач пакета: v437=360 … v441=364):
#   kipia-test-v593 → kipia-v441   (текущая — asserts)
#   kipia-test-v594 → kipia-v442   (guard «ещё не существует»)
#   'kipia-test-v59' → 'kipia-v44' (нет захардкоженных версий в index.html)
# Исторические guard-версии (v514/v517/v523/…, «старая убрана»)
# остаются как в kip8test — это принятое соглашение kip8 (guard
# тривиально истинен, но файл = эталон kip8test).
# Файлы: адаптированные общие (363/361/362 правили их) + новые 360–364.
import io, os, sys

SRC = '/home/z/my-project/kip8test/tests'
DST = 'tests'

COMMON = ['test-task319.js', 'test-task341.js', 'test-task342.js',
          'test-task343.js', 'test-task355.js', 'test-work-schedule.js']
NEW = ['test-task360.js', 'test-task361.js', 'test-task362.js',
       'test-task363.js', 'test-task364.js']

def adapt(s):
    # порядок важен: сначала v594 (guard), затем v593, затем префикс v59
    s = s.replace('kipia-test-v594', 'kipia-v442')
    s = s.replace('kipia-test-v593', 'kipia-v441')
    s = s.replace("INDEX_SRC.indexOf('kipia-test-v59')",
                  "INDEX_SRC.indexOf('kipia-v44')")
    s = s.replace('v594 ещё не существует', 'v442 ещё не существует')
    # комментарий-шапка
    s = s.replace('//   SW: kipia-v441.', '//   SW: kipia-v441.')
    return s

for name in COMMON + NEW:
    src = io.open(os.path.join(SRC, name), encoding='utf-8').read()
    out = adapt(src)
    rest = [w for w in out.split() if w.startswith('kipia-test-v') and
            not any(x in w for x in ('v514','v515','v516','v517','v523',
                                     'v525','v527','v539','v546'))]
    if rest:
        print('ОСТАЛИСЬ тест-версии в %s: %s' % (name, sorted(set(rest))))
        sys.exit(1)
    io.open(os.path.join(DST, name), 'w', encoding='utf-8').write(out)
    kind = 'адаптирован' if name in COMMON else 'перенесён'
    print('%s: %s' % (name, kind))

print('OK: %d файлов' % (len(COMMON) + len(NEW)))
