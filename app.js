// ИСТОРИЯ И НАВИГАЦИЯ

// ===== SAFE LOCALSTORAGE WRAPPER =====
// Handles private mode Safari, quota exceeded, and other errors
const SafeStorage = {
    _memory: {},
    _available: null,

    isAvailable() {
        if (this._available !== null) return this._available;
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            this._available = true;
            return true;
        } catch (e) {
            this._available = false;
            console.warn('[Storage] localStorage not available, using memory fallback');
            return false;
        }
    },

    setItem(key, value) {
        try {
            if (this.isAvailable()) {
                localStorage.setItem(key, value);
                return true;
            }
        } catch (e) {
            if (e.name === 'QuotaExceededError') {
                console.warn('[Storage] Quota exceeded, using memory fallback');
            } else {
                console.warn('[Storage] Error writing to localStorage:', e.message);
            }
        }
        this._memory[key] = value;
        return true;
    },

    getItem(key) {
        try {
            if (this.isAvailable()) {
                return localStorage.getItem(key);
            }
        } catch (e) {
            console.warn('[Storage] Error reading from localStorage:', e.message);
        }
        return this._memory[key] || null;
    },

    removeItem(key) {
        try {
            if (this.isAvailable()) {
                localStorage.removeItem(key);
                return true;
            }
        } catch (e) {
            console.warn('[Storage] Error removing from localStorage:', e.message);
        }
        delete this._memory[key];
        return true;
    },

    clear() {
        try {
            if (this.isAvailable()) {
                localStorage.clear();
            }
        } catch (e) {
            console.warn('[Storage] Error clearing localStorage:', e.message);
        }
        this._memory = {};

// ===== INPUT VALIDATION HELPERS =====
const Validate = {
    // Check if value is a valid positive number
    isPositiveNumber(value, name = 'value') {
        const num = parseFloat(value);
        if (isNaN(num)) return { valid: false, error: `${name}: введите число` };

// ===== UNIVERSAL ERROR CALCULATION (replaces 4 duplicate functions) =====
function showTempTable(fromUnit, toUnit, fromValue, toValue) {
    let tableDiv = document.getElementById('conv-temp-table');
    if (!tableDiv) return;

    let tU={'C':{label:'°C',fn:z=>z},'F':{label:'°F',fn:z=>z*9/5+32},'K':{label:'K',fn:z=>z+273.15},'R':{label:'°R',fn:z=>z*0.8},'Ra':{label:'°Ra',fn:z=>(z+273.15)*9/5}};
    let fromLabel = tU[fromUnit].label;
    let toLabel = tU[toUnit].label;

    let html = '<div class="converter-result-label-title" style="margin-top:16px;">Таблица пересчёта: ' + fromLabel + ' → ' + toLabel + '</div>';
    html += '<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);margin-top:8px;">';
    html += '<table style="min-width:100%;width:100%;border-collapse:collapse;">';
    html += '<thead><tr style="background:rgba(22,27,34,0.7);">';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">' + fromLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4ac771;text-align:left;">' + toLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">%</th>';
    html += '</tr></thead><tbody>';

    for (let pct = 0; pct <= 100; pct += 5) {
        let fromVal = fromValue * (pct / 100);
        let c = fromUnit === 'C' ? fromVal : fromUnit === 'F' ? (fromVal - 32) * 5 / 9 : fromUnit === 'K' ? fromVal - 273.15 : fromUnit === 'R' ? fromVal * 1.25 : (fromVal - 491.67) * 5 / 9;
        let toVal = tU[toUnit].fn(c);
        let bg = (pct / 5) % 2 ? 'rgba(22,27,34,0.4)' : 'rgba(13,17,23,0.4)';
        html += '<tr style="background:' + bg + ';">';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4ac771;">' + formatNumber(fromVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4a8fc7;">' + formatNumber(toVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:rgba(255,255,255,0.4);">' + pct + '%</td>';
        html += '</tr>';
    }

    html += '</tbody></table></div>';
    html += '<div style="margin-top:8px;padding:8px 12px;background:rgba(13,17,23,0.4);border-radius:8px;font-size:11px;color:rgba(255,255,255,0.35);">';
    html += 'Базовое значение: <b style="color:#4a8fc7;">' + formatNumber(fromValue) + ' ' + fromLabel + '</b> = <b style="color:#4ac771;">' + formatNumber(toValue) + ' ' + toLabel + '</b></div>';

    tableDiv.innerHTML = html;
    tableDiv.style.display = 'block';
    setTimeout(() => tableDiv.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

function calcErrorUniversal(config) {
    // config: { minId, maxId, classId, currentId?, resultId, title, unit?, gost? }
    let min = parseFloat(document.getElementById(config.minId).value);
    let max = parseFloat(document.getElementById(config.maxId).value);
    let cls = parseFloat(document.getElementById(config.classId).value);
    let cur = config.currentId ? parseFloat(document.getElementById(config.currentId).value) : NaN;

    const validation = Validate.validateFields({
        min: Validate.isNumber(min, 'НПИ'),
        max: Validate.isNumber(max, 'ВПИ'),
        cls: Validate.isPositiveNumber(cls, 'Класс точности')
    });
    if (!validation.valid) return;

    if (min >= max) { showToast('НПИ должен быть меньше ВПИ'); return; }

    let xNorm = (min === 0 || min * max < 0) ? (Math.abs(max) + Math.abs(min)) : Math.abs(max);
    let absErr = (cls / 100) * xNorm;
    let formulaText = 'Δ = (<span class="greek-gamma">&gamma;</span>/100)·Xₙ = (' + cls + '/100)·' + formatNumber(xNorm) + ' = ±' + formatNumber(absErr) + ' ед.';

    let gostRef = config.gost || 'ГОСТ 8.401-80';
    let unitLabel = config.unit || 'ед.';

    let html = '<div class="converter-result-label-title">Результаты расчёта (' + gostRef + ')</div>';
    html += '<div class="converter-result-item"><span class="converter-result-label">Класс точности (<span class="greek-gamma">&gamma;</span>)</span><span class="converter-result-value">' + cls + ' %</span></div>';
    html += '<div class="converter-result-item"><span class="converter-result-label">Нормирующее значение (Xₙ)</span><span class="converter-result-value">' + formatNumber(xNorm) + ' ' + unitLabel + '</span></div>';
    html += '<div class="converter-result-item"><span class="converter-result-label">Абсолютная погрешность (±Δ)</span><span class="converter-result-value">± ' + formatNumber(absErr) + ' ' + unitLabel + '</span></div>';
    html += '<div class="converter-result-item"><span class="converter-result-label">Формула расчёта</span><span class="converter-result-value">' + formulaText + '</span></div>';

    if (!isNaN(cur) && cur !== 0) {
        let rel = (absErr / Math.abs(cur)) * 100;
        html += '<div class="converter-result-item"><span class="converter-result-label">Относительная погрешность (δ)</span><span class="converter-result-value">± ' + formatNumber(rel) + ' %</span></div>';
    }

    html += '<div class="converter-result-item"><span class="converter-result-label">Диапазон измерения</span><span class="converter-result-value">' + formatNumber(min) + ' … ' + formatNumber(max) + '</span></div>';

    document.getElementById(config.resultId).innerHTML = html;
    document.getElementById(config.resultId).style.display = 'block';
    setTimeout(() => document.getElementById(config.resultId).scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// Wrapper functions for backward compatibility (call universal)
function calcErrorPressure() {
    calcErrorUniversal({
        minId: 'pressure_range_min',
        maxId: 'pressure_range_max',
        classId: 'pressure_accuracy_class',
        currentId: 'pressure_current_value',
        resultId: 'errorPressureResults',
        title: 'Датчик давления',
        unit: 'ед.',
        gost: 'ГОСТ 8.401-80'
    });
}

function calcErrorFlow() {
    calcErrorUniversal({
        minId: 'flow_range_min',
        maxId: 'flow_range_max',
        classId: 'flow_accuracy_class',
        currentId: 'flow_current_value',
        resultId: 'errorFlowResults',
        title: 'Расходомер',
        unit: 'ед.',
        gost: 'ГОСТ 8.401-80'
    });
}

function calcErrorLevel() {
    calcErrorUniversal({
        minId: 'level_range_min',
        maxId: 'level_range_max',
        classId: 'level_accuracy_class',
        currentId: 'level_current_value',
        resultId: 'errorLevelResults',
        title: 'Уровнемер',
        unit: 'ед.',
        gost: 'ГОСТ 8.401-80'
    });
}

function calcErrorGeneric() {
    calcErrorUniversal({
        minId: 'generic_range_min',
        maxId: 'generic_range_max',
        classId: 'generic_accuracy_class',
        currentId: 'generic_current_value',
        resultId: 'errorGenericResults',
        title: 'Аналоговый преобразователь',
        unit: 'ед.',
        gost: 'ГОСТ 8.401-80'
    });
}

        if (num <= 0) return { valid: false, error: `${name}: должно быть > 0` };
        return { valid: true, value: num };
    },

    // Check if value is a valid number (can be zero or negative)
    isNumber(value, name = 'value') {
        const num = parseFloat(value);
        if (isNaN(num)) return { valid: false, error: `${name}: введите число` };
        return { valid: true, value: num };
    },

    // Check range: min < max
    isValidRange(min, max, name = 'диапазон') {
        if (min >= max) return { valid: false, error: `${name}: минимум должен быть меньше максимума` };
        return { valid: true };
    },

    // Check if value is within [0, 100] (for percentages)
    isPercentage(value, name = 'значение') {
        const num = parseFloat(value);
        if (isNaN(num)) return { valid: false, error: `${name}: введите число` };
        if (num < 0 || num > 100) return { valid: false, error: `${name}: должно быть 0-100%` };
        return { valid: true, value: num };
    },

    // Validate multiple fields at once
    validateFields(fields) {
        const errors = [];
        const results = {};
        for (const [key, check] of Object.entries(fields)) {
            if (!check.valid) {
                errors.push(check.error);
            } else {
                results[key] = check.value;
            }
        }
        if (errors.length > 0) {
            showToast(errors[0]);
            return { valid: false, errors };
        }
        return { valid: true, values: results };
    }
};

        return true;
    }
};

    let pageHistory = [];
    function navigateTo(page, addToHistory=true) {
        if (page === 'library') { navigateTo('library-internal'); return; }
        let active = document.querySelector('.page-content.active');
        if (active && addToHistory) { let id = active.id.replace('page-', ''); if (id !== page) pageHistory.push(id); }
        document.querySelectorAll('.page-content').forEach(el => { el.classList.remove('active', 'visible'); });
        let target = document.getElementById('page-' + page);
        if (target) { target.classList.add('active'); requestAnimationFrame(() => { requestAnimationFrame(() => target.classList.add('visible')); }); }
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (page === 'buoy-calc') { updateBuoyCalcTitle(); setCalibMethodOnForm(); }
        updateBottomNavActive(page);
        // Toggle global app-header visibility
        let appHeader = document.querySelector('.app-header');
        if (appHeader) appHeader.style.display = (page === 'dashboard') ? 'block' : 'none';
    }
    function updateBottomNavActive(page) {
        let map = {'converter':0,'scale-signal':1,'error-select':2,'buoy-select':3,'library':4};
        let idx = map[page];
        document.querySelectorAll('.bottom-nav-item').forEach((el, i) => { el.classList.toggle('active', i === idx); });
    }
    function goBack() { if (pageHistory.length) { let prev = pageHistory.pop(); navigateTo(prev, false); } else { navigateTo('dashboard', false); } }
    function toggleSidebar() {
    let sidebar = document.getElementById('sidebar');
    let overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Close sidebar when clicking outside
document.addEventListener('click', function(e) {
    let sidebar = document.getElementById('sidebar');
    let overlay = document.getElementById('sidebarOverlay');
    let menuBtn = document.getElementById('menuBtn');
    if (!sidebar || !overlay) return;
    if (sidebar.classList.contains('active')) {
        let clickedSidebar = sidebar.contains(e.target);
        let clickedMenuBtn = menuBtn && menuBtn.contains(e.target);
        if (!clickedSidebar && !clickedMenuBtn) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }
});

function showToast(msg) { let t = document.getElementById('toast'); document.getElementById('toastMessage').textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 2500); }

    // ======================== КОНВЕРТЕРЫ (полные данные) ========================
    const unitData = {
        pressure: { units: { 'Pa':{label:'Па',factor:1}, 'kPa':{label:'кПа',factor:1000}, 'MPa':{label:'МПа',factor:1000000}, 'bar':{label:'бар',factor:100000}, 'mbar':{label:'мбар',factor:100}, 'atm':{label:'атм',factor:101325}, 'kgf_cm2':{label:'кгс/см²',factor:98066.5}, 'mmHg':{label:'мм рт. ст.',factor:133.322}, 'PSI':{label:'PSI',factor:6894.757}, 'mmH2O':{label:'мм вод. ст.',factor:9.80665} } },
        flow: { units: { 'm3h':{label:'м³/ч',factor:1}, 'm3s':{label:'м³/с',factor:3600}, 'l_min':{label:'л/мин',factor:0.06}, 'l_s':{label:'л/с',factor:3.6}, 't_h':{label:'т/ч',factor:1}, 'kg_s':{label:'кг/с',factor:3.6}, 'kg_h':{label:'кг/ч',factor:0.001} } },
        mass: { units: { 'kg':{label:'кг',factor:1}, 'g':{label:'г',factor:0.001}, 'mg':{label:'мг',factor:0.000001}, 't':{label:'т',factor:1000}, 'lb':{label:'фунт',factor:0.453592}, 'oz':{label:'унция',factor:0.0283495},  } },
        length: { units: { 'm':{label:'м',factor:1}, 'km':{label:'км',factor:1000}, 'cm':{label:'см',factor:0.01}, 'mm':{label:'мм',factor:0.001}, 'um':{label:'мкм',factor:0.000001}, 'mi':{label:'миля',factor:1609.344}, 'ft':{label:'фут',factor:0.3048}, 'in':{label:'дюйм',factor:0.0254}, 'yd':{label:'ярд',factor:0.9144} } },
        density: { units: { 'kg_m3':{label:'кг/м³',factor:1}, 'g_cm3':{label:'г/см³',factor:1000}, 'g_l':{label:'г/л',factor:1}, 'kg_l':{label:'кг/л',factor:1000},  } },
        time: { units: { 's':{label:'секунда',factor:1}, 'ms':{label:'мс',factor:0.001}, 'min':{label:'минута',factor:60}, 'h':{label:'час',factor:3600}, 'd':{label:'сутки',factor:86400}, 'week':{label:'неделя',factor:604800}, 'month':{label:'месяц',factor:2592000}, 'year':{label:'год',factor:31536000} } },
        volume: { units: { 'm3':{label:'м³',factor:1}, 'l':{label:'литр',factor:0.001}, 'ml':{label:'мл',factor:0.000001}, 'cm3':{label:'см³',factor:0.000001}, 'gal':{label:'галлон US',factor:0.00378541}, 'bbl':{label:'баррель',factor:0.158987}, 'ft3':{label:'куб. фут',factor:0.0283168}, 'dm3':{label:'дм³',factor:0.001} } }
    };
    function formatNumber(n) { if (n===0) return '0'; if (Math.abs(n)>=1e9||Math.abs(n)<0.00001&&n!==0) return n.toExponential(4); let d=Math.abs(n)>=100?2:Math.abs(n)>=1?4:6; return parseFloat(n.toFixed(d)).toString(); }
function roundNumber(n) {
    if (n === 0) return '0';
    let absN = Math.abs(n);
    // Determine the order of magnitude
    let order = Math.floor(Math.log10(absN));
    // Scale the number so the most significant digit is in the ones place
    let scaled = absN / Math.pow(10, order);
    // Round to nearest 0.5 (JavaScript Math.round rounds half up)
    let roundedScaled = Math.round(scaled * 2) / 2;
    // Scale back
    let result = roundedScaled * Math.pow(10, order);
    // Preserve sign
    if (n < 0) result = -result;
    // Check if rounded_scaled is effectively an integer
    let isScaledInteger = Math.abs(roundedScaled - Math.round(roundedScaled)) < 1e-10;
    if (isScaledInteger) {
        if (order >= 0) {
            return Math.round(result).toString();
        } else {
            // For numbers < 1, format with appropriate decimal places
            let decimalPlaces = Math.max(1, -order);
            let s = result.toFixed(decimalPlaces);
            // Remove trailing zeros
            s = s.replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
            return s || '0';
        }
    } else {
        // Half-integer in scaled domain
        if (order >= 0) {
            // Result is an integer (e.g., 7.5 * 1000 = 7500)
            if (Math.abs(result - Math.round(result)) < 1e-10) {
                return Math.round(result).toString();
            } else {
                // e.g. 2.5 with order=0 -> show as 2.5
                let s = result.toString();
                s = s.replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
                return s || '0';
            }
        } else {
            // For half-integers with order < 0, need extra decimal place
            let decimalPlaces = Math.max(1, -order + 1);
            let s = result.toFixed(decimalPlaces);
            s = s.replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
            return s || '0';
        }
    }
}

// ===== PRESSURE TABLE (5% step) =====
function showPressureTable(fromUnit, toUnit, fromValue, toValue) {
    let tableDiv = document.getElementById('conv-pressure-table');
    if (!tableDiv) return;

    let fromLabel = unitData.pressure.units[fromUnit].label;
    let toLabel = unitData.pressure.units[toUnit].label;
    let factor = unitData.pressure.units[toUnit].factor / unitData.pressure.units[fromUnit].factor;

    let html = '<div class="converter-result-label-title" style="margin-top:16px;">Таблица пересчёта: ' + fromLabel + ' → ' + toLabel + '</div>';
    html += '<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);margin-top:8px;">';
    html += '<table style="min-width:100%;width:100%;border-collapse:collapse;">';
    html += '<thead><tr style="background:rgba(22,27,34,0.7);">';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">' + fromLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4ac771;text-align:left;">' + toLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">%</th>';
    html += '</tr></thead><tbody>';

    for (let pct = 0; pct <= 100; pct += 5) {
        let fromVal = fromValue * (pct / 100);
        let toVal = toValue * (pct / 100);
        let bg = (pct / 5) % 2 ? 'rgba(22,27,34,0.4)' : 'rgba(13,17,23,0.4)';
        html += '<tr style="background:' + bg + ';">';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4ac771;">' + formatNumber(fromVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4a8fc7;">' + formatNumber(toVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:rgba(255,255,255,0.4);">' + pct + '%</td>';
        html += '</tr>';
    }

    html += '</tbody></table></div>';
    html += '<div style="margin-top:8px;padding:8px 12px;background:rgba(13,17,23,0.4);border-radius:8px;font-size:11px;color:rgba(255,255,255,0.35);">';
    html += 'Базовое значение: <b style="color:#4a8fc7;">' + formatNumber(fromValue) + ' ' + fromLabel + '</b> = <b style="color:#4ac771;">' + formatNumber(toValue) + ' ' + toLabel + '</b></div>';

    tableDiv.innerHTML = html;
    tableDiv.style.display = 'block';
    setTimeout(() => tableDiv.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

    
// ===== GENERIC TABLE FUNCTIONS (5% step) =====
function showGenericTable(cat, fromUnit, toUnit, fromValue, toValue) {
    let tableDiv = document.getElementById('conv-' + cat + '-table');
    if (!tableDiv) return;

    let fromLabel = unitData[cat].units[fromUnit].label;
    let toLabel = unitData[cat].units[toUnit].label;
    let factor = unitData[cat].units[toUnit].factor / unitData[cat].units[fromUnit].factor;

    let html = '<div class="converter-result-label-title" style="margin-top:16px;">Таблица пересчёта: ' + fromLabel + ' → ' + toLabel + '</div>';
    html += '<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);margin-top:8px;">';
    html += '<table style="min-width:100%;width:100%;border-collapse:collapse;">';
    html += '<thead><tr style="background:rgba(22,27,34,0.7);">';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">' + fromLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4ac771;text-align:left;">' + toLabel + '</th>';
    html += '<th style="padding:10px 12px;font-size:14px;color:#4a8fc7;text-align:left;">%</th>';
    html += '</tr></thead><tbody>';

    for (let pct = 0; pct <= 100; pct += 5) {
        let fromVal = fromValue * (pct / 100);
        let toVal = toValue * (pct / 100);
        let bg = (pct / 5) % 2 ? 'rgba(22,27,34,0.4)' : 'rgba(13,17,23,0.4)';
        html += '<tr style="background:' + bg + ';">';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4ac771;">' + formatNumber(fromVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:#4a8fc7;">' + formatNumber(toVal) + '</td>';
        html += '<td style="padding:8px 12px;font-size:16px;color:rgba(255,255,255,0.4);">' + pct + '%</td>';
        html += '</tr>';
    }

    html += '</tbody></table></div>';
    html += '<div style="margin-top:8px;padding:8px 12px;background:rgba(13,17,23,0.4);border-radius:8px;font-size:11px;color:rgba(255,255,255,0.35);">';
    html += 'Базовое значение: <b style="color:#4a8fc7;">' + formatNumber(fromValue) + ' ' + fromLabel + '</b> = <b style="color:#4ac771;">' + formatNumber(toValue) + ' ' + toLabel + '</b></div>';

    tableDiv.innerHTML = html;
    tableDiv.style.display = 'block';
    setTimeout(() => tableDiv.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

function showFlowTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('flow', fromUnit, toUnit, fromValue, toValue); }
function showMassTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('mass', fromUnit, toUnit, fromValue, toValue); }
function showLengthTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('length', fromUnit, toUnit, fromValue, toValue); }
function showDensityTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('density', fromUnit, toUnit, fromValue, toValue); }
function showTimeTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('time', fromUnit, toUnit, fromValue, toValue); }
function showVolumeTable(fromUnit, toUnit, fromValue, toValue) { showGenericTable('volume', fromUnit, toUnit, fromValue, toValue); }

    function convertUnits(cat) { if (cat==='temp') { convertTemp(); return; } let d=unitData[cat]; let val=parseFloat(document.getElementById(`conv-${cat}-input`).value); let from=document.getElementById(`conv-${cat}-unit`).value; let resDiv=document.getElementById(`conv-${cat}-results`); if(isNaN(val)) { resDiv.innerHTML='<p style="text-align:center;color:#c74a4a;font-size:14px;padding:16px;">Введите значение</p>'; return; } let base=val*d.units[from].factor; let html='<div class="converter-result-label-title">Результаты</div>'; let delay=0; for(let u in d.units){ if(u===from) continue; let v=base/d.units[u].factor; let showTableFn = '';
            if (cat === 'pressure') showTableFn = `showPressureTable`;
            else if (cat === 'flow') showTableFn = `showFlowTable`;
            else if (cat === 'mass') showTableFn = `showMassTable`;
            else if (cat === 'length') showTableFn = `showLengthTable`;
            else if (cat === 'density') showTableFn = `showDensityTable`;
            else if (cat === 'time') showTableFn = `showTimeTable`;
            else if (cat === 'volume') showTableFn = `showVolumeTable`;

            if (showTableFn) {
                html+=`<div class="converter-result-item" style="animation-delay:${delay}ms;cursor:pointer;" onclick="${showTableFn}('${from}', '${u}', ${val}, ${v})"><span class="converter-result-label">${d.units[u].label}</span><span class="converter-result-value">${formatNumber(v)} <span style="color:rgba(255,255,255,0.25);font-weight:400;font-size:0.85em;">(${roundNumber(v)})</span></span></div>`;
            } else {
                html+=`<div class="converter-result-item" style="animation-delay:${delay}ms"><span class="converter-result-label">${d.units[u].label}</span><span class="converter-result-value">${formatNumber(v)} <span style="color:rgba(255,255,255,0.25);font-weight:400;font-size:0.85em;">(${roundNumber(v)})</span></span></div>`;
            } delay+=40; } resDiv.innerHTML=html; }
    function convertTemp() { let val=parseFloat(document.getElementById('conv-temp-input').value); let from=document.getElementById('conv-temp-unit').value; let resDiv=document.getElementById('conv-temp-results'); if(isNaN(val)) { resDiv.innerHTML='<p style="text-align:center;color:#c74a4a;font-size:14px;padding:16px;">Введите значение</p>'; return; } let c=from==='C'?val:from==='F'?(val-32)*5/9:from==='K'?val-273.15:from==='R'?val*1.25:(val-491.67)*5/9; let tU={'C':{label:'°C',fn:z=>z},'F':{label:'°F',fn:z=>z*9/5+32},'K':{label:'K',fn:z=>z+273.15},'R':{label:'°R',fn:z=>z*0.8},'Ra':{label:'°Ra',fn:z=>(z+273.15)*9/5}}; let html='<div class="converter-result-label-title">Результаты</div>'; let delay=0; for(let u in tU){ if(u===from) continue; let v=tU[u].fn(c); html+=`<div class="converter-result-item" style="animation-delay:${delay}ms;cursor:pointer;" onclick="showTempTable('${from}', '${u}', ${val}, ${v})"><span class="converter-result-label">${tU[u].label}</span><span class="converter-result-value">${formatNumber(v)} <span style="color:rgba(255,255,255,0.25);font-weight:400;font-size:0.85em;">(${roundNumber(v)})</span></span></div>`; delay+=40; } resDiv.innerHTML=html; }

    // Шкала-сигнал
    const sigUnitLabels={'4_20':'мА','0_20':'мА','0_5mA':'мА','0_10V':'В','1_5V':'В','0_5V':'В','bipolar_10':'В','20_100_kPa':'кПа','0_2_1_0_bar':'бар','3_15_psi':'psi','0_2_1_0_kgf_cm2':'кгс/см²','custom':'ед.'};
    function setSignalDefaults() { let type=document.getElementById('sigType').value; let def={'4_20':[4,20],'0_20':[0,20],'0_5mA':[0,5],'0_10V':[0,10],'1_5V':[1,5],'0_5V':[0,5],'bipolar_10':[-10,10],'20_100_kPa':[20,100],'0_2_1_0_bar':[0.2,1.0],'3_15_psi':[3,15],'0_2_1_0_kgf_cm2':[0.2,1.0]}; let customDiv=document.getElementById('sigCustomRange'); if(def[type]){document.getElementById('sigMin').value=def[type][0]; document.getElementById('sigMax').value=def[type][1]; customDiv.style.display='none';} else{document.getElementById('sigMin').value='0'; document.getElementById('sigMax').value='100'; document.getElementById('sigUnitCustom').value='%'; customDiv.style.display='block';} document.getElementById('sigUnitLabel').innerText=sigUnitLabels[type]; }
    function setScaleDefaults() { let type=document.getElementById('scalePreset').value; let def={'0_100':[0,100,'%'],'0_20':[0,20,'мА'],'0_5mA':[0,5,'мА'],'0_10V':[0,10,'В'],'1_5V':[1,5,'В'],'0_5V':[0,5,'В'],'bipolar_10':[-10,10,'В'],'20_100_kPa':[20,100,'кПа'],'0_2_1_0_bar':[0.2,1.0,'бар'],'3_15_psi':[3,15,'psi'],'0_2_1_0_kgf_cm2':[0.2,1.0,'кгс/см²']}; let customDiv=document.getElementById('scaleCustomRange'); if(def[type]){document.getElementById('scaleMin').value=def[type][0]; document.getElementById('scaleMax').value=def[type][1]; document.getElementById('scaleUnitName').value=def[type][2]; customDiv.style.display='none';} else{customDiv.style.display='block';} }
    function calcScaleSignal() { let smin=parseFloat(document.getElementById('scaleMin').value); let smax=parseFloat(document.getElementById('scaleMax').value); let gmin=parseFloat(document.getElementById('sigMin').value); let gmax=parseFloat(document.getElementById('sigMax').value); let scaleType=document.getElementById('scaleType').value; if(isNaN(smin)||isNaN(smax)||isNaN(gmin)||isNaN(gmax)){showToast('Заполните все поля');return;} if(smin===smax||gmin===gmax){showToast('Пределы не должны совпадать');return;} document.getElementById('scaleResultsArea').style.display='block'; let unit=document.getElementById('scaleUnitName').value||'ед.'; let sigRange=getSignalRangeAndUnit(document.getElementById('sigType').value); let sigUnit=sigRange.unit; let typeLabels={linear:'Линейная',quadratic:'Квадратичная',sqrt:'Корнеизвлекающая'}; let pct=[0,5,10,15,20,25,30,40,50,60,70,75,80,90,95,100]; let html='<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);"><table style="min-width:100%;width:100%;border-collapse:collapse;"><thead><tr style="background:rgba(22,27,34,0.7);"><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;text-align:left;">%</th><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;text-align:left;">Шкала ('+unit+')</th><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;text-align:left;">Сигнал ('+sigUnit+')</th></tr></thead><tbody>'; for(let i=0;i<pct.length;i++){ let pr=pct[i]/100; let scaleVal=smin+(smax-smin)*pr; let sigVal; if(scaleType==='quadratic'){ sigVal=gmin+(gmax-gmin)*pr*pr; } else if(scaleType==='sqrt'){ sigVal=gmin+(gmax-gmin)*Math.sqrt(pr); } else { sigVal=gmin+(gmax-gmin)*pr; } let bg=i%2?'rgba(22,27,34,0.4)':'rgba(13,17,23,0.4)'; html+=`<tr style="background:${bg};"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${pct[i]}</td><td style="padding:8px 12px;font-size:18px;color:#e0e0e0;">${formatNumber(scaleVal)}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatNumber(sigVal)}</td></tr>`; } html+='</tbody></table></div>'; html+=`<div style="margin-top:10px;padding:8px 12px;background:rgba(13,17,23,0.4);border-radius:8px;font-size:12px;color:rgba(255,255,255,0.35);">Тип шкалы: <b style="color:#4a8fc7;">${typeLabels[scaleType]}</b> · Сигнал: ${sigRange.label}</div>`; document.getElementById('scaleTableContainer').innerHTML=html; document.getElementById('queryScaleResult').innerHTML=''; document.getElementById('querySigResult').innerHTML=''; setTimeout(()=>document.getElementById('scaleResultsArea').scrollIntoView({behavior:'smooth',block:'start'}),100); }
    function queryFromScale(){ let smin=parseFloat(document.getElementById('scaleMin').value), smax=parseFloat(document.getElementById('scaleMax').value), gmin=parseFloat(document.getElementById('sigMin').value), gmax=parseFloat(document.getElementById('sigMax').value), scaleType=document.getElementById('scaleType').value, q=parseFloat(document.getElementById('queryScaleVal').value), unit=document.getElementById('scaleUnitName').value||'ед.', sigRange=getSignalRangeAndUnit(document.getElementById('sigType').value), sigUnit=sigRange.unit, res=document.getElementById('queryScaleResult'); if(isNaN(q)){res.innerHTML='<p style="color:#c74a4a;font-size:12px;">Введите значение</p>';return;} let p=(q-smin)/(smax-smin); let sig; if(scaleType==='quadratic'){ sig=gmin+(gmax-gmin)*p*p; } else if(scaleType==='sqrt'){ sig=gmin+(gmax-gmin)*Math.sqrt(p); } else { sig=gmin+(gmax-gmin)*p; } res.innerHTML=`<div style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="color:rgba(255,255,255,0.4);">Шкала: <b>${formatNumber(q)} ${unit}</b> (${(p*100).toFixed(2)}%)</span></div><div style="padding:8px 10px;background:rgba(13,17,23,0.4);border-radius:8px;margin-top:5px;"><span style="color:rgba(255,255,255,0.4);">→ Сигнал: <b style="color:#4ac771;">${formatNumber(sig)} ${sigUnit}</b></span></div>`; }
    function queryFromSignal(){ let smin=parseFloat(document.getElementById('scaleMin').value), smax=parseFloat(document.getElementById('scaleMax').value), gmin=parseFloat(document.getElementById('sigMin').value), gmax=parseFloat(document.getElementById('sigMax').value), scaleType=document.getElementById('scaleType').value, q=parseFloat(document.getElementById('querySigVal').value), unit=document.getElementById('scaleUnitName').value||'ед.', sigRange=getSignalRangeAndUnit(document.getElementById('sigType').value), sigUnit=sigRange.unit, res=document.getElementById('querySigResult'); if(isNaN(q)){res.innerHTML='<p style="color:#c74a4a;font-size:12px;">Введите значение</p>';return;} let p=(q-gmin)/(gmax-gmin); let val_lin; if(scaleType==='quadratic'){ val_lin=Math.sqrt(p); } else if(scaleType==='sqrt'){ val_lin=p*p; } else { val_lin=p; } let val=smin+(smax-smin)*val_lin; res.innerHTML=`<div style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="color:rgba(255,255,255,0.4);">Сигнал: <b>${formatNumber(q)} ${sigUnit}</b> (${(p*100).toFixed(2)}%)</span></div><div style="padding:8px 10px;background:rgba(13,17,23,0.4);border-radius:8px;margin-top:5px;"><span style="color:rgba(255,255,255,0.4);">→ Шкала: <b style="color:#4ac771;">${formatNumber(val)} ${unit}</b></span></div>`; }

    // Расчёт погрешности для всех типов
    
    
    
    

    // ТС и ТП (полные данные)
    const rtdData = {
        'pt10': { name:'Pt10 (10П)', group:'Pt', r0:10, nsc:'10П', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-100,450]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-196,600]}, classC:{formula:{const:0.60,coeff:0.0100},range:[-196,600]} },
        'pt50': { name:'Pt50 (50П)', group:'Pt', r0:50, nsc:'50П', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-100,450]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-196,600]}, classC:{formula:{const:0.60,coeff:0.0100},range:[-196,600]} },
        'pt100': { name:'Pt100 (100П)', group:'Pt', r0:100, nsc:'100П', classAA:{formula:{const:0.10,coeff:0.0017},range:[-50,250]}, classA:{formula:{const:0.15,coeff:0.0020},range:[-100,450]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-196,600]}, classC:{formula:{const:0.60,coeff:0.0100},range:[-196,600]} },
        'pt500': { name:'Pt500 (500П)', group:'Pt', r0:500, nsc:'500П', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-200,600]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-200,600]}, classC:{formula:{const:0.60,coeff:0.0100},range:[-200,600]} },
        'pt1000': { name:'Pt1000 (1000П)', group:'Pt', r0:1000, nsc:'1000П', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-200,600]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-200,600]}, classC:{formula:{const:0.60,coeff:0.0100},range:[-200,600]} },
        'cu10': { name:'Cu10 (10М)', group:'Cu', r0:10, nsc:'10М', classAA:null, classA:null, classB:{formula:{const:0.30,coeff:0.0050},range:[-50,150]}, classC:null },
        'cu50': { name:'Cu50 (50М)', group:'Cu', r0:50, nsc:'50М', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-50,150]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-50,150]}, classC:null },
        'cu100': { name:'Cu100 (100М)', group:'Cu', r0:100, nsc:'100М', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-50,150]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-50,150]}, classC:null },
        'ni50': { name:'Ni50 (50Н)', group:'Ni', r0:50, nsc:'50Н', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-60,180]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-60,180]}, classC:null },
        'ni100': { name:'Ni100 (100Н)', group:'Ni', r0:100, nsc:'100Н', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-60,180]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-60,180]}, classC:null },
        'ni120': { name:'Ni120 (120Н)', group:'Ni', r0:120, nsc:'120Н', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-60,180]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-60,180]}, classC:null },
        'ni500': { name:'Ni500 (500Н)', group:'Ni', r0:500, nsc:'500Н', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-60,180]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-60,180]}, classC:null },
        'ni1000': { name:'Ni1000 (1000Н)', group:'Ni', r0:1000, nsc:'1000Н', classAA:null, classA:{formula:{const:0.15,coeff:0.0020},range:[-60,180]}, classB:{formula:{const:0.30,coeff:0.0050},range:[-60,180]}, classC:null }
    };
    function updateRtdTypeOptions(){ let g=document.getElementById('rtd_group').value; let typeSel=document.getElementById('rtd_type'); let classSel=document.getElementById('rtd_class'); let opts=''; if(g==='Pt'){ opts='<option value="pt10">Pt10 (10П)</option><option value="pt50">Pt50 (50П)</option><option value="pt100" selected>Pt100 (100П)</option><option value="pt500">Pt500 (500П)</option><option value="pt1000">Pt1000 (1000П)</option>'; classSel.innerHTML='<option value="AA">AA (1/3 B)</option><option value="A" selected>A</option><option value="B">B</option><option value="C">C</option>'; } else if(g==='Cu'){ opts='<option value="cu10">Cu10 (10М)</option><option value="cu50">Cu50 (50М)</option><option value="cu100" selected>Cu100 (100М)</option>'; classSel.innerHTML='<option value="A">A</option><option value="B" selected>B</option>'; } else if(g==='Ni'){ opts='<option value="ni50">Ni50 (50Н)</option><option value="ni100">Ni100 (100Н)</option><option value="ni120">Ni120 (120Н)</option><option value="ni500">Ni500 (500Н)</option><option value="ni1000" selected>Ni1000 (1000Н)</option>'; classSel.innerHTML='<option value="A">A</option><option value="B" selected>B</option>'; } typeSel.innerHTML=opts; updateRtdClassOptions(); }
    function updateRtdClassOptions(){ let type=document.getElementById('rtd_type').value; let d=rtdData[type]; let classSel=document.getElementById('rtd_class'); if(!d)return; for(let i=0;i<classSel.options.length;i++){ let opt=classSel.options[i]; let key='class'+opt.value.toUpperCase(); let avail=!!d[key]; opt.disabled=!avail; if(!avail&&opt.selected){ for(let j=0;j<classSel.options.length;j++){ if(!classSel.options[j].disabled){ classSel.options[j].selected=true; break; } } } } }
    function calcRtdError(){ let type=document.getElementById('rtd_type').value; let cls=document.getElementById('rtd_class').value.toLowerCase(); let t=parseFloat(document.getElementById('rtd_temperature').value); let warn=document.getElementById('rtd_range_warning'); if(isNaN(t)){showToast('Введите температуру');return;} let d=rtdData[type]; if(!d){showToast('Некорректный тип ТС');return;} let data=d['class'+cls.toUpperCase()]; if(!data){showToast(`Класс ${cls.toUpperCase()} не определён`);return;} let absT=Math.abs(t); let err=data.formula.const+data.formula.coeff*absT; let rng=data.range; if(t<rng[0]||t>rng[1]){ warn.style.display='block'; warn.innerHTML=`⚠️ Температура ${t}°C вне диапазона [${rng[0]}…${rng[1]}]°C`; }else warn.style.display='none'; let groupNames={Pt:'Платиновый (Pt)',Cu:'Медный (Cu)',Ni:'Никелевый (Ni)'}; let html=`<div class="converter-result-label-title">Результаты (ГОСТ 6651-2009)</div><div class="converter-result-item"><span class="converter-result-label">Тип ТС</span><span class="converter-result-value">${d.name}</span></div><div class="converter-result-item"><span class="converter-result-label">Материал</span><span class="converter-result-value">${groupNames[d.group]}</span></div><div class="converter-result-item"><span class="converter-result-label">R₀ (0°C)</span><span class="converter-result-value">${d.r0} Ом</span></div><div class="converter-result-item"><span class="converter-result-label">Класс допуска</span><span class="converter-result-value">${cls.toUpperCase()}</span></div><div class="converter-result-item"><span class="converter-result-label">Предел погрешности</span><span class="converter-result-value">± ${formatNumber(err)} °C</span></div><div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">Δ = ±(${data.formula.const} + ${data.formula.coeff}·|t|) °C</span></div><div class="converter-result-item"><span class="converter-result-label">Диапазон</span><span class="converter-result-value">${rng[0]} … ${rng[1]} °C</span></div>`; document.getElementById('rtdResults').innerHTML=html; document.getElementById('rtdResults').style.display='block'; setTimeout(()=>document.getElementById('rtdResults').scrollIntoView({behavior:'smooth',block:'start'}),100); }

    const tcData={
        'K':{name:'K (ТХА)',ranges:{class1:[[-40,375,'const',1.5],[375,1000,'linear',0.004]],class2:[[-40,333,'const',2.5],[333,1300,'linear',0.0075]],class3:[[-250,-167,'linear',0.015],[-167,40,'const',2.5]]}},
        'J':{name:'J (ТЖК)',ranges:{class1:[[-40,375,'const',1.5],[375,750,'linear',0.004]],class2:[[0,333,'const',2.5],[333,900,'linear',0.0075]],class3:null}},
        'T':{name:'T (ТМК)',ranges:{class1:[[-40,125,'const',0.5],[125,350,'linear',0.004]],class2:[[-40,135,'const',1.0],[135,350,'linear',0.0075]],class3:[[-200,-66,'linear',0.015],[-66,40,'const',1.0]]}},
        'N':{name:'N (ТНН)',ranges:{class1:[[-40,375,'const',1.5],[375,1000,'linear',0.004]],class2:[[-40,333,'const',2.5],[333,1300,'linear',0.0075]],class3:[[-250,-167,'linear',0.015],[-167,40,'const',2.5]]}},
        'E':{name:'E (ТХКн)',ranges:{class1:[[-40,375,'const',1.5],[375,800,'linear',0.004]],class2:[[-40,333,'const',2.5],[333,900,'linear',0.0075]],class3:[[-200,-167,'linear',0.015],[-167,40,'const',2.5]]}},
        'R':{name:'R (ТПП 13% Rh)',ranges:{class1:[[0,1100,'const',1.0],[1100,1600,'linear2',[1.0,0.003]]],class2:[[0,600,'const',1.5],[600,1600,'linear',0.0025]],class3:null}},
        'S':{name:'S (ТПП 10% Rh)',ranges:{class1:[[0,1100,'const',1.0],[1100,1600,'linear2',[1.0,0.003]]],class2:[[0,600,'const',1.5],[600,1600,'linear',0.0025]],class3:null}},
        'B':{name:'B (ТПР 30/6%)',ranges:{class1:null,class2:[[600,1700,'linear',0.005]],class3:[[600,800,'const',4.0],[800,1700,'linear',0.005]]}}
    };
    function updateTcRanges(){ let type=document.getElementById('tc_type').value; let cls=document.getElementById('tc_class').value; let warn=document.getElementById('tc_range_warning'); if(tcData[type] && tcData[type].ranges['class'+cls]) warn.style.display='none'; }
    function calcTcError(){ let type=document.getElementById('tc_type').value; let cls=document.getElementById('tc_class').value; let t=parseFloat(document.getElementById('tc_temperature').value); let warn=document.getElementById('tc_range_warning'); if(isNaN(t)){showToast('Введите температуру');return;} let data=tcData[type]; if(!data){showToast('Некорректный тип термопары');return;} let classData=data.ranges['class'+cls]; if(!classData){showToast(`Класс ${cls} не определён`);return;} let absT=Math.abs(t); let err=null, formula='', valid=''; for(let i=0;i<classData.length;i++){ let r=classData[i]; if(t>=r[0]&&t<=r[1]){ if(r[2]==='const'){ err=r[3]; formula=`Δ = ±${r[3]} °C`; } else if(r[2]==='linear'){ err=r[3]*absT; formula=`Δ = ±(${r[3]}·|t|) °C`; } else if(r[2]==='linear2'){ let p=r[3]; err=p[0]+p[1]*(t-1100); formula=`Δ = ±[${p[0]} + ${p[1]}·(t−1100)] °C`; } valid=`${r[0]} … ${r[1]} °C`; break; } } if(err===null||isNaN(err)){ warn.style.display='block'; warn.innerHTML=`⚠️ Температура ${t}°C вне допустимого диапазона для данного класса`; return; } else warn.style.display='none'; let html=`<div class="converter-result-label-title">Результаты (ГОСТ Р 8.585-2001)</div><div class="converter-result-item"><span class="converter-result-label">Тип термопары</span><span class="converter-result-value">${data.name}</span></div><div class="converter-result-item"><span class="converter-result-label">Класс точности (<span class="greek-gamma">&gamma;</span>)</span><span class="converter-result-value">${cls}</span></div><div class="converter-result-item"><span class="converter-result-label">Предел погрешности</span><span class="converter-result-value">± ${formatNumber(err)} °C</span></div><div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">${formula}</span></div><div class="converter-result-item"><span class="converter-result-label">Диапазон</span><span class="converter-result-value">${valid}</span></div>`; document.getElementById('tcResults').innerHTML=html; document.getElementById('tcResults').style.display='block'; setTimeout(()=>document.getElementById('tcResults').scrollIntoView({behavior:'smooth',block:'start'}),100); }

    // Буйковый уровнемер
    const G = 9.80665;
    function setLiquidDensity(){ let p=document.getElementById('liquid_preset').value; if(p!=='custom') document.getElementById('liquid_density').value=p; }
    function getSignalRangeAndUnit(st){ let r={ '4_20':{min:4,max:20,unit:'мА',label:'4-20 мА'}, '0_20':{min:0,max:20,unit:'мА',label:'0-20 мА'}, '0_5mA':{min:0,max:5,unit:'мА',label:'0-5 мА'}, '0_10V':{min:0,max:10,unit:'В',label:'0-10 В'}, '1_5V':{min:1,max:5,unit:'В',label:'1-5 В'}, '0_5V':{min:0,max:5,unit:'В',label:'0-5 В'}, 'bipolar_10':{min:-10,max:10,unit:'В',label:'-10...+10 В'}, '20_100_kPa':{min:20,max:100,unit:'кПа',label:'20-100 кПа'}, '0_2_1_0_bar':{min:0.2,max:1.0,unit:'бар',label:'0.2-1.0 бар'}, '3_15_psi':{min:3,max:15,unit:'psi',label:'3-15 psi'}, '0_2_1_0_kgf_cm2':{min:0.2,max:1.0,unit:'кгс/см²',label:'0.2-1.0 кгс/см²'} }; if(st==='custom'){ let cmin=parseFloat(document.getElementById('signal_min_custom').value); let cmax=parseFloat(document.getElementById('signal_max_custom').value); let cunit=document.getElementById('signal_unit_custom').value; return { min:cmin, max:cmax, unit:cunit, label:(isNaN(cmin)?'?':cmin)+'-'+(isNaN(cmax)?'?':cmax)+' '+cunit, isCustom:true }; } return r[st]||r['4_20']; }
    function updateBuoySignalUnit(){ let st=document.getElementById('buoy_signal_type').value; let cd=document.getElementById('customSignalRange'); let ud=document.getElementById('signalUnitDisplay'); if(st==='custom'){ cd.style.display='block'; ud.innerHTML='📊 Выберите диапазон и единицы'; ud.style.color='#4ac771'; }else{ cd.style.display='none'; ud.innerHTML='📊 Сигнал: '+getSignalRangeAndUnit(st).label; ud.style.color='rgba(255,255,255,0.25)'; } }
    function calculateSignalValue(pct,st){ let r=getSignalRangeAndUnit(st); if(r.isCustom && (isNaN(r.min)||isNaN(r.max))) return {value:0,unit:r.unit,isValid:false}; if(r.min===r.max) return {value:r.min,unit:r.unit,isValid:true}; return {value:r.min+(pct/100)*(r.max-r.min),unit:r.unit,isValid:true}; }
    function calcBuoyVolume(d,l){ let r=(d/1000)/2, l_m=l/1000; return Math.PI*r*r*l_m; }
    function calcBuoyancyMass(pct,d,l,rho){ let l_m=l/1000, sub=(pct/100)*l_m; if(sub<=0)return 0; if(sub>l_m)sub=l_m; let r=(d/1000)/2; return Math.PI*r*r*sub*rho; }
    function formatBuoyNumber(n){ if(n===0)return '0'; if(Math.abs(n)<0.0001)return n.toExponential(4); let d=Math.abs(n)>=100?2:Math.abs(n)>=1?3:4; return parseFloat(n.toFixed(d)).toString(); }
    function copyBuoyTable(){ let t=document.getElementById('buoyTableContainer'); if(!t)return; let rows=t.querySelectorAll('tr'), data=[]; for(let i=0;i<rows.length;i++){ let cells=rows[i].querySelectorAll('th,td'), row=[]; for(let j=0;j<cells.length;j++) row.push(cells[j].innerText); data.push(row.join('\t')); } navigator.clipboard.writeText(data.join('\n')).then(()=>showToast('Таблица скопирована')).catch(()=>showToast('Ошибка копирования')); }
    function calculateBuoyCalibration(){ let d=parseFloat(document.getElementById('buoy_diam').value); let l=parseFloat(document.getElementById('buoy_length').value); let w=parseFloat(document.getElementById('buoy_weight_kg').value); let rho=parseFloat(document.getElementById('liquid_density').value); let m_s=parseFloat(document.getElementById('suspension_mass').value) / 1000; let st=document.getElementById('buoy_signal_type').value; let method=getSelectedCalibMethod(); if(isNaN(d)||d<=0){showToast('Введите диаметр');return;} if(isNaN(l)||l<=0){showToast('Введите длину');return;} if(method==='without_buoy'&&(isNaN(w)||w<=0)){showToast('Введите вес буйка');return;} if(isNaN(rho)||rho<=0){showToast('Введите плотность жидкости');return;} if(isNaN(m_s)||m_s<0){showToast('Введите массу подвеса');return;} let sigRange=getSignalRangeAndUnit(st); if(st==='custom'&&(isNaN(sigRange.min)||isNaN(sigRange.max))){showToast('Введите диапазон сигнала');return;} let vol=calcBuoyVolume(d,l); let results=[]; for(let p=0;p<=100;p+=10){ let m_buoy=calcBuoyancyMass(p,d,l,rho); let mass_kg=method==='without_buoy'? w - m_buoy + m_s : m_buoy + m_s; let sig=calculateSignalValue(p,st); results.push({pct:p, mass_kg:mass_kg, signal:sig.value, sigUnit:sig.unit}); } let html='<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);"><table style="min-width:100%;width:100%;border-collapse:collapse;"><thead><tr style="background:rgba(22,27,34,0.7);"><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;">Уровень (%)</th><th style="padding:10px 12px;font-size:16px;color:#4ac771;">Масса гирь (г)</th><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;">Сигнал ('+results[0].sigUnit+')</th></tr></thead><tbody>'; for(let i=0;i<results.length;i++){ let r=results[i]; let bg=i%2?'rgba(22,27,34,0.4)':'rgba(13,17,23,0.4)'; html+=`<tr style="background:${bg};"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${r.pct}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatBuoyNumber(r.mass_kg*1000)}</td><td style="padding:8px 12px;font-size:18px;color:#5b9bd5;">${formatBuoyNumber(r.signal)}</td></tr>`; } html+='</tbody></table></div>'; let methodName=method==='without_buoy'?'Без буйка':'С буйком'; let formulaText=method==='without_buoy'?'m_гири = m_буйка − m_выт + m_подвеса':'m_гири = m_выт + m_подвеса'; let infoHtml=`<strong>${methodName}</strong><br>📐 ${formulaText}<br>`; if(method==='without_buoy') infoHtml+=`⚖️ Вес буйка: ${formatBuoyNumber(w)} кг<br>`; infoHtml+=`💧 Плотность: ${formatBuoyNumber(rho)} кг/м³<br>📏 Объём: ${formatBuoyNumber(vol*1e6)} см³<br>⚖️ Масса гирь: ${formatBuoyNumber(results[results.length-1].mass_kg*1000)} г (100%)<br>📡 Сигнал: ${sigRange.label}`; document.getElementById('buoyTableContainer').innerHTML=html; document.getElementById('buoyInfo').innerHTML=infoHtml; document.getElementById('buoyResults').style.display='block'; setTimeout(()=>document.getElementById('buoyResults').scrollIntoView({behavior:'smooth',block:'start'}),100); }
    function selectCalibMethod(m){ SafeStorage.setItem('buoy_calib_method', m); navigateTo('buoy-calc'); }
    function getSelectedCalibMethod(){ let m=SafeStorage.getItem('buoy_calib_method'); return (m==='with_buoy'||m==='without_buoy')?m:'with_buoy'; }
    function setCalibMethodOnForm(){ let m=getSelectedCalibMethod(); let ind=document.getElementById('selectedMethodText'); if(ind) ind.innerText=m==='with_buoy'?'С буйком':'Без буйка'; updateBuoyCalcTitle(); let wCont=document.getElementById('buoyWeightContainer'); if(wCont) wCont.style.display=m==='with_buoy'?'none':'block'; }
    function updateBuoyCalcTitle(){ let m=getSelectedCalibMethod(); let t=document.getElementById('buoyCalcTitle'); if(t) t.innerText=m==='with_buoy'?'Калибровка: с буйком':'Калибровка: без буйка'; }

    function calcErrorKit(){
        let devices = [];
        for(let i=1;i<=3;i++){
            let min=parseFloat(document.getElementById('kit_dev'+i+'_range_min').value);
            let max=parseFloat(document.getElementById('kit_dev'+i+'_range_max').value);
            let cls=parseFloat(document.getElementById('kit_dev'+i+'_accuracy').value);
            if(isNaN(min)||isNaN(max)||isNaN(cls)){
                if(i<3){showToast('Заполните все поля для прибора '+i);return;}
                else continue;
            }
            if(min>=max){showToast('НПИ должен быть меньше ВПИ (прибор '+i+')');return;}
            if(cls<=0){showToast('Класс точности должен быть положительным (прибор '+i+')');return;}
            let xNorm = (min===0 || min*max<0) ? (Math.abs(max)+Math.abs(min)) : Math.abs(max);
            let absErr=(cls/100)*xNorm;
            devices.push({num:i,min:min,max:max,cls:cls,xNorm:xNorm,absErr:absErr});
        }
        if(devices.length===0){showToast('Введите данные хотя бы одного прибора');return;}
        let totalAbs = 0;
        for(let d of devices) totalAbs += d.absErr*d.absErr;
        totalAbs = Math.sqrt(totalAbs);
        let html='<div class="converter-result-label-title">Результаты расчёта (ГОСТ 8.401-80)</div>';
        for(let d of devices){
            html+=`<div class="converter-result-item"><span class="converter-result-label">Прибор ${d.num}: абс. погрешность</span><span class="converter-result-value">± ${formatNumber(d.absErr)} ед.</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Прибор ${d.num}: диапазон</span><span class="converter-result-value">${formatNumber(d.min)} … ${formatNumber(d.max)}</span></div>`;
        }
        html+=`<div class="converter-result-item"><span class="converter-result-label">Суммарная абс. погрешность (±Δ<sub>Σ</sub>)</span><span class="converter-result-value">± ${formatNumber(totalAbs)} ед.</span></div>`;
        html+=`<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">Δ<sub>Σ</sub> = √(Δ₁² + Δ₂² + … + Δₙ²)</span></div>`;
        document.getElementById('errorKitResults').innerHTML=html;
        document.getElementById('errorKitResults').style.display='block';
        setTimeout(()=>document.getElementById('errorKitResults').scrollIntoView({behavior:'smooth',block:'start'}),100);
    }

    function updateTempSensorOptions(){
        let type=document.getElementById('temp_sensor_type').value;
        document.getElementById('rtd_options').style.display=type==='rtd'?'block':'none';
        document.getElementById('tc_options').style.display=type==='tc'?'block':'none';
    }
    function calcTempSensor(){
        let type=document.getElementById('temp_sensor_type').value;
        let tMin=parseFloat(document.getElementById('temp_sensor_min').value);
        let tMax=parseFloat(document.getElementById('temp_sensor_max').value);
        let step=parseFloat(document.getElementById('temp_sensor_step').value)||10;
        let resDiv=document.getElementById('tempSensorResults');
        if(isNaN(tMin)||isNaN(tMax)){showToast('Введите диапазон измерения');return;}
        if(tMin>=tMax){showToast('Минимум должен быть меньше максимума');return;}
        if(step<=0){step=10;}
        if(type==='rtd'){
            let rtdType=document.getElementById('temp_rtd_type').value;
            let sensorData={
                cu50_1428:{r0:50,alpha:0.00428,name:'Cu50 (50М)',nsc:'cu',formula:'R(t) = R₀(1 + 0,00428·t)'},
                cu100_1428:{r0:100,alpha:0.00428,name:'Cu100 (100М)',nsc:'cu',formula:'R(t) = R₀(1 + 0,00428·t)'},
                cu50_1426:{r0:50,alpha:0.00426,name:'Cu50 (50М)',nsc:'cu',formula:'R(t) = R₀(1 + 0,00426·t)'},
                cu100_1426:{r0:100,alpha:0.00426,name:'Cu100 (100М)',nsc:'cu',formula:'R(t) = R₀(1 + 0,00426·t)'},
                pt50_1391:{r0:50,name:'Pt50 (50П)',nsc:'pt1391',formula:'R(t) = R₀[1 + At + Bt²], A=3,96847·10⁻³, B=−5,84·10⁻⁷'},
                pt100_1391:{r0:100,name:'Pt100 (100П)',nsc:'pt1391',formula:'R(t) = R₀[1 + At + Bt²], A=3,96847·10⁻³, B=−5,84·10⁻⁷'},
                pt100_1385:{r0:100,name:'Pt100',nsc:'pt1385',formula:'R(t) = R₀[1 + At + Bt² + C(t−100)t³], IEC 60751 / ГОСТ 6651-2009'},
                pt1000_1385:{r0:1000,name:'Pt1000',nsc:'pt1385',formula:'R(t) = R₀[1 + At + Bt² + C(t−100)t³], IEC 60751 / ГОСТ 6651-2009'}
            };
            let sd=sensorData[rtdType];
            if(!sd){showToast('Неизвестный тип ТС');return;}
            let isCu=sd.nsc==='cu';
            let html=`<div class="converter-result-label-title">Результаты расчёта (ГОСТ 6651-2009)</div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Тип ТС</span><span class="converter-result-value">${sd.name}</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Диапазон</span><span class="converter-result-value">${formatNumber(tMin)} … ${formatNumber(tMax)} °C</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">R₀ (при 0°C)</span><span class="converter-result-value">${sd.r0} Ом</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">${sd.formula}</span></div>`;
            html+=`<div style="margin-top:14px;"><div class="converter-result-label-title">Таблица значений (шаг ${step}°C)</div>`;
            html+=`<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);"><table style="min-width:100%;width:100%;border-collapse:collapse;"><thead><tr style="background:rgba(22,27,34,0.7);"><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;text-align:left;">t, °C</th><th style="padding:10px 12px;font-size:16px;color:#4ac771;text-align:left;">R(t), Ом</th></tr></thead><tbody>`;
            let start=Math.ceil(tMin/step)*step;
            let end=Math.floor(tMax/step)*step;
            if(start>tMax||end<tMin){start=tMin;end=tMax;}
            let row=0;
            for(let tc=start;tc<=end;tc+=step){
                let rv=isCu?calcCuResistance(tc,sd.r0,sd.alpha):calcRtdResistance(tc,sd.r0,sd.nsc);
                let bg=row%2?'rgba(22,27,34,0.4)':'rgba(13,17,23,0.4)';
                html+=`<tr style="background:${bg};"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${tc}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatNumber(rv)}</td></tr>`;
                row++;
            }
            if(row===0){
                let rv=isCu?calcCuResistance(tMin,sd.r0,sd.alpha):calcRtdResistance(tMin,sd.r0,sd.nsc);
                html+=`<tr style="background:rgba(13,17,23,0.4);"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${tMin}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatNumber(rv)}</td></tr>`;
            }
            html+=`</tbody></table></div></div>`;
            resDiv.innerHTML=html;
        } else {
            let tcType=document.getElementById('temp_tc_type').value;
            let names={K:'K (ТХА)',J:'J (ТЖК)',T:'T (ТМК)',N:'N (ТНН)',E:'E (ТХКн)',R:'R (ТПП)',S:'S (ТПП)',B:'B (ТПР)'};
            let html=`<div class="converter-result-label-title">Результаты расчёта (ГОСТ Р 8.585-2001)</div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Тип термопары</span><span class="converter-result-value">${names[tcType]}</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Диапазон</span><span class="converter-result-value">${formatNumber(tMin)} … ${formatNumber(tMax)} °C</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">E(0°C)</span><span class="converter-result-value">0.000 мВ</span></div>`;
            html+=`<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">E = Σ cᵢ·tⁱ (полином НИСТ)</span></div>`;
            html+=`<div style="margin-top:14px;"><div class="converter-result-label-title">Таблица значений (шаг ${step}°C)</div>`;
            html+=`<div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05);"><table style="min-width:100%;width:100%;border-collapse:collapse;"><thead><tr style="background:rgba(22,27,34,0.7);"><th style="padding:10px 12px;font-size:16px;color:#4a8fc7;text-align:left;">t, °C</th><th style="padding:10px 12px;font-size:16px;color:#4ac771;text-align:left;">E(t), мВ</th></tr></thead><tbody>`;
            let start=Math.ceil(tMin/step)*step;
            let end=Math.floor(tMax/step)*step;
            if(start>tMax||end<tMin){start=tMin;end=tMax;}
            let row=0;
            for(let tc=start;tc<=end;tc+=step){
                let ev=calcTcVoltage(tc,tcType);
                let bg=row%2?'rgba(22,27,34,0.4)':'rgba(13,17,23,0.4)';
                html+=`<tr style="background:${bg};"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${tc}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatNumber(ev)}</td></tr>`;
                row++;
            }
            if(row===0){
                let ev=calcTcVoltage(tMin,tcType);
                html+=`<tr style="background:rgba(13,17,23,0.4);"><td style="padding:8px 12px;font-size:18px;color:rgba(255,255,255,0.4);">${tMin}</td><td style="padding:8px 12px;font-size:18px;color:#4ac771;">${formatNumber(ev)}</td></tr>`;
            }
            html+=`</tbody></table></div></div>`;
            resDiv.innerHTML=html;
        }
        resDiv.style.display='block';
        setTimeout(()=>resDiv.scrollIntoView({behavior:'smooth',block:'start'}),100);
    }
    function calcRtdResistance(t,r0,nsc){
        if(nsc==='pt1385'){
            let A=3.9083e-3, B=-5.775e-7, C=-4.183e-12;
            if(t>=0){ return r0*(1+A*t+B*t*t); }
            else { return r0*(1+A*t+B*t*t+C*(t-100)*t*t*t); }
        } else if(nsc==='pt1391'){
            let A=3.96847e-3, B=-5.84e-7;
            if(t>=0){ return r0*(1+A*t+B*t*t); }
            else { return r0*(1+A*t+B*t*t); }
        }
        return r0;
    }
    function calcCuResistance(t,r0,alpha){
        return r0*(1+alpha*t);
    }
    
