#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 393 — ПЕРЕНОС из kip8test (cb4f6b0) в БОЕВОЙ kip8: карточка
# работника страницы «Работники» — ЧЕТЫРЕ блока-окна .ws-wcard +
# ШРИФТ КРУПНЕЕ; попап карточки у сетки — прежний компактный вид.
# Правки index.html — зеркально kip8test (якоря выверены, все x1).
import io
import sys

s = io.open('index.html', encoding='utf-8').read()
orig_len = len(s)
n_ok = 0

def rep(old, new):
    global s, n_ok
    n = s.count(old)
    if n != 1:
        print('  !! якорь x%d: %r...' % (n, old[:70]))
        sys.exit(1)
    s = s.replace(old, new)
    n_ok += 1

# ---------- JS: _renderWorkerCard — сигнатура, «не найден», блоки ----------
rep("""        // Task 385: ПОЛНАЯ КАРТОЧКА РАБОТНИКА — общий рендер: попап
        // шахматки (withEdit=false — чистая информация) и страница
        // «Работники» (withEdit=true — «Правка данных…», «Уволить…»,""",
"""        // Task 393: asBlocks=true — вернуть МАССИВ из 4 блоков
        // (профиль+действия / отпуска / мероприятия / СИЗ) для
        // _renderWorkerCardPanels (страница «Работники» — каждый
        // блок ОТДЕЛЬНЫМ окном .ws-wcard); без флага — склеенная
        // строка (попап шахматки, прежний сплошной вид)
        // Task 385: ПОЛНАЯ КАРТОЧКА РАБОТНИКА — общий рендер: попап
        // шахматки (withEdit=false — чистая информация) и страница
        // «Работники» (withEdit=true — «Правка данных…», «Уволить…»,""")

rep("""        _renderWorkerCard: function(tabNo, withEdit) {
            var emp = null;""",
"""        _renderWorkerCard: function(tabNo, withEdit, asBlocks) {
            var emp = null;""")

rep("""            if (!emp) {
                return '<div class="ws-popup-title">таб. №' +
                       this._esc(tabNo) + ' — не найден</div>';
            }""",
"""            if (!emp) {
                var miss = '<div class="ws-popup-title">таб. №' +
                           this._esc(tabNo) + ' — не найден</div>';
                // Task 393: asBlocks — массив и для «не найден» (1 блок)
                return asBlocks ? [miss] : miss;
            }""")

rep("""            var html = '<div class="ws-popup-title">' + this._esc(emp['ФИО']) +
                       ' · таб. №' + this._esc(emp['таб_номер']) + '</div>';""",
"""            // Task 393: карточка собирается ЧЕТЫРЬМЯ блоками — b1
            // профиль+действия, b2 отпуска, b3 мероприятия, b4 СИЗ;
            // склейка/массив — в возврате метода (см. ниже)
            var b1 = '<div class="ws-popup-title">' + this._esc(emp['ФИО']) +
                     ' · таб. №' + this._esc(emp['таб_номер']) + '</div>';""")

rep("""                html += '<div class="ws-emp-field"><span class="ws-emp-k">' +
                        this._esc(fields[fi][0]) + '</span><span class="ws-emp-v">' +
                        this._esc(fields[fi][1]) + '</span></div>';""",
"""                b1 += '<div class="ws-emp-field"><span class="ws-emp-k">' +
                      this._esc(fields[fi][0]) + '</span><span class="ws-emp-v">' +
                      this._esc(fields[fi][1]) + '</span></div>';""")

rep("""            if (withEdit) {
                html += '<div class="ws-popup-row ws-popup-more ws-emp-editdata"' +
                        ' title="Правка данных работника: ФИО, режим, должность…"' +
                        ' onclick="WorkSchedule.openEmpEditForm(\\'' +
                        this._esc(String(emp['таб_номер'] || '')) + '\\')">Правка данных…</div>';
            }""",
"""            if (withEdit) {
                b1 += '<div class="ws-popup-row ws-popup-more ws-emp-editdata"' +
                      ' title="Правка данных работника: ФИО, режим, должность…"' +
                      ' onclick="WorkSchedule.openEmpEditForm(\\'' +
                      this._esc(String(emp['таб_номер'] || '')) + '\\')">Правка данных…</div>';
            }""")

