#!/usr/bin/env node
// scripts/task507-vlm-check.js — VLM kip8 (перенос 504+505+506).
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const DIR = '/home/z/my-project/download/kip8-task507';

function vision(file, prompt) {
    const out = execFileSync('z-ai', [
        'vision', '-p', prompt, '-i', path.join(DIR, file)
    ], { encoding: 'utf8', timeout: 120000, stdio: ['ignore', 'pipe', 'pipe'] });
    const m = out.match(/"content":\s*"((?:[^"\\]|\\.)*)"/);
    return m ? JSON.parse('"' + m[1] + '"') : out;
}

const shots = [
    ['a1-events-dates.png',
     'Это раздел «Табель учёта рабочего времени» приложения (тёмная тема): слева сетка графика, справа панель «Мероприятия» со списком строк (дата + текст мероприятия). Ответь строго по пунктам: (1) В панели «Мероприятия» видны строки с датами? (2) Есть ли строки, где ДАТА окрашена в ЗЕЛЁНЫЙ цвет, и строки, где ДАТА окрашена в КРАСНЫЙ цвет? (3) Есть ли визуальные дефекты (наложение текста, обрезка)?'],
    ['b1-preview.png',
     'Это диалог «Предпросмотр печати» раздела «Кабельный журнал» (тёмная тема): белый альбомный лист A4 с таблицей. Ответь строго по пунктам: (1) Таблица начинается сразу с двухуровневой шапки (слева «Обозначение кабеля, провода», «Начало трассы»…; справа пары «По проекту»/«Проложен» с подколонками «Марка»/«Число и сечение жил»/«Длина, м») — БЕЗ крупного заголовка над ней? (2) Колонки группы «По проекту» залиты светло-серым, а «Проложен» — белым? (3) Внизу диалога кнопки «Печать», «Сохранить PDF», «Сохранить Excel», «Отмена»? (4) Есть ли визуальные дефекты (наложение, обрезка, пустой лист)?']
];

function score(txt) {
    const t = String(txt).replace(/\*/g, '');
    let ok = true;
    const qs = t.split(/\(\d\)|(?=^\d\.\s)/m).map(x => x.trim()).filter(x => x);
    if (qs.length >= 2) {
        for (const q of qs) {
            const low = q.toLowerCase();
            const isDefectQ = /дефект/i.test(q);
            const negated = /не наблюд|не содержит|отсутств|нет\b|ничего|не замечен|не обнаруж/i.test(low.slice(0, 60));
            const hasYes = /(^|[^а-яё])да[,. ]/i.test(low) ||
                           /да\b/i.test(low.slice(0, 30));
            if (isDefectQ) {
                if (negated && !/есть .*дефект|обнаружен дефект/i.test(low)) { /* ок */ }
                else if (/^да[,.]?\s*(есть|видны?|обнаруж)/i.test(low.trim())) { ok = false; }
            } else {
                if (!hasYes && /(^|[^а-яё])(нет|не видн|неверно|отсутств)/i.test(low)) { ok = false; }
            }
        }
    } else {
        if (/(есть|видны?|присутству)\D{0,40}дефект/i.test(t)) ok = false;
    }
    return ok;
}

let pass = 0, fail = 0;
for (const [file, prompt] of shots) {
    let txt;
    try {
        txt = vision(file, prompt);
    } catch (e) {
        console.log('X ' + file + ': ' + String(e).slice(0, 200));
        fail++;
        continue;
    }
    const ok = score(txt);
    if (ok) pass++; else fail++;
    console.log((ok ? '+ ' : 'X ') + file);
    console.log('    ' + String(txt).replace(/\s+/g, ' ').slice(0, 400));
}
console.log('\nVLM kip8: %d/%d (fail=%d)', pass, pass + fail, fail);
process.exit(fail ? 1 : 0);
