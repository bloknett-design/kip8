// scripts/task496-windows-diag.js — kip8: какие окна упали и на сколько
const fs = require('fs');
const path = require('path');
const T = path.join(__dirname, '..', 'tests');
const SW = fs.readFileSync(path.join(__dirname, '..', 'sw.js'), 'utf8');

const i = SW.indexOf("const CACHE_VERSION = 'kipia-v520';");
console.log('iConst = ' + i);

const DIST = {};
for (const m of ['Task 461', 'Task 471', 'Task 472', 'Task 473', 'Task 474',
                 'Task 478', 'Task 479', 'Task 480', 'Task 481', 'Task 482',
                 'Task 483', 'Task 484', 'Task 485', 'Task 486']) {
    DIST[m] = i - SW.lastIndexOf(m, i);
    console.log(m + ' @' + DIST[m]);
}

const files = ['test-task461.js', 'test-task472.js', 'test-task473.js',
               'test-task474.js', 'test-task476.js', 'test-task477.js',
               'test-task478.js', 'test-task479.js', 'test-task480.js',
               'test-task481.js', 'test-task482.js', 'test-task483.js',
               'test-task484.js', 'test-task485.js', 'test-task486.js'];

for (const f of files) {
    const src = fs.readFileSync(path.join(T, f), 'utf8');
    console.log('\n=== ' + f + ' ===');
    // slice-окна: i - N
    const slices = [...src.matchAll(/(?:SW_SRC\.)?slice\(Math\.max\(0,\s*i\s*-\s*(\d+)\)/g)];
    const seen = new Set();
    for (const m of slices) {
        const w = +m[1];
        if (seen.has(w)) continue;
        seen.add(w);
        // ближайший якорь, который должен попадать (грубая оценка: якорь задачи)
        console.log('  slice i - ' + w);
    }
    // LIMITS-окна: (i - iXXX) < N
    for (const m of src.matchAll(/\(i\s*-\s*i(\d+)\)\s*<\s*(\d+)/g)) {
        console.log('  limit (i - i' + m[1] + ') < ' + m[2]);
    }
    // lastIndexOf-окна: SW_SRC.lastIndexOf('Task NNN', i) — дистанция уже есть
}
