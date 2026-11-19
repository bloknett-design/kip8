#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 558 ПОРТ — ожидание CI kip8 (496541b6): CI Tests + Sync
content to kip8-desktop + pages build and deployment. Токен — из
remote.origin.url git (в лог НЕ печатается). head_sha — ПОЛНЫЙ SHA
(урок Task 555). kip8test НЕ ждём (319bc582 уже зелёный, пуша не
было)."""
import json
import re
import subprocess
import sys
import time
import urllib.request

CWD = '/home/z/my-project/kip8'
REPO = 'kip8'
JOBS = ['CI Tests', 'Sync content to kip8-desktop',
        'pages build and deployment']


def headers_for():
    remote = subprocess.check_output(
        ['git', 'config', '--get', 'remote.origin.url'],
        cwd=CWD, text=True).strip()
    m = re.search(r'x-access-token:([^@]+)@', remote)
    pat = m.group(1) if m else ''
    return {'Authorization': 'Bearer ' + pat,
            'Accept': 'application/vnd.github+json'}


def sha_of():
    return subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=CWD, text=True).strip()


def runs(sha):
    url = ('https://api.github.com/repos/bloknett-design/%s/actions/runs'
           '?head_sha=%s&per_page=30' % (REPO, sha))
    req = urllib.request.Request(url, headers=headers_for())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['workflow_runs']


def wait(sha, name_kw, timeout_s=600):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        for r in runs(sha):
            if name_kw in r['name']:
                if r['status'] != 'completed':
                    time.sleep(15)
                    break
                print('  kip8 [%s]: %s' % (name_kw, r['conclusion']))
                return r['conclusion'] == 'success'
        else:
            time.sleep(15)
    print('  kip8 [%s]: TIMEOUT' % name_kw)
    return False


def main():
    sha = sha_of()
    print('kip8 @ %s' % sha[:10])
    overall = True
    for job in JOBS:
        overall = wait(sha, job) and overall
    print('CI kip8: %s' % ('ЗЕЛЁНЫЙ' if overall else 'КРАСНЫЙ/таймаут'))
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
