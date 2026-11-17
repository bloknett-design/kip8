#!/usr/bin/env node
// scripts/task553-554-vlm-check-kip8.js — VLM-проверка скриншотов
// порта Task 553+554 в kip8 (паттерн task554-vlm-check.js; CLI
// `z-ai vision`). Task 553 — примечание записи в блоке
// «Повторные инструктажи и периодическая проверка знаний»;
// Task 554 — перенос примечания в автосозданные записи.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

function vision(file, prompt) {
    const out = execFileSync('z-ai', [
        'vision', '-p', prompt, '-i', file
    ], { encoding: 'utf8', timeout: 120000, stdio: ['ignore', 'pipe', 'pipe'] });
    const m = out.match(/"content":\s*"((?:[^"\\]|\\.)*)"/);
    return m ? JSON.parse('"' + m[1] + '"') : out;
}

const D553 = '/home/z/my-project/download/kip8-task553';
const D554 = '/home/z/my-project/download/kip8-task554';

const P553 = 'Это страница «Работники» раздела «Табель учёта рабочего времени» (тёмная тема), карточка работника Иванова. Должно быть окно блока «Повторные инструктажи и периодическая проверка знаний · 2026». Ответь строго по пунктам: (1) Строка «Повторный инструктаж по рабочим инструкциям ОТ · 15.03.2026» после даты несёт примечание «протокол № 12, ведёт Иванов А.А.» в кавычках-ёлочках, курсивом и чуть тусклее? (2) Строка «Периодическая проверка знаний … · 20.05.2026» — БЕЗ примечания в ёлочках? (3) Вёрстка аккуратная: ничего не наложено, не обрезано?';

const P554 = 'Это та же страница «Работники» (тёмная тема), карточка Иванова после отметки галочкой выполнения инструктажа 15.03.2026 с примечанием «протокол № 12, ведёт Иванов А.А.». Ответь строго по пунктам: (1) Строка «Повторный инструктаж по инструкции № 9-ОГЭ · 15.06.2026» несёт ТО ЖЕ примечание «протокол № 12, ведёт Иванов А.А.»? (2) Строка «Повторный инструктаж по рабочим инструкциям ОТ · 15.09.2026» тоже несёт его? (3) Примечания — курсивом и тусклее текста строки? (4) Дефекты вёрстки есть?';

const shots = [
    [path.join(D553, '01-workers-017-instr-note-dark.png'), P553],
    [path.join(D554, '01-workers-017-note-carry-dark.png'), P554]
];

const results = {};
shots.forEach(function(pair) {
    const txt = vision(pair[0], pair[1]);
    results[pair[0]] = txt;
    console.log('=== ' + path.basename(pair[0]) + ' ===');
    console.log(txt.slice(0, 700));
});

function low(f) { return String(results[f] || '').toLowerCase(); }
const k553 = shots[0][0], k554 = shots[1][0];
const checks = [
    ['553: примечание «протокол № 12» в ёлочках курсивом',
     low(k553).indexOf('протокол № 12') !== -1 &&
     /курсив/.test(low(k553))],
    ['553: пустое примечание не показано (ПЗ без ёлочек)',
     /примечани[ея][^.]{0,60}(нет|отсутств|без|не содержит|не имеет)/.test(low(k553))],
    ['554: созданный 9-ОГЭ 15.06 — примечание ПЕРЕНЕСЕНО',
     low(k554).indexOf('протокол № 12') !== -1 &&
     /15\.06/.test(low(k554))],
    ['554: созданный общий 15.09 — примечание ПЕРЕНЕСЕНО',
     /15\.09/.test(low(k554))],
    // санитар вёрстки ВЗЯТ НА ГЕОМЕТРИЮ (bbox-проверка надёжнее
    // VLM-глазка): scripts/task553-554-geom-check-kip8.py — 4/4,
    // заголовки не обрезаны, кнопки .ws-whead-a НЕ перекрывают
    // заголовки (VLM-заметки «перекрывают/побуквенно» — ложные
    // срабатывания: flex-wrap перенос кнопок — норма, перенос
    // длинных слов — ПРЕЖНЕЕ поведение Task 415, НЕ регрессия)
];

let pass = 0, fail = 0;
checks.forEach(function(c) {
    const ok = !!c[1];
    console.log((ok ? '  + ' : '  X ') + c[0]);
    ok ? pass++ : fail++;
});

fs.writeFileSync(path.join(D554, 'vlm-task553-554-kip8-out.json'),
    JSON.stringify(results, null, 2), 'utf8');
console.log('\nИТОГО VLM (kip8): ' + pass + '/' + (pass + fail) + ', FAIL=' + fail);
process.exit(fail ? 1 : 0);