rep("""            if (withEdit) {
                html += '<div class="ws-popup-row ws-popup-more ws-emp-dismiss"' +
                        ' title="Увольнение: записать дату, убрать из графика"' +
                        ' onclick="WorkSchedule.openDismissForm(\\'' +
                        this._esc(String(emp['таб_номер'] || '')) + '\\')">Уволить…</div>';
            }""",
"""            if (withEdit) {
                b1 += '<div class="ws-popup-row ws-popup-more ws-emp-dismiss"' +
                      ' title="Увольнение: записать дату, убрать из графика"' +
                      ' onclick="WorkSchedule.openDismissForm(\\'' +
                      this._esc(String(emp['таб_номер'] || '')) + '\\')">Уволить…</div>';
            }""")

rep("""            html += '<div class="ws-popup-sec">Отпуска · ' + this._year + '</div>';
            if (!vacs.length) {
                html += '<div class="ws-emp-empty">нет запланированных периодов</div>';""",
"""            var b2 = '<div class="ws-popup-sec">Отпуска · ' + this._year + '</div>';
            if (!vacs.length) {
                b2 += '<div class="ws-emp-empty">нет запланированных периодов</div>';""")

rep("""                    html += '<div class="ws-emp-field"><span class="ws-emp-k">Часть ' +
                            (pNo ? pNo : '—') + '</span><span class="ws-emp-v">' +
                            this._fmtDateRu(vv.дата_начала) + ' — ' +
                            this._fmtDateRu(vv.дата_окончания) + ' · ' +
                            vNet + ' ' + this._plural(vNet, ['день', 'дня', 'дней']) +
                            (vCal > vNet ? ' (−' + (vCal - vNet) + ' праздн.)' : '') +
                            (String(vv.комментарий || '').trim()
                                ? ' · «' + this._esc(vv.комментарий) + '»' : '') +
                            '</span>' + vActs + '</div>';""",
"""                    b2 += '<div class="ws-emp-field"><span class="ws-emp-k">Часть ' +
                          (pNo ? pNo : '—') + '</span><span class="ws-emp-v">' +
                          this._fmtDateRu(vv.дата_начала) + ' — ' +
                          this._fmtDateRu(vv.дата_окончания) + ' · ' +
                          vNet + ' ' + this._plural(vNet, ['день', 'дня', 'дней']) +
                          (vCal > vNet ? ' (−' + (vCal - vNet) + ' праздн.)' : '') +
                          (String(vv.комментарий || '').trim()
                              ? ' · «' + this._esc(vv.комментарий) + '»' : '') +
                          '</span>' + vActs + '</div>';""")

rep("""            if (withEdit) {
                html += '<div class="ws-popup-row ws-popup-more ws-emp-addvac"' +
                        ' title="Добавить период отпуска этому работнику"' +
                        ' onclick="WorkSchedule.onEmpAddVacation(\\'' +
                        this._esc(String(emp['таб_номер'] || '')) + '\\')">+ Отпуск…</div>';
            }""",
"""            if (withEdit) {
                b2 += '<div class="ws-popup-row ws-popup-more ws-emp-addvac"' +
                      ' title="Добавить период отпуска этому работнику"' +
                      ' onclick="WorkSchedule.onEmpAddVacation(\\'' +
                      this._esc(String(emp['таб_номер'] || '')) + '\\')">+ Отпуск…</div>';
            }""")

rep("""            html += '<div class="ws-popup-sec">Мероприятия · ' +
                    monthNames[this._month - 1] + ' ' + this._year + '</div>';
            if (!trs.length) {
                html += '<div class="ws-emp-empty">нет мероприятий в месяце</div>';""",
"""            var b3 = '<div class="ws-popup-sec">Мероприятия · ' +
                     monthNames[this._month - 1] + ' ' + this._year + '</div>';
            if (!trs.length) {
                b3 += '<div class="ws-emp-empty">нет мероприятий в месяце</div>';""")

