#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 531 — ожидание CI kip8 + синка в kip8-desktop + kip8test зеркала
import json
import subprocess
import sys
import time

PAT = open('/home/z/.kip_pat').read().strip()

CHECKS = [
    ('kip8', 'bloknett-design/kip8', '107b80f'),
    ('kip8-desktop', 'bloknett-design/kip8-desktop', None),   # синк от kip8
]

def gh(path):
    out = subprocess.check_output(
        ['curl', '-s', '-m', '25', '-H',
         'Authorization: Bearer ' + PAT,
         'https://api.github.com/' + path])
    return json.loads(out.decode())


def wait_repo(repo, sha):
    for i in range(60):
        runs = gh('repos/%s/actions/runs?per_page=10' % repo)
        seen = {}
        for r in runs.get('workflow_runs', []):
            if r.get('head_sha', '').startswith(sha):
                seen[r.get('name')] = (r.get('status'), r.get('conclusion'))
        if seen and all(s == 'completed' for s, _ in seen.values()):
            return seen
        time.sleep(12)
    return None


print('== kip8 CI @107b80f ==')
res = wait_repo('bloknett-design/kip8', '107b80f')
fail = False
if not res:
    print('  TIMEOUT')
    fail = True
else:
    for n, (s, c) in sorted(res.items()):
        print('  %-40s %s' % (n[:40], c))
        if c != 'success':
            fail = True

print('== kip8-desktop sync (ждём коммит синка от kip8@107b80f) ==')
ok = False
for i in range(50):
    commits = gh('repos/bloknett-design/kip8-desktop/commits?per_page=3')
    for c in commits:
        msg = c['commit']['message']
        if 'sync content from kip8@107b80f' in msg:
            ok = True
            sha = c['sha'][:10]
            print('  синк-коммит найден: %s' % sha)
            break
    if ok:
        break
    time.sleep(12)
if not ok:
    print('  TIMEOUT: синк не появился')
    fail = True

sys.exit(1 if fail else 0)
