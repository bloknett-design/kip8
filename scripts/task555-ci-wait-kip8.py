#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 555 — ожидание CI kip8 (CI Tests + Deploy GitHub Pages +
Sync content to kip8-desktop). Токен — из remote.origin.url git
(секрет в файлах репозитория НЕ хранится — push protection;
в лог НЕ печатается)."""
import json
import re
import subprocess
import sys
import time
import urllib.request

SHA = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
REMOTE = subprocess.check_output(
    ['git', 'config', '--get', 'remote.origin.url'],
    cwd='/home/z/my-project/kip8', text=True).strip()
m = re.search(r'x-access-token:([^@]+)@', REMOTE)
PAT = m.group(1) if m else ''
if not PAT:
    print('токен в remote.origin.url не найден — выход')
    sys.exit(2)
HDRS = {'Authorization': 'Bearer ' + PAT,
        'Accept': 'application/vnd.github+json'}
REPO = 'kip8'


def runs():
    url = ('https://api.github.com/repos/bloknett-design/%s/actions/runs'
           '?head_sha=%s&per_page=30' % (REPO, SHA))
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['workflow_runs']


def wait(name_kw, timeout_s=900):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        for r in runs():
            if name_kw in r['name']:
                if r['status'] != 'completed':
                    time.sleep(15)
                    break
                print('%s: %s' % (r['name'], r['conclusion']))
                return r['conclusion'] == 'success'
        else:
            time.sleep(15)
    print('%s: TIMEOUT' % name_kw)
    return False


ok_ci = wait('CI Tests', 900)
ok_sync = wait('Sync content to kip8-desktop', 900)
ok_pages = wait('Deploy GitHub Pages', 900)
ok = ok_ci and ok_sync and ok_pages
print('CI kip8: %s' % ('ЗЕЛЁНЫЙ' if ok else 'КРАСНЫЙ/таймаут'))
sys.exit(0 if ok else 1)