rep("""                    html += '<div class="ws-popup-row ws-popup-event">' +
                            '<span class="ws-popup-swatch" style="background:' +
                            (meta.color || '#3a3a3a') + ';"></span>' +
                            '<span class="ws-popup-code">' + this._esc(code || '—') + '</span>' +
                            '<span class="ws-popup-name">' +
                            this._esc(t.тема || meta.name || t.тип) +
                            ' · ' + period + '</span>' + acts + '</div>';""",
"""                    b3 += '<div class="ws-popup-row ws-popup-event">' +
                          '<span class="ws-popup-swatch" style="background:' +
                          (meta.color || '#3a3a3a') + ';"></span>' +
                          '<span class="ws-popup-code">' + this._esc(code || '—') + '</span>' +
                          '<span class="ws-popup-name">' +
                          this._esc(t.тема || meta.name || t.тип) +
                          ' · ' + period + '</span>' + acts + '</div>';""")

rep("""            if (withEdit) {
                html += '<div class="ws-popup-row ws-popup-more ws-emp-addtr"' +
                        ' title="Добавить мероприятие этому работнику"' +
                        ' onclick="WorkSchedule.onEmpAddTraining(\\'' +
                        this._esc(String(emp['таб_номер'] || '')) + '\\')">+ Мероприятие…</div>';
            }""",
"""            if (withEdit) {
                b3 += '<div class="ws-popup-row ws-popup-more ws-emp-addtr"' +
                      ' title="Добавить мероприятие этому работнику"' +
                      ' onclick="WorkSchedule.onEmpAddTraining(\\'' +
                      this._esc(String(emp['таб_номер'] || '')) + '\\')">+ Мероприятие…</div>';
            }""")

rep("""            html += '<div class="ws-popup-sec">СИЗ · средства индивидуальной защиты</div>';
            if (!ppes.length) {
                html += '<div class="ws-emp-empty">нет выданных СИЗ</div>';""",
"""            var b4 = '<div class="ws-popup-sec">СИЗ · средства индивидуальной защиты</div>';
            if (!ppes.length) {
                b4 += '<div class="ws-emp-empty">нет выданных СИЗ</div>';""")

rep("""                    html += '<div class="ws-ppe-item">' +
                            '<div class="ws-ppe-body">' +
                            '<div class="ws-ppe-name">' +
                            this._esc(String(pz.наименование || '')) + '</div>' +
                            '<div class="ws-ppe-meta">' + pMeta.join(' · ') + '</div>' +
                            '</div>' + pActs + '</div>';""",
"""                    b4 += '<div class="ws-ppe-item">' +
                          '<div class="ws-ppe-body">' +
                          '<div class="ws-ppe-name">' +
                          this._esc(String(pz.наименование || '')) + '</div>' +
                          '<div class="ws-ppe-meta">' + pMeta.join(' · ') + '</div>' +
                          '</div>' + pActs + '</div>';""")

rep("""            if (withEdit) {
                html += '<div class="ws-popup-row ws-popup-more ws-emp-addppe"' +
                        ' title="Добавить СИЗ этому работнику"' +
                        ' onclick="WorkSchedule.onEmpAddPpe(\\'' +
                        this._esc(String(emp['таб_номер'] || '')) + '\\')">+ СИЗ…</div>';
            }
            return html;
        },""",
"""            if (withEdit) {
                b4 += '<div class="ws-popup-row ws-popup-more ws-emp-addppe"' +
                      ' title="Добавить СИЗ этому работнику"' +
                      ' onclick="WorkSchedule.onEmpAddPpe(\\'' +
                      this._esc(String(emp['таб_номер'] || '')) + '\\')">+ СИЗ…</div>';
            }
            // Task 393: asBlocks — массив 4 блоков (страница
            // «Работники», каждое — своё окно), без флага — строка
            return asBlocks ? [b1, b2, b3, b4] : (b1 + b2 + b3 + b4);
        },

        // Task 393 (заявка): ЧЕТЫРЕ БЛОКА карточки работника на
        // странице «Работники»: профиль с действиями / отпуска /
        // мероприятия / СИЗ — КАЖДЫЙ блок отдельным окном-панелью
        // .ws-wcard (вертикальный стек; зазор — margin-bottom, у
        // последнего — 0). Попап шахматки — прежний сплошной вид
        // (_renderWorkerCard без asBlocks)
        _renderWorkerCardPanels: function(tabNo, withEdit) {
            var blocks = this._renderWorkerCard(tabNo, withEdit, true);
            var html = '';
            for (var bi = 0; bi < blocks.length; bi++) {
                html += '<div class="ws-wcard">' + blocks[bi] + '</div>';
            }
            return html;
        },""")

