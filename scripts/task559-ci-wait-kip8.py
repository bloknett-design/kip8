#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 559 ПОРТ — ожидание CI kip8 (d0ff62c5): CI Tests + Sync
content to kip8-desktop + pages build and deployment, ЗАТЕМ зеркало
kip8-desktop (CI Tests + Build Desktop App на свежем HEAD main после
синка). Токен — из remote.origin.url git (в лог НЕ печатается).
head_sha — ПОЛНЫЙ SHA (урок Task 555). kip8test НЕ ждём (103ca85
уже зелёный, пуша не было)."""
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


def api(url):
    req = urllib.request.Request(url, headers=headers_for())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def runs(repo, sha):
    return api('https://api.github.com/repos/bloknett-design/%s/'
               'actions/runs?head_sha=%s&per_page=30'
               % (repo, sha))['workflow_runs']


def wait(repo, sha, name_kw, timeout_s=900):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        for r in runs(repo, sha):
            if name_kw in r['name']:
                if r['status'] != 'completed':
                    time.sleep(15)
                    break
                print('  %s [%s]: %s' % (repo, name_kw, r['conclusion']))
                return r['conclusion'] == 'success'
        else:
            time.sleep(15)
    print('  %s [%s]: TIMEOUT' % (repo, name_kw))
    return False


def main():
    sha = sha_of()
    print('kip8 @ %s' % sha[:10])
    overall = True
    for job in JOBS:
        overall = wait('kip8', sha, job) and overall

    print('зеркало kip8-desktop: ждём синк (HEAD main меняется)...')
    t0 = time.time()
    mirror_sha = None
    while time.time() - t0 < 600:
        c = api('https://api.github.com/repos/bloknett-design/'
                'kip8-desktop/commits/main')
        if c['sha'] != sha and c['sha']:
            mirror_sha = c['sha']
            break
        time.sleep(15)
    if not mirror_sha:
        print('  kip8-desktop: синк не обнаружен (TIMEOUT)')
        sys.exit(1)
    print('  kip8-desktop @ %s (после синка)' % mirror_sha[:10])
    time.sleep(20)
    overall = wait('kip8-desktop', mirror_sha, 'CI Tests') and overall
    overall = wait('kip8-desktop', mirror_sha,
                   'Build Desktop App') and overall
    print('CI: %s' % ('ЗЕЛЁНЫЙ' if overall else 'КРАСНЫЙ/таймаут'))
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
