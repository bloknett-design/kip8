#!/usr/bin/env node
// Task 495: диагностика окон истории sw.js в kip8 после вставки
// комментария (~287 симв. перед CACHE_VERSION).
const fs = require('fs');
const SW = fs.readFileSync('/home/z/my-project/kip8/sw.js', 'utf8');

const iConst = SW.indexOf("const CACHE_VERSION = 'kipia-v519';");
const iVstr = SW.indexOf('kipia-v519');
console.log('iConst =', iConst, ' iVstr =', iVstr);

function lastAnchors(i, marks) {
    for (const m of marks) {
        const pos = SW.lastIndexOf(m, i);
        console.log('  ' + m + ': дистанция ' + (i - pos));
    }
}

console.log('\n== Маркеры задач (от iConst) ==');
lastAnchors(iConst, [
    'Task 461', 'Task 471', 'Task 472', 'Task 473', 'Task 474',
    'Task 478', 'Task 479', 'Task 480', 'Task 481', 'Task 482',
    'Task 483', 'Task 484', 'Task 485', 'Task 486', 'Task 488',
    'Task 493', 'Task 494', 'Task 495'
]);

console.log('\n== Спец-якоря (от iConst) ==');
lastAnchors(iConst, [
    'Период ремонта', 'ЗЕЛЁНЫЙ', 'КРАСНЫЙ', 'оранжево-золотистый',
    'dev-ppr-warn', '_barExpMaxH', 'рамка зелёная', 'галочка отметки',
    'Работы на месяц', 'Перечень КИП ИОС рабочий', 'бежевое'
]);

console.log('\n== От iVstr (471/472) ==');
lastAnchors(iVstr, ['Task 471', 'Task 472', 'бежевое', 'textarea']);
