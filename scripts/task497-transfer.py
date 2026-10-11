#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 497 (ПЕРЕНОС в kip8, регламент Task 441 — ОДИН инкремент
# kipia-v520 → kipia-v521): «Расходомеры хозрасчётные» — фикс бага
# избранного при первом открытии (карточки из кэша ДО ответа
# сервера; заглушка «Нет избранных» — только когда избранного
# действительно нет; loading/error при наличии избранного —
# «Загрузка данных…» / «Нет связи с сервером»).
#
# Регионы index.html идентичны kip8test@e8b7d6f6 (проверено
# предварительно: init/renderList/_restoreCache содержатся в kip8
# ДО правки — пре-497-регионы совпадают).
import io

INDEX = '/home/z/my-project/kip8/index.html'
SW = '/home/z/my-project/kip8/sw.js'

src = io.open(INDEX, encoding='utf-8').read()

# ---------- A. init(): мгновенный рендер избранного из кэша ----------
OLD_INIT = """            this._restoreCache(silent);
            this._loadFallback(silent);"""
NEW_INIT = """            this._restoreCache(silent);
            // Task 497 (баг-репорт): при наличии избранного показывать
            // его СРАЗУ из локального кэша, ДО подгрузки данных с
            // сервера. Раньше при первом открытии раздела (после входа
            // в приложение) на вкладке «Избранные» (Task 491 открывает
            // её автоматически) висела заглушка «Нет избранных
            // расходомеров», хотя счётчик в нижнем баре показывал число
            // избранных: _restoreCache(silent) заполнял _METERS из
            // localStorage МОЛЧА (без рендера), а первый рендер с
            // данными ждал ответа API. Теперь: кэш есть → мгновенный
            // рендер избранных карточек; серверный load() по завершении
            // перерисует список свежими показаниями (как и раньше).
            // Кэша нет → renderList выше уже показал «Загрузка
            // данных…» (не «Нет избранных…» — порядок заглушек Task
            // 497 в renderList).
            if (silent && this._activeTab === 'fav' &&
                    typeof FlowFav !== 'undefined' &&
                    FlowFav.count() > 0 && this._METERS.length > 0) {
                this.renderList();
            }
            this._loadFallback(silent);"""
assert src.count(OLD_INIT) == 1, 'init _restoreCache: %d' % src.count(OLD_INIT)
src = src.replace(OLD_INIT, NEW_INIT)

# ---------- B. renderList(): порядок заглушек пустого списка ----------
OLD_STUB = """            // Заглушка для пустого списка
            if (!meters || meters.length === 0) {
                if (isFavTab) {
                    container.innerHTML ="""
NEW_STUB = """            // Заглушка для пустого списка
            if (!meters || meters.length === 0) {
                // Task 497 (баг-репорт): пустой список на вкладке
                // «Избранные» ещё не значит «нет избранных»: пока данные
                // не пришли с сервера (_loadState 'loading') или fetch
                // упал ('error'), избранное СУЩЕСТВУЕТ — счётчик в
                // нижнем баре это уже показывает, а заглушка «Нет
                // избранных расходомеров» при первом открытии раздела
                // вводила в заблуждение. Подсказка «Нет избранных…» —
                // только когда избранного ДЕЙСТВИТЕЛЬНО нет (FlowFav
                // пуст) или данные уже загружены, но избранных в них не
                // оказалось (например, расходомер удалён на сервере);
                // в полёте/ошибке — «Загрузка данных…» / «Нет связи с
                // сервером».
                var hasFav497 = (typeof FlowFav !== 'undefined') &&
                                (FlowFav.count() > 0);
                var favEmpty497 = isFavTab &&
                        !(hasFav497 && (this._loadState === 'loading' ||
                                        this._loadState === 'error'));
                if (favEmpty497) {
                    container.innerHTML ="""
assert src.count(OLD_STUB) == 1, 'renderList заглушка: %d' % src.count(OLD_STUB)
src = src.replace(OLD_STUB, NEW_STUB)

io.open(INDEX, 'w', encoding='utf-8').write(src)
print('index.html kip8: init (Task 497 мгновенный рендер) + renderList '
      '(порядок заглушек) — перенесено')

# ---------- C. sw.js: версия + комментарий ----------
sw = io.open(SW, encoding='utf-8').read()
OLD_SW = """// Task 496: «Датчики температуры» — панель произвольного расчёта:
// кнопка подтверждения («Готово»/Enter) мобильной клавиатуры
// закрывает клавиатуру (enterkeyhint done + tempQueryEnterBlur),
// а не перескакивает на следующее поле. Клиент-only.
const CACHE_VERSION = 'kipia-v520';"""
NEW_SW = """// Task 496: «Датчики температуры» — панель произвольного расчёта:
// кнопка подтверждения («Готово»/Enter) мобильной клавиатуры
// закрывает клавиатуру (enterkeyhint done + tempQueryEnterBlur),
// а не перескакивает на следующее поле. Клиент-only.
// Task 497 (перенос из kip8test@e8b7d6f6): «Расходомеры хозрасчётные»
// — баг избранного при первом открытии: если избранное есть, карточки
// показываются СРАЗУ из локального кэша (до ответа сервера), а
// заглушка «Нет избранных расходомеров» больше не появляется в
// состояниях загрузки/ошибки (только когда избранного действительно
// нет). Клиент-only.
const CACHE_VERSION = 'kipia-v521';"""
assert sw.count(OLD_SW) == 1, 'sw.js CACHE_VERSION: %d' % sw.count(OLD_SW)
sw = sw.replace(OLD_SW, NEW_SW)
io.open(SW, 'w', encoding='utf-8').write(sw)
print('sw.js kip8: kipia-v520 → v521 + комментарий Task 497 (перенос)')
print('OK')
