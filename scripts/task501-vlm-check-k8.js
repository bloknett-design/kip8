#!/usr/bin/env node
// scripts/task501-vlm-check-k8.js — VLM-проверка SMOKE-скриншотов
// переноса Task 500+501 в БОЕВОЙ kip8.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const DIR = '/home/z/my-project/download/kip8-task501-smoke';

function vision(file, prompt) {
    const out = execFileSync('z-ai', [
        'vision', '-p', prompt, '-i', path.join(DIR, file)
    ], { encoding: 'utf8', timeout: 120000, stdio: ['ignore', 'pipe', 'pipe'] });
    const m = out.match(/"content":\s*"((?:[^"\\]|\\.)*)"/);
    return m ? JSON.parse('"' + m[1] + '"') : out;
}

const shots = [
    ['t501-smoke-cb-dark.png',
     'Это скриншот мобильного веб-приложения (тёмная тема, 375px), страница «Автоматический выключатель» (электротехника), колонка ввода. Ответь строго по пунктам: (1) Группы полей (Тип питания, Тип нагрузки и далее) — ВНУТРИ ОДНОЙ общей рамки-панели с «утопленным» фоном? (2) Поля и селекты крупные, жирные, белым текстом? (3) Между группами тонкие линии-разделители? (4) Есть ли визуальные дефекты?'],
    ['t501-smoke-scale-signal-dark.png',
     'Это скриншот мобильного веб-приложения (тёмная тема, 375px), страница «Шкала-сигнал», колонка ввода. Ответь строго по пунктам: (1) Вверху — панель «расчёта произвольных значений» с полями «Значение шкалы» и «Сигнал» с рамкой-выступом? (2) Ниже — панель расчёта шкалы (Тип шкалы, Диапазон, Тип сигнала) с «утопленным» фоном? (3) Под селектом «Тип шкалы» нет мелкой серой строки-подсказки? (4) Есть ли визуальные дефекты?'],
    ['t501-smoke-ts-view-light.png',
     'Это скриншот страницы расчёта датчика температуры 50М (Cu50) в СВЕТЛОЙ теме мобильного приложения. Ответь строго по пунктам: (1) Рамки панелей и акцентные цвета — ТЁПЛЫЕ терракотовые (в тон кнопке «Рассчитать»), НЕ синие? (2) Тени панелей без синевы? (3) Поля с тёмным читаемым текстом? (4) Есть ли визуальные дефекты?'],
    ['t501-smoke-cb-desktop.png',
     'Это скриншот ДЕСКТОПНОЙ версии (1280px, светлая тема), страница «Автоматический выключатель». Ответь строго по пунктам: (1) Три колонки: слева форма, в центре результаты, справа справка? (2) В левой колонке ОДНА общая панель со всеми полями и линиями-разделителями? (3) Поля крупные? (4) Есть ли визуальные дефекты?']
];

const CACHE = path.join(DIR, 'vlm-task501-k8-out.json');
let cache = {};
if (fs.existsSync(CACHE)) cache = JSON.parse(fs.readFileSync(CACHE, 'utf8'));

function score(txt, file) {
    const t = String(txt);
    let ok = true;
    const qs = t.split(/\(\d\)|(?=^\d\.\s)/m).map(x => x.trim()).filter(x => x);
    if (qs.length >= 3) {
        for (const q of qs) {
            const low = q.toLowerCase();
            const lowClean = low.replace(/\*/g, '');
            const isDefectQ = /дефект/i.test(q);
            const negated = /не наблюд|не содержит|отсутств|нет\b|ничего|не замечен|не обнаруж/i.test(low.slice(0, 60));
            const hasYes = /(^|[^а-яё])да[,. ]/i.test(lowClean) ||
                           /да\b/i.test(lowClean.slice(0, 30));
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
    if (!fs.existsSync(path.join(DIR, file))) {
        console.log('нет файла ' + file); fail++; continue;
    }
    let txt = cache[file];
    if (!txt) {
        txt = vision(file, prompt);
        cache[file] = txt;
        fs.writeFileSync(CACHE, JSON.stringify(cache, null, 1));
    }
    const ok = score(txt, file);
    if (ok) { pass++; console.log('+ ' + file); }
    else { fail++; console.log('X ' + file); }
    console.log('    ' + String(txt).replace(/\s+/g, ' ').slice(0, 220));
}
console.log('ИТОГ VLM kip8 Task 500+501: ' + pass + ' OK, ' + fail + ' FAIL');
if (fail) process.exit(1);
