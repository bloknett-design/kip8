#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 536 — docs-коммит kip8 (по образцу task535-docs-kip8.py):
  1) версионная строка промта: post-Task 536 (зеркало kip8test
     @6cb34a8c) ЗАМЕНЯЕТ post-Task 535;
  2) ARCHITECTURE.md §2 — счётчики: 7028 тестов / 233 тест-файлов,
     зеркало kip8-desktop 7043;
  3) worklog.md — запись Task 536 (финализация kip8).
Коммит делает обёртка (bash). Скрипт — артефакт коммита.
"""
import io

P_PROMT = 'Системный_промт_для_приложения_КИПиА.md'
P_ARCH = 'ARCHITECTURE.md'
P_WLOG = 'worklog.md'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


# ---------- 1. Версионная строка промта ----------
T536 = (
    '> **Версия документа:** 2026-10-16 (post-Task 536 — зеркало '
    'kip8test @6cb34a8c) (ТАБЕЛЬ: СЕРВЕРНАЯ ПОГОДА УДАЛЕНА — '
    'WorkSchedule.gs −290 строк: getWeather/_parseMeteoinfo/'
    '_parseOpenMeteo/authorizeWeather; Code.gs без роутинга; КЛИЕНТ — '
    'двухканальная цепочка open-meteo → wttr.in БЕЗ серверного '
    'резерва, единая ветка сбоя панели без подсказок '
    'authorizeWeather/appsscript.json/oauthScopes; заявка: «через '
    'сервер погода не загружается, работает только через wttr.in '
    '(напрямую из браузера), поэтому убери из кода WorkSchedule.gs не '
    'рабочие строки кода связанные с погодой»); перенос — дифф 96 '
    'строк клиент + WorkSchedule.gs ЦЕЛИКОМ (−290) + Code.gs '
    'ТОЧЕЧНЫМ патчем роутинга; все 4 репо ЗЕЛЁНЫЕ: kip8 7028/0 → '
    'kip8-desktop 7043/0 (+10; 7043 = 7028 + 29 electron − 14 '
    'workflow-гвардов), kip8test 7028/0 → kip8test-desktop 7013/0; '
    'SW v545→v546 (886 замен/206 файлов, гварды v547 первыми); '
    'DEPLOY-Task536 (КЛИЕНТ: Ctrl+Shift+R — само; СЕРВЕР опционален: '
    'чистка мёртвого кода — свежие WorkSchedule.gs + Code.gs + New '
    'version, authorizeWeather больше НЕ запускать); ARCHITECTURE.md '
    '§2 (счётчик 7028/233 + зеркало 7043); worklog.md — запись Task '
    '536 (финализация kip8); scripts/task536-transfer-tests.py + '
    'task536-browser-check-kip8.py + task536-docs-kip8.py (УРОК '
    'переноса: SW-своп обязан сохранять ЧИСЛО тестов хвоста — единый '
    '1-тестовый блок срезал 5, 7023≠7028; паритет восстановлен '
    'блоками 1/2/3/3/1/1; kipia-v546, Task 536))')

promt = read(P_PROMT)
lines = promt.split('\n')
assert 'post-Task 535' in lines[2], 'строка 3 не post-Task 535!'
lines[2] = T536
write(P_PROMT, '\n'.join(lines))
print('промт: строка версии заменена post-Task 535 → post-Task 536 '
      '(зеркало @6cb34a8c)')

# ---------- 2. ARCHITECTURE.md §2 ----------
arch = read(P_ARCH)
old = ('`tests/`, 7018 тестов, 232 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 7033')
new = ('`tests/`, 7028 тестов, 233 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 7043')
assert old in arch, 'не найден счётчик ARCHITECTURE.md'
arch = arch.replace(old, new, 1)
write(P_ARCH, arch)
print('ARCHITECTURE.md: 7018/232/7033 → 7028/233/7043')

# ---------- 3. worklog.md ----------
WLOG = (
    '\n---\n'
    'Task ID: 536 (финализация kip8)\n'
    'Agent: main (Super Z)\n'
    'Task: Заявка Task 536 (зеркало kip8test @bc37e572): «Через '
    'сервер погода не загружается, работает только через wttr.in '
    '(напрямую из браузера), поэтому убери из кода WorkSchedule.gs не '
    'рабочие строки кода связанные с погодой».\n'
    '\n'
    'Work Log:\n'
    '- Перенос scripts/task536-transfer-tests.py: index.html '
    '(prepare-скрипт, дифф = клиент Task 536) + WorkSchedule.gs '
    'ЦЕЛИКОМ (−290 строк, файл был идентичен между репо до задачи) + '
    'Code.gs ТОЧЕЧНЫМ патчем (репо дрейфанули: только роутинг '
    'case workSchedule.getWeather → заметка Task 536).\n'
    '- Тесты: перенос шести файлов 530/532/533/534/535/536.js '
    '(SW-хвосты → kip8-блоки v546/гвард v547) + бамп SW v545→v546 '
    '(гварды v547 первыми, 886 замен/206 файлов) + регистрация — '
    '7028/0 (ПАРИТЕТ kip8test). УРОК ПЕРЕНОСА: SW-своп обязан '
    'сохранять ЧИСЛО тестов хвоста — единый 1-тестовый k8-блок срезал '
    '5 тестов (7023≠7028); паритет восстановлен блочным паритетом '
    '1/2/3/3/1/1 (хвосты 530/532/533/534/535/536 kip8test).\n'
    '- Верификация зеркальная: браузер task536-browser-check-kip8.py '
    '25/25 (порт 8997, обе темы: OM 503 → wttr.in «-2°» облака, '
    'сервер Apps Script НЕ звался; оба пали → «--» + why:network + '
    'dnote 503/502; календарь 30px жив; 1024 светлая; 0 JS-ошибок).\n'
    '- Пуши и зеркала: kip8 638d90bf (feat) → CI Tests + Pages + '
    'Build + синк → kip8-desktop bot 5dade92130 → CI 7043/0 '
    '(=7028+29 electron −14 workflow-гвардов) + Build success.\n'
    '- Docs: DEPLOY-Task536-server-weather-removed.md (копия kip8test '
    'с kip8-счётчиками), промт post-Task 536 (зеркало @6cb34a8c), '
    'ARCHITECTURE.md §2 (7028/233 + зеркало 7043), эта запись; '
    'scripts/task536-transfer-tests.py + task536-browser-check-kip8.py '
    '+ task536-docs-kip8.py.\n'
    '\n'
    'Stage Summary:\n'
    '- Task 536 в kip8 ЗАКРЫТ: репо ЗЕЛЁНОЕ (7028/0, ПАРИТЕТ '
    'kip8test), Pages/Build success, десктоп-зеркало синкнуто '
    '(5dade92130, 7043/0 + Build). Из заявки выполнено ВСЁ (зеркало '
    'kip8test): нерабочая серверная погода удалена из WorkSchedule.gs '
    '(−290 строк) и Code.gs (роутинг); клиент — только прямые каналы '
    'open-meteo → wttr.in. SW: kipia-v546. Хвостов НЕТ. '
    'СЛЕДУЮЩАЯ ЗАДАЧА: задачи пользователя.\n')

wlog = read(P_WLOG)
wlog += WLOG
write(P_WLOG, wlog)
print('worklog.md: запись Task 536 добавлена')
print('OK — docs готовы к коммиту')