// ===== NIST COEFFICIENTS LOADER =====
let nistCoefficients = null;

async function loadNistCoefficients() {
    if (nistCoefficients) return nistCoefficients;
    try {
        const response = await fetch('nist_coefficients.json');
        if (!response.ok) throw new Error('Failed to load NIST coefficients');
        nistCoefficients = await response.json();
        return nistCoefficients;
    } catch (error) {
        console.warn('[NIST] Failed to load coefficients, using fallback:', error);
        // Fallback to inline data (minimal set)
        nistCoefficients = {"K": {"name": "K (ТХА)", "type": "thermocouple", "ranges": [{"min": -270, "max": 0, "coefficients": [0, 0.039450128025, 2.3622373598e-05, -3.2858906784e-07, -4.9904828777e-09, -6.7509059173e-11, -5.7410327428e-13, -3.1088872894e-15, -1.0451609365e-17, -1.9889266878e-20, -1.6322697487e-23], "formula": "polynomial"}, {"min": 0, "max": 1372, "coefficients": [-0.017600413686, 0.038921204975, 1.8558770032e-05, -9.9457592874e-08, 3.1840945719e-10, -5.6072844889e-13, 5.6075059059e-16, -3.2020720003e-19, 9.7151147152e-23, -1.2104721275e-26], "formula": "polynomial_with_exponential", "exponential": {"a": 0.1185976, "b": -0.0001183432, "c": 126.9686}}]}, "J": {"name": "J (ТЖК)", "type": "thermocouple", "ranges": [{"min": -210, "max": 1200, "coefficients": [0, 0.050381187815, 3.047583693e-05, -8.568106672e-08, 1.3228195295e-10, -1.7052958337e-13, 2.0948090697e-16, -1.2538395336e-19, 1.5631725697e-23], "formula": "polynomial"}]}};
        return nistCoefficients;
    }
}

