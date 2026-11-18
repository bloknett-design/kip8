#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 557 — ожидание CI ОБЕИХ репозиториев (kip8 d8e079f5 +
kip8test 3f42a514): CI Tests + Deploy GitHub Pages + Sync content
to *-desktop. Токен — из remote.origin.url git (в лог НЕ
печатается). head_sha — ПОЛНЫЙ SHA (урок Task 555)."""
import json
import re
import subprocess
import sys
import time
import urllib.request

REPOS = [
    ('kip8', '/home/z/my-project/kip8',
     ['CI Tests', 'Sync content to kip8-desktop', 'pages build and deployment']),
    ('kip8test', '/home/z/my-project/kip8test',
     ['CI Tests', 'Sync content to kip8test-desktop', 'Deploy GitHub Pages']),
]
HDRS_CACHE = {}


def headers_for(cwd):
    if cwd in HDRS_CACHE:
        return HDRS_CACHE[cwd]
    remote = subprocess.check_output(
        ['git', 'config', '--get', 'remote.origin.url'],
        cwd=cwd, text=True).strip()
    m = re.search(r'x-access-token:([^@]+)@', remote)
    pat = m.group(1) if m else ''
    hdrs = {'Authorization': 'Bearer ' + pat,
            'Accept': 'application/vnd.github+json'}
    HDRS_CACHE[cwd] = hdrs
    return hdrs


def sha_of(cwd):
    return subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip()


def runs(repo, sha):
    url = ('https://api.github.com/repos/bloknett-design/%s/actions/runs'
           '?head_sha=%s&per_page=30' % (repo, sha))
    req = urllib.request.Request(url, headers=headers_for(
        {'kip8': '/home/z/my-project/kip8',
         'kip8test': '/home/z/my-project/kip8test'}[repo]))
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['workflow_runs']


def wait(repo, sha, name_kw, timeout_s=420):
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
    overall = True
    for repo, cwd, jobs in REPOS:
        sha = sha_of(cwd)
        print('%s @ %s' % (repo, sha[:8]))
        for job in jobs:
            overall = wait(repo, sha, job) and overall
    print('CI BOTH: %s' % ('ЗЕЛЁНЫЙ' if overall else 'КРАСНЫЙ/таймаут'))
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