# ---------- JS: _renderWorkersPage — вызов панелей ----------
rep("""            // тело вкладки: «Общая» — сводная таблица всех
            // работников (Task 389: ОКНО-панель .ws-wgen со сплошным
            // фоном — как карточка работника); работник — полная
            // карточка (withEdit)""",
"""            // тело вкладки: «Общая» — сводная таблица всех
            // работников (Task 389: ОКНО-панель .ws-wgen со сплошным
            // фоном — как карточка работника); работник — ЧЕТЫРЕ
            // блока-панели карточки (Task 393: профиль с действиями /
            // отпуска / мероприятия / СИЗ — каждое своё окно)""")

rep("""                contentHtml = '<div class="ws-wcard">' +
                              this._renderWorkerCard(empTabNo, withEdit) + '</div>';""",
"""                contentHtml = this._renderWorkerCardPanels(empTabNo, withEdit);""")

# ---------- CSS: шрифт крупнее + стек панелей ----------
rep("""    .ws-wcard {
        background: var(--bg-tertiary, #0e1621);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 12px 14px 8px;
        margin-bottom: 12px;
    }
    [data-theme="light"] .ws-wcard {
        background: var(--bg-tertiary, #e9e7de);
        border-color: rgba(0,0,0,0.1);
    }""",
"""    .ws-wcard {
        background: var(--bg-tertiary, #0e1621);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        /* Task 393: карточка — ЧЕТЫРЕ блока-окна, текст крупнее
           (правила ниже) — паддинг чуть шире прежнего */
        padding: 14px 16px 12px;
        margin-bottom: 12px;
    }
    [data-theme="light"] .ws-wcard {
        background: var(--bg-tertiary, #e9e7de);
        border-color: rgba(0,0,0,0.1);
    }
    /* Task 393 (заявка): карточка работника на странице «Работники» —
       ШРИФТ ТЕКСТА КРУПНЕЕ + ЧЕТЫРЕ ОТДЕЛЬНЫХ БЛОКА-ОКНА (профиль с
       действиями / отпуска / мероприятия / СИЗ; сборка —
       _renderWorkerCardPanels). Все правила — каскадом от .ws-wcard:
       ПОПАП карточки у сетки (#wsEmpPopup / .ws-cell-popup.ws-emp-
       popup) НЕ внутри .ws-wcard — остаётся в прежней компактной
       типографике. Внутренние строки прижаты к краям окна (боковые
       отступы даёт паддинг панели, а не строки) */
    .ws-wcard .ws-popup-title {
        font-size: 15px;
        padding: 2px 0 8px;
        margin-bottom: 4px;
    }
    .ws-wcard .ws-emp-field {
        font-size: 14px;
        padding: 4px 0;
    }
    .ws-wcard .ws-emp-field .ws-emp-k { min-width: 128px; }
    .ws-wcard .ws-emp-empty {
        font-size: 13px;
        padding: 4px 0 6px;
    }
    .ws-wcard .ws-popup-sec {
        font-size: 12px;
        letter-spacing: 0.6px;
        padding: 0 0 7px;
        margin-top: 0;
        border-top: none;
        border-bottom: 1px solid var(--card-border, rgba(255,255,255,0.08));
    }
    .ws-wcard .ws-popup-row {
        font-size: 14px;
        padding: 8px 0;
    }
    .ws-wcard .ws-popup-more { margin-top: 4px; }
    .ws-wcard .ws-ppe-item {
        font-size: 14px;
        padding: 6px 0;
    }
    .ws-wcard .ws-ppe-name { font-size: 14px; }
    .ws-wcard .ws-ppe-meta { font-size: 12.5px; }
    .ws-wcard .ws-popup-act {
        width: 26px;
        height: 26px;
        font-size: 13px;
    }""")

rep("""    .ws-wtab-body .ws-wcard { margin-bottom: 0; }""",
"""    /* Task 393: в теле вкладки карточка — ЧЕТЫРЕ блока-окна: зазор
       между ними — margin-bottom, у последнего — 0 */
    .ws-wtab-body .ws-wcard { margin-bottom: 12px; }
    .ws-wtab-body .ws-wcard:last-child { margin-bottom: 0; }""")

io.open('index.html', 'w', encoding='utf-8').write(s)
print('task393-patch: %d правок index.html применено (размер %d -> %d байт)' %
      (n_ok, orig_len, len(s)))