function calcTcVoltageFromNIST(t, type) {
    if (!nistCoefficients || !nistCoefficients[type]) {
        console.warn('[NIST] Coefficients not loaded for type:', type);
        return 0;
    }

    const tcData = nistCoefficients[type];
    let mv = 0;

    for (const range of tcData.ranges) {
        if (t >= range.min && t <= range.max) {
            const coeffs = range.coefficients;
            let p = 1;
            for (let i = 0; i < coeffs.length; i++) {
                mv += coeffs[i] * p;
                p *= t;
            }

            // Handle exponential correction for K-type
            if (range.exponential && t > 0) {
                mv += range.exponential.a * Math.exp(range.exponential.b * Math.pow(t - range.exponential.c, 2));
            }
            break;
        }
    }

    return mv;
}

function calcTcVoltage(t, type) {
    // Use loaded NIST coefficients if available
    if (nistCoefficients && nistCoefficients[type]) {
        return calcTcVoltageFromNIST(t, type);
    }

    // Fallback: inline minimal calculation for common types
    let mv = 0;
    if (type === 'K') {
        if (t < 0) {
            let c = [0, 3.9450128025e-2, 2.3622373598e-5, -3.2858906784e-7, -4.9904828777e-9, -6.7509059173e-11, -5.7410327428e-13, -3.1088872894e-15, -1.0451609365e-17, -1.9889266878e-20, -1.6322697487e-23];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [-1.7600413686e-2, 3.8921204975e-2, 1.8558770032e-5, -9.9457592874e-8, 3.1840945719e-10, -5.6072844889e-13, 5.6075059059e-16, -3.2020720003e-19, 9.7151147152e-23, -1.2104721275e-26];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
            mv += 1.185976e-1 * Math.exp(-1.183432e-4 * Math.pow(t - 1.269686e2, 2));
        }
    } else if (type === 'J') {
        let c = [0, 5.0381187815e-2, 3.0475836930e-5, -8.5681066720e-8, 1.3228195295e-10, -1.7052958337e-13, 2.0948090697e-16, -1.2538395336e-19, 1.5631725697e-23];
        let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
    } else if (type === 'T') {
        if (t >= 0) {
            let c = [0, 2.592800e-2, -7.602961e-4, 4.637791e-5, -2.165394e-6, 6.048144e-8, -7.293422e-10];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [0, 2.5949192e-2, -2.1316967e-3, 7.9018692e-5, -4.8277513e-6, -2.5705510e-7, 3.0990545e-8, -3.1776515e-9, 2.8555359e-10, -1.2743389e-11];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        }
    } else if (type === 'N') {
        if (t >= 0) {
            let c = [0, 2.592939e-2, -1.548991e-3, 3.575407e-5, -1.992859e-7, -1.801801e-8, 8.393395e-10, -1.728223e-11];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [0, 2.560682e-2, 1.497613e-4, -2.768767e-5, 2.816179e-6, -1.522396e-7, 3.601868e-9, -3.467403e-11];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        }
    } else if (type === 'E') {
        let c = [0, 5.8695844e-2, 5.7410995e-5, -8.930991e-8, 1.3393587e-10, -1.7022404e-13, 1.9416091e-16, -9.6391842e-20];
        let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
    } else if (type === 'R') {
        if (t >= 1064.18) {
            let c = [2.9515792e0, -2.5206125e-3, 1.5956440e-5, -7.6408590e-9, 2.0530520e-12, -2.9335960e-16];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [0, 5.289617e-3, 1.39111e-5, -2.388556e-8, 3.569160e-11, -4.623476e-14, 5.007774e-17, -3.731058e-20, 1.577164e-23];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        }
    } else if (type === 'S') {
        if (t >= 1064.18) {
            let c = [1.3290044e0, 3.3450931e-3, 6.5480519e-6, -1.6485626e-9, 1.2998961e-16];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [0, 5.4031331e-6, 1.2593429e-5, -2.3247797e-8, 3.2202882e-11, -3.3146520e-14, 2.5574425e-17, -1.2506887e-20, 2.7144318e-24];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        }
    } else if (type === 'B') {
        if (t >= 630.615) {
            let c = [-3.8938168e-2, 3.1019775e-4, -8.8627159e-8, 1.1295763e-11, -4.2789760e-16];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        } else {
            let c = [-2.4650818e-1, 4.2386323e-3, -3.7202336e-6, 5.8057311e-9, -5.1985638e-12, 3.0534464e-15];
            let p = 1; for (let i = 0; i < c.length; i++) { mv += c[i] * p; p *= t; }
        }
    }
    return mv;
}

    // DOMContentLoaded
    
    // Автоматический выключатель — адаптирован для КИП, АСУ ТП, малой мощности, 12-36 В
    const cbCableDataKip = {
        cu: {
            0.5: { Ik: 11, Imax: 6, desc: 'сигнальные цепи, датчики' },
            0.75: { Ik: 15, Imax: 10, desc: '4-20 мА, термопары, ТС' },
            1.0: { Ik: 17, Imax: 10, desc: 'питание 24 В DC, клапана' },
            1.5: { Ik: 23, Imax: 16, desc: 'группа приборов 220 В' },
            2.5: { Ik: 30, Imax: 25, desc: 'силовая линия, щит' },
            4: { Ik: 41, Imax: 32, desc: 'щит питания АСУ ТП' },
            6: { Ik: 50, Imax: 40, desc: 'главный ввод' }
        },
        al: {
            0.5: { Ik: 8, Imax: 4, desc: 'не рекомендуется для КИП' },
            0.75: { Ik: 11, Imax: 6, desc: 'не рекомендуется для КИП' },
            1.0: { Ik: 13, Imax: 10, desc: 'временные линии' },
            1.5: { Ik: 17, Imax: 10, desc: 'освещение' },
            2.5: { Ik: 23, Imax: 16, desc: 'силовая линия' },
            4: { Ik: 30, Imax: 25, desc: 'щит' },
            6: { Ik: 38, Imax: 32, desc: 'главный ввод' }
        }
    };
    const cbStandardSeriesKip = [0.5, 1, 2, 3, 4, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 63];
    const cbConsumerProfiles = {
        kip_resistive: { cosphi: 1.0, inrush: 1.0, desc: 'активная нагрузка' },
        kip_inductive: { cosphi: 0.7, inrush: 3.0, desc: 'клапана, реле, соленоиды' },
        asutp_controller: { cosphi: 0.95, inrush: 1.2, desc: 'контроллер + модули' },
        asutp_actuator: { cosphi: 0.75, inrush: 5.0, desc: 'исполнительные механизмы' },
        mixed: { cosphi: 0.85, inrush: 2.0, desc: 'смешанная нагрузка' },
        custom: { cosphi: null, inrush: null, desc: 'пользовательские параметры' }
    };
    const cbSupplyProfiles = {
        ac220: { U: 220, type: 'AC', desc: '~220 В' },
        dc24: { U: 24, type: 'DC', desc: '=24 В' },
        dc12: { U: 12, type: 'DC', desc: '=12 В' },
        dc36: { U: 36, type: 'DC', desc: '=36 В' },
        ac24: { U: 24, type: 'AC', desc: '~24 В' },
        ac36: { U: 36, type: 'AC', desc: '~36 В' },
        custom: { U: null, type: null, desc: 'своё' }
    };
    function getCbCableDataKip(lineType, customSection, customMaterial) {
        let preset = {
            signal_0_75: { mat: 'cu', sec: 0.75 },
            power_1_0: { mat: 'cu', sec: 1.0 },
            power_1_5: { mat: 'cu', sec: 1.5 },
            power_2_5: { mat: 'cu', sec: 2.5 }
        };
        let mat = lineType === 'custom' ? customMaterial : preset[lineType].mat;
        let sec = lineType === 'custom' ? parseFloat(customSection) : preset[lineType].sec;
        return { material: mat, section: sec, data: cbCableDataKip[mat][sec] };
    }
    function nearestCbStandardKip(val) {
        for (let i = 0; i < cbStandardSeriesKip.length; i++) {
            if (cbStandardSeriesKip[i] >= val) return cbStandardSeriesKip[i];
        }
        return cbStandardSeriesKip[cbStandardSeriesKip.length - 1];
    }
    function updateCbForm() {
        let loadType = document.getElementById('cb_load_type').value;
        document.getElementById('cb_power_block').style.display = loadType === 'power' ? 'block' : 'none';
        document.getElementById('cb_current_block').style.display = loadType === 'current' ? 'block' : 'none';
        let supply = document.getElementById('cb_supply_type').value;
        document.getElementById('cb_custom_voltage_block').style.display = supply === 'custom' ? 'block' : 'none';
    }
    function updateCbCosPhi() {
        let consumer = document.getElementById('cb_consumer_type').value;
        document.getElementById('cb_custom_cosphi_block').style.display = consumer === 'custom' ? 'block' : 'none';
    }
    function updateCbCableTable() {
        let lineType = document.getElementById('cb_line_type').value;
        document.getElementById('cb_custom_cable').style.display = lineType === 'custom' ? 'block' : 'none';
    }
    function calcCircuitBreaker() {
        let supplyType = document.getElementById('cb_supply_type').value;
        let loadType = document.getElementById('cb_load_type').value;
        let consumerType = document.getElementById('cb_consumer_type').value;
        let lineType = document.getElementById('cb_line_type').value;
        let curve = document.getElementById('cb_curve').value;
        let deviceCount = parseInt(document.getElementById('cb_device_count').value) || 1;
        let customSection = document.getElementById('cb_cable_section') ? document.getElementById('cb_cable_section').value : '0.75';
        let customMaterial = document.getElementById('cb_cable_material') ? document.getElementById('cb_cable_material').value : 'cu';

        // Supply profile
        let supply = cbSupplyProfiles[supplyType];
        let U;
        if (supplyType === 'custom') {
            U = parseFloat(document.getElementById('cb_custom_voltage').value);
            if (isNaN(U) || U <= 0) { showToast('Введите напряжение питания'); return; }
        } else {
            U = supply.U;
        }

        // Consumer profile
        let consumer = cbConsumerProfiles[consumerType];
        let cosphi, inrush;
        if (consumerType === 'custom') {
            cosphi = parseFloat(document.getElementById('cb_custom_cosphi').value);
            inrush = parseFloat(document.getElementById('cb_inrush_factor').value);
            if (isNaN(cosphi) || cosphi <= 0 || cosphi > 1) { showToast('cos φ должен быть 0,1…1,0'); return; }
            if (isNaN(inrush) || inrush < 1) { showToast('Кпуск ≥ 1,0'); return; }
        } else {
            cosphi = consumer.cosphi;
            inrush = consumer.inrush;
        }

        // Calculate current
        let Icalc;
        if (loadType === 'power') {
            let P = parseFloat(document.getElementById('cb_power').value);
            let unitMult = parseFloat(document.getElementById('cb_power_unit').value);
            if (isNaN(P) || P <= 0) { showToast('Введите мощность'); return; }
            P = P * unitMult * deviceCount;
            Icalc = P / (U * cosphi);
        } else {
            Icalc = parseFloat(document.getElementById('cb_current').value);
            if (isNaN(Icalc) || Icalc <= 0) { showToast('Введите ток'); return; }
            Icalc = Icalc * deviceCount;
        }

        // Cable data
        let cable = getCbCableDataKip(lineType, customSection, customMaterial);
        let In_min = Icalc * 1.25; // Запас 25% для КИП
        let Ina = nearestCbStandardKip(In_min);
        let Ina_inrush = nearestCbStandardKip(Icalc * inrush / (curve === 'B' ? 3 : curve === 'C' ? 5 : curve === 'D' ? 10 : 2));
        if (Ina_inrush > Ina) Ina = Ina_inrush;

        let warning = '';
        if (Ina > cable.data.Imax) {
            warning = `Выбранный автомат ${Ina} А превышает допустимый ток для кабеля ${cable.section} мм² (${cable.data.Imax} А). Увеличьте сечение кабеля.`;
        }
        if (Ina < 0.5) {
            warning += (warning ? '<br>' : '') + `Расчётный ток ${formatNumber(Icalc)} А очень мал. Рекомендуется применять предохранители или защиту в составе БП.`;
        }

        let Pmax = Ina * U * cosphi;
        let I_inrush = Icalc * inrush;

        let html = '<div class="converter-result-label-title">Результаты расчёта (КИП и А / АСУ ТП)</div>';
        html += `<div class="converter-result-item"><span class="converter-result-label">Напряжение питания</span><span class="converter-result-value">${supplyType === 'custom' ? (document.getElementById('cb_custom_voltage_type').value === 'dc' ? '=' : '~') + U + ' В' : supply.desc}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Тип нагрузки</span><span class="converter-result-value">${consumer.desc}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">cos φ / Кпуск</span><span class="converter-result-value">${cosphi} / ${inrush}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расчётный ток Iр</span><span class="converter-result-value">${formatNumber(Icalc)} А</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Пусковой ток Iпуск</span><span class="converter-result-value">${formatNumber(I_inrush)} А</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Кабель</span><span class="converter-result-value">${cable.material === 'cu' ? 'медь' : 'алюминий'} ${cable.section} мм² · ${cable.data.Imax} А · ${cable.data.desc}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Макс. автомат для кабеля</span><span class="converter-result-value">${cable.data.Imax} А</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Рекомендуемый автомат</span><span class="converter-result-value" style="color:#4ac771; font-size:18px;">${curve}${Ina}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Макс. мощность</span><span class="converter-result-value">${formatNumber(Pmax)} Вт (${formatNumber(Pmax/1000)} кВт)</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Количество приборов</span><span class="converter-result-value">${deviceCount} шт.</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">I = P/(U·cos φ) · Кзапаса 1,25</span></div>`;

        if (warning) {
            html += `<div class="warning-banner" style="margin:10px 0 0;"><div class="warning-icon"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div><div class="warning-banner-content"><div class="warning-banner-title">Рекомендации</div><div class="warning-banner-desc">${warning}</div></div></div>`;
        }

        document.getElementById('cbResults').innerHTML = html;
        document.getElementById('cbResults').style.display = 'block';
        setTimeout(() => document.getElementById('cbResults').scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }

    // ===== СУЖАЮЩЕЕ УСТРОЙСТВО (ДИАФРАГМА) — вспомогательные функции =====
    const opAlphaCoefficients = {
        orifice: { A: 0.5959, B: 0.0312, C: -0.1840, D: 0.0390 },
        nozzle: { A: 0.9965, B: 0.0105, C: -0.0420, D: 0.0085 },
        venturi: { A: 0.9840, B: 0.0050, C: -0.0150, D: 0.0030 }
    };
    const opThermalExpansion = {
        steel20: 11.9e-6,
        steel12x18h10t: 16.6e-6,
        steel15x5m: 11.5e-6,
        brass: 18.9e-6,
        bronze: 17.6e-6
    };
    function updateOpForm() {
        let type = document.getElementById('op_medium_type');
        if (type) {
            let gasParams = document.getElementById('op_gas_params');
            if (gasParams) gasParams.style.display = type.value === 'gas' ? 'block' : 'none';
        }
    }
    function updateOpDpForm() {
        let type = document.getElementById('op_dp_medium_type');
        if (type) {
            let gasParams = document.getElementById('op_dp_gas_params');
            if (gasParams) gasParams.style.display = type.value === 'gas' ? 'block' : 'none';
        }
    }
    function updateOpFlowForm() {
        let type = document.getElementById('op_flow_medium_type');
        if (type) {
            let gasParams = document.getElementById('op_flow_gas_params');
            if (gasParams) gasParams.style.display = type.value === 'gas' ? 'block' : 'none';
        }
    }
    function getOpAlpha(m, device) {
        let coeff = opAlphaCoefficients[device];
        return coeff.A + coeff.B * m + coeff.C * m * m + coeff.D * m * m * m;
    }
    function getOpEpsilon(m, dp_Pa, pressure_abs, kappa, medium) {
        if (medium !== 'gas') return 1.0;
        let tau = dp_Pa / pressure_abs;
        let eps = 1 - (0.41 + 0.35 * Math.pow(m, 1.5)) * tau / kappa;
        return eps < 0.9 ? 0.9 : eps;
    }
    function convertOpFlowToM3s(flow, unit, rho) {
        switch(unit) {
            case 'm3h': return flow / 3600;
            case 'm3s': return flow;
            case 'l_s': return flow / 1000;
            case 'kg_h': return flow / (3600 * rho);
            case 'kg_s': return flow / rho;
            case 't_h': return flow * 1000 / (3600 * rho);
            default: return flow / 3600;
        }
    }
    function convertOpDpToPa(dp, unit) {
        switch(unit) {
            case 'kPa': return dp * 1000;
            case 'Pa': return dp;
            case 'MPa': return dp * 1e6;
            case 'mmH2O': return dp * 9.80665;
            case 'mmHg': return dp * 133.322;
            case 'bar': return dp * 1e5;
            default: return dp * 1000;
        }
    }
    function getOpThermalD(d20_mm, material, temp) {
        let alpha = opThermalExpansion[material] || 11.9e-6;
        return d20_mm / 1000 * (1 + alpha * (temp - 20));
    }

    // Расчёт перепада давления Δp по Q и d₂₀
    function calcOrificeDp() {
        let medium = document.getElementById('op_dp_medium_type').value;
        let d20_mm = parseFloat(document.getElementById('op_dp_d20').value);
        let pipeMat = document.getElementById('op_dp_pipe_material').value;
        let temp = parseFloat(document.getElementById('op_dp_temp').value);
        let flow = parseFloat(document.getElementById('op_dp_flow').value);
        let flowUnit = document.getElementById('op_dp_flow_unit').value;
        let d_plate_mm = parseFloat(document.getElementById('op_dp_d_plate').value);
        let rho = parseFloat(document.getElementById('op_dp_density').value);
        let nu_cSt = parseFloat(document.getElementById('op_dp_viscosity').value);
        let device = document.getElementById('op_dp_device_type').value;
        let plateMat = document.getElementById('op_dp_plate_material').value;
        let pressure = parseFloat(document.getElementById('op_dp_pressure').value) || 0;

        if (isNaN(d20_mm) || d20_mm <= 0) { showToast('Введите диаметр трубопровода'); return; }
        if (isNaN(flow) || flow <= 0) { showToast('Введите расход'); return; }
        if (isNaN(d_plate_mm) || d_plate_mm <= 0) { showToast('Введите диаметр диска'); return; }
        if (isNaN(rho) || rho <= 0) { showToast('Введите плотность'); return; }
        if (isNaN(nu_cSt) || nu_cSt <= 0) { showToast('Введите вязкость'); return; }
        if (d_plate_mm >= d20_mm) { showToast('Диаметр диска должен быть меньше диаметра трубы'); return; }

        let D = getOpThermalD(d20_mm, pipeMat, temp);
        let d = d_plate_mm / 1000 * (1 + (opThermalExpansion[plateMat] || 16.6e-6) * (temp - 20));
        let m = (d / D) * (d / D);
        let Q_m3s = convertOpFlowToM3s(flow, flowUnit, rho);
        let alpha = getOpAlpha(m, device);
        let kappa = medium === 'gas' ? (parseFloat(document.getElementById('op_dp_kappa').value) || 1.4) : 1.0;
        let Z = medium === 'gas' ? (parseFloat(document.getElementById('op_dp_z').value) || 1.0) : 1.0;
        let pressure_abs = pressure * 1e6 + 101325;

        let epsilon = getOpEpsilon(m, 25000, pressure_abs, kappa, medium);
        let dp_Pa;
        for (let iter = 0; iter < 20; iter++) {
            let denom = alpha * epsilon * (Math.PI * D * D / 4) * Math.sqrt(2 / rho) * m;
            dp_Pa = Math.pow(Q_m3s / denom, 2);
            let eps_new = getOpEpsilon(m, dp_Pa, pressure_abs, kappa, medium);
            if (Math.abs(eps_new - epsilon) < 0.0001) break;
            epsilon = eps_new;
        }

        let ReD = (4 * Q_m3s) / (Math.PI * D * nu_cSt * 1e-6);
        let dp_kPa = dp_Pa / 1000;
        let dp_mmH2O = dp_Pa / 9.80665;

        let warnings = [];
        if (m < 0.05) warnings.push('m < 0,05 — ниже рекомендуемого диапазона');
        if (m > 0.64) warnings.push('m > 0,64 — превышает рекомендуемый диапазон');
        if (ReD < 1e5) warnings.push('ReD < 10⁵ — возможна зависимость α от Re');
        if (dp_Pa > 0.25 * pressure_abs) warnings.push('Δp > 0,25·P — применение формулы ограничено');

        let deviceNames = { orifice: 'Диафрагма стандартная', nozzle: 'Сопло стандартное', venturi: 'Труба Вентури' };
        let html = '<div class="converter-result-label-title">Результаты расчёта Δp (РД 50-411-83)</div>';
        html += `<div class="converter-result-item"><span class="converter-result-label">Тип СУ</span><span class="converter-result-value">${deviceNames[device]}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расход Q</span><span class="converter-result-value">${formatNumber(Q_m3s * 3600)} м³/ч</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Диаметр диска d₂₀</span><span class="converter-result-value">${formatNumber(d_plate_mm)} мм</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Относительное отверстие m</span><span class="converter-result-value">${formatNumber(m)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расхода α</span><span class="converter-result-value">${formatNumber(alpha)}</span></div>`;
        if (medium === 'gas') {
            html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расширения ε</span><span class="converter-result-value">${formatNumber(epsilon)}</span></div>`;
        }
        html += `<div class="converter-result-item"><span class="converter-result-label">Число ReD</span><span class="converter-result-value">${formatNumber(ReD)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Перепад Δp</span><span class="converter-result-value" style="color:#4ac771; font-size:18px;">${formatNumber(dp_kPa)} кПа</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Перепад Δp</span><span class="converter-result-value">${formatNumber(dp_mmH2O)} мм вод.ст.</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Перепад Δp</span><span class="converter-result-value">${formatNumber(dp_Pa)} Па</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">Δp = ρ/2 · [Q/(α·ε·(πD²/4)·m)]²</span></div>`;

        if (warnings.length > 0) {
            html += `<div class="warning-banner" style="margin:10px 0 0;"><div class="warning-icon"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div><div class="warning-banner-content"><div class="warning-banner-title">Рекомендации</div><div class="warning-banner-desc">${warnings.join('<br>')}</div></div></div>`;
        }

        document.getElementById('opResultsDp').innerHTML = html;
        document.getElementById('opResultsDp').style.display = 'block';
        setTimeout(() => document.getElementById('opResultsDp').scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }

    // Расчёт расхода Q по Δp и d₂₀
    function calcOrificeFlow() {
        let medium = document.getElementById('op_flow_medium_type').value;
        let d20_mm = parseFloat(document.getElementById('op_flow_d20').value);
        let pipeMat = document.getElementById('op_flow_pipe_material').value;
        let temp = parseFloat(document.getElementById('op_flow_temp').value);
        let dp = parseFloat(document.getElementById('op_flow_dp').value);
        let dpUnit = document.getElementById('op_flow_dp_unit').value;
        let d_plate_mm = parseFloat(document.getElementById('op_flow_d_plate').value);
        let rho = parseFloat(document.getElementById('op_flow_density').value);
        let nu_cSt = parseFloat(document.getElementById('op_flow_viscosity').value);
        let device = document.getElementById('op_flow_device_type').value;
        let plateMat = document.getElementById('op_flow_plate_material').value;
        let pressure = parseFloat(document.getElementById('op_flow_pressure').value) || 0;

        if (isNaN(d20_mm) || d20_mm <= 0) { showToast('Введите диаметр трубопровода'); return; }
        if (isNaN(dp) || dp <= 0) { showToast('Введите перепад давления'); return; }
        if (isNaN(d_plate_mm) || d_plate_mm <= 0) { showToast('Введите диаметр диска'); return; }
        if (isNaN(rho) || rho <= 0) { showToast('Введите плотность'); return; }
        if (isNaN(nu_cSt) || nu_cSt <= 0) { showToast('Введите вязкость'); return; }
        if (d_plate_mm >= d20_mm) { showToast('Диаметр диска должен быть меньше диаметра трубы'); return; }

        let D = getOpThermalD(d20_mm, pipeMat, temp);
        let d = d_plate_mm / 1000 * (1 + (opThermalExpansion[plateMat] || 16.6e-6) * (temp - 20));
        let m = (d / D) * (d / D);
        let dp_Pa = convertOpDpToPa(dp, dpUnit);
        let alpha = getOpAlpha(m, device);
        let kappa = medium === 'gas' ? (parseFloat(document.getElementById('op_flow_kappa').value) || 1.4) : 1.0;
        let Z = medium === 'gas' ? (parseFloat(document.getElementById('op_flow_z').value) || 1.0) : 1.0;
        let pressure_abs = pressure * 1e6 + 101325;
        let epsilon = getOpEpsilon(m, dp_Pa, pressure_abs, kappa, medium);

        let Q_m3s = alpha * epsilon * (Math.PI * D * D / 4) * Math.sqrt(2 * dp_Pa / rho) * m;
        let ReD = (4 * Q_m3s) / (Math.PI * D * nu_cSt * 1e-6);

        let warnings = [];
        if (m < 0.05) warnings.push('m < 0,05 — ниже рекомендуемого диапазона');
        if (m > 0.64) warnings.push('m > 0,64 — превышает рекомендуемый диапазон');
        if (ReD < 1e5) warnings.push('ReD < 10⁵ — возможна зависимость α от Re');
        if (dp_Pa > 0.25 * pressure_abs) warnings.push('Δp > 0,25·P — применение формулы ограничено');

        let deviceNames = { orifice: 'Диафрагма стандартная', nozzle: 'Сопло стандартное', venturi: 'Труба Вентури' };
        let html = '<div class="converter-result-label-title">Результаты расчёта Q (РД 50-411-83)</div>';
        html += `<div class="converter-result-item"><span class="converter-result-label">Тип СУ</span><span class="converter-result-value">${deviceNames[device]}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Перепад Δp</span><span class="converter-result-value">${formatNumber(dp_Pa / 1000)} кПа</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Диаметр диска d₂₀</span><span class="converter-result-value">${formatNumber(d_plate_mm)} мм</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Относительное отверстие m</span><span class="converter-result-value">${formatNumber(m)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расхода α</span><span class="converter-result-value">${formatNumber(alpha)}</span></div>`;
        if (medium === 'gas') {
            html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расширения ε</span><span class="converter-result-value">${formatNumber(epsilon)}</span></div>`;
        }
        html += `<div class="converter-result-item"><span class="converter-result-label">Число ReD</span><span class="converter-result-value">${formatNumber(ReD)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расход Q</span><span class="converter-result-value" style="color:#4ac771; font-size:18px;">${formatNumber(Q_m3s * 3600)} м³/ч</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расход Q</span><span class="converter-result-value">${formatNumber(Q_m3s)} м³/с</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расход Q</span><span class="converter-result-value">${formatNumber(Q_m3s * 1000)} л/с</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Массовый расход</span><span class="converter-result-value">${formatNumber(Q_m3s * rho * 3600)} кг/ч</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">Q = α·ε·(πD²/4)·√(2Δp/ρ)·m</span></div>`;

        if (warnings.length > 0) {
            html += `<div class="warning-banner" style="margin:10px 0 0;"><div class="warning-icon"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div><div class="warning-banner-content"><div class="warning-banner-title">Рекомендации</div><div class="warning-banner-desc">${warnings.join('<br>')}</div></div></div>`;
        }

        document.getElementById('opResultsFlow').innerHTML = html;
        document.getElementById('opResultsFlow').style.display = 'block';
        setTimeout(() => document.getElementById('opResultsFlow').scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }

    // Расчёт диаметра диска d₂₀ по Q и Δp
    function calcOrificeDiameter() {
        let medium = document.getElementById('op_medium_type').value;
        let d20 = parseFloat(document.getElementById('op_d20').value);
        let dUnit = document.getElementById('op_d_unit').value;
        let pipeMat = document.getElementById('op_pipe_material').value;
        let temp = parseFloat(document.getElementById('op_temp').value);
        let flow = parseFloat(document.getElementById('op_flow').value);
        let flowUnit = document.getElementById('op_flow_unit').value;
        let flowMin = parseFloat(document.getElementById('op_flow_min').value);
        let pressure = parseFloat(document.getElementById('op_pressure').value);
        let rho = parseFloat(document.getElementById('op_density').value);
        let nu_cSt = parseFloat(document.getElementById('op_viscosity').value);
        let dp = parseFloat(document.getElementById('op_dp').value);
        let dpUnit = document.getElementById('op_dp_unit').value;
        let device = document.getElementById('op_device_type').value;
        let plateMat = document.getElementById('op_plate_material').value;

        if (isNaN(d20) || d20 <= 0) { showToast('Введите диаметр трубопровода'); return; }
        if (isNaN(flow) || flow <= 0) { showToast('Введите расход'); return; }
        if (isNaN(rho) || rho <= 0) { showToast('Введите плотность'); return; }
        if (isNaN(dp) || dp <= 0) { showToast('Введите перепад давления'); return; }
        if (isNaN(nu_cSt) || nu_cSt <= 0) { showToast('Введите вязкость'); return; }

        let D20_m = dUnit === 'mm' ? d20 / 1000 : d20;
        let Q_m3s = convertOpFlowToM3s(flow, flowUnit, rho);
        let dp_Pa = convertOpDpToPa(dp, dpUnit);
        let alpha_pipe = opThermalExpansion[pipeMat] || 11.9e-6;
        let alpha_plate = opThermalExpansion[plateMat] || 16.6e-6;
        let kt_pipe = 1 + alpha_pipe * (temp - 20);
        let kt_plate = 1 + alpha_plate * (temp - 20);
        let D = D20_m * kt_pipe;
        let coeff = opAlphaCoefficients[device];
        let kappa = medium === 'gas' ? (parseFloat(document.getElementById('op_kappa').value) || 1.4) : 1.0;
        let Z = medium === 'gas' ? (parseFloat(document.getElementById('op_z').value) || 1.0) : 1.0;
        let pressure_abs = pressure * 1e6 + 101325;

        let m = 0.25;
        let alpha, epsilon = 1.0;
        let Q_calc;
        let iter;
        for (iter = 0; iter < 50; iter++) {
            alpha = coeff.A + coeff.B * m + coeff.C * m * m + coeff.D * m * m * m;
            if (medium === 'gas') {
                let tau = dp_Pa / pressure_abs;
                epsilon = 1 - (0.41 + 0.35 * Math.pow(m, 1.5)) * tau / kappa;
                if (epsilon < 0.9) epsilon = 0.9;
            }
            Q_calc = alpha * epsilon * (Math.PI * D * D / 4) * Math.sqrt(2 * dp_Pa / rho) * m;
            let err = (Q_calc - Q_m3s) / Q_m3s;
            if (Math.abs(err) < 0.0001) break;
            m = m * (1 - err * 0.5);
            if (m < 0.02) m = 0.02;
            if (m > 0.70) m = 0.70;
        }

        let d = D * Math.sqrt(m);
        let d20_calc = d / kt_plate;
        let d_mm = d20_calc * 1000;
        let ReD = (4 * Q_m3s) / (Math.PI * D * nu_cSt * 1e-6);
        let ReD_min = ReD * (flowMin / flow);

        let warnings = [];
        if (m < 0.05) warnings.push('m < 0,05 — ниже рекомендуемого диапазона');
        if (m > 0.64) warnings.push('m > 0,64 — превышает рекомендуемый диапазон');
        if (ReD < 1e5) warnings.push('ReD < 10⁵ — возможна зависимость α от Re');
        if (d20_calc / D20_m > 0.8) warnings.push('d₂₀/D₂₀ > 0,8 — проверьте условия установки');
        if (flowMin / flow < 0.3) warnings.push('Qₘᵢₙ/Q < 0,3 — возможна недостаточная точность на малых расходах');

        let deviceNames = { orifice: 'Диафрагма стандартная', nozzle: 'Сопло стандартное', venturi: 'Труба Вентури' };
        let html = '<div class="converter-result-label-title">Результаты расчёта d₂₀ (РД 50-411-83)</div>';
        html += `<div class="converter-result-item"><span class="converter-result-label">Тип СУ</span><span class="converter-result-value">${deviceNames[device]}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Диаметр трубы D₂₀</span><span class="converter-result-value">${formatNumber(d20)} ${dUnit}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Рабочий диаметр D</span><span class="converter-result-value">${formatNumber(D * 1000)} мм</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Расход Q</span><span class="converter-result-value">${formatNumber(Q_m3s * 3600)} м³/ч</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Перепад Δp</span><span class="converter-result-value">${formatNumber(dp_Pa / 1000)} кПа</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Относительное отверстие m</span><span class="converter-result-value">${formatNumber(m)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расхода α</span><span class="converter-result-value">${formatNumber(alpha)}</span></div>`;
        if (medium === 'gas') {
            html += `<div class="converter-result-item"><span class="converter-result-label">Коэффициент расширения ε</span><span class="converter-result-value">${formatNumber(epsilon)}</span></div>`;
        }
        html += `<div class="converter-result-item"><span class="converter-result-label">Число ReD (ном.)</span><span class="converter-result-value">${formatNumber(ReD)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Число ReD (мин.)</span><span class="converter-result-value">${formatNumber(ReD_min)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Диаметр отверстия d₂₀</span><span class="converter-result-value" style="color:#4ac771; font-size:18px;">${formatNumber(d_mm)} мм</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Отношение d₂₀/D₂₀</span><span class="converter-result-value">${formatNumber(d20_calc / D20_m)}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Итераций</span><span class="converter-result-value">${iter}</span></div>`;
        html += `<div class="converter-result-item"><span class="converter-result-label">Формула</span><span class="converter-result-value">Q = α·ε·(πD²/4)·√(2Δp/ρ)·m</span></div>`;

        if (warnings.length > 0) {
            html += `<div class="warning-banner" style="margin:10px 0 0;"><div class="warning-icon"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div><div class="warning-banner-content"><div class="warning-banner-title">Рекомендации</div><div class="warning-banner-desc">${warnings.join('<br>')}</div></div></div>`;
        }

        document.getElementById('opResultsDiameter').innerHTML = html;
        document.getElementById('opResultsDiameter').style.display = 'block';
        setTimeout(() => document.getElementById('opResultsDiameter').scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }

    document.addEventListener('DOMContentLoaded', function(){
        setSignalDefaults();
        setScaleDefaults();
        setLiquidDensity();
        updateBuoySignalUnit();
        if(document.getElementById('rtd_group')) updateRtdTypeOptions();
        if(document.getElementById('tc_type')) updateTcRanges();
        setCalibMethodOnForm();
        let firstActive=document.querySelector('.page-content.active');
        if(firstActive) { requestAnimationFrame(()=>firstActive.classList.add('visible')); updateBottomNavActive(firstActive.id.replace('page-','')); }
        let appHeader = document.querySelector('.app-header');
        if(appHeader && firstActive) appHeader.style.display = (firstActive.id === 'page-dashboard') ? 'block' : 'none';
    
    // Preload NIST coefficients for thermocouple calculations
    loadNistCoefficients().catch(err => console.warn('[NIST] Preload failed:', err));
});

    // Theme toggle functionality
    function toggleTheme() {
        let currentTheme = SafeStorage.getItem('app-theme') || 'dark';
        let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        SafeStorage.setItem('app-theme', newTheme);
        updateThemeLabel();
    }

    function updateThemeLabel() {
        let label = document.getElementById('themeLabel');
        if (label) {
            let currentTheme = SafeStorage.getItem('app-theme') || 'dark';
            label.textContent = currentTheme === 'dark' ? 'Светлая тема' : 'Тёмная тема';
        }
    }

    // Apply saved theme on load
    (function() {
        let savedTheme = SafeStorage.getItem('app-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeLabel();
    })();