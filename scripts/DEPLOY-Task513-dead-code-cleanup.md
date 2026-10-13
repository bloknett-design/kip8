# DEPLOY — Task 513 (УБОРКА МЁРТВОГО КОДА) + Task 514 (ПРОВЕРКА ФАКТИЧЕСКОГО Apps Script) — ПРОД kip8

> **Заявки:** «Проверь код приложения на наличие ошибок и мёртвого кода» (Task 512),
> «Подтверждаю уборку» (Task 513), выгрузка всех .gs из Apps Script в docx (Task 514).
> **Task 514 проверял ТЕСТОВЫЙ проект (kip8test).** Состояние ПРОД-проекта Apps Script
> неизвестно и может отличаться (в прод Utils.gs, вероятно, уже содержит Admin-блок —
> репо-версия Utils синхронизирована с прод при Task 347; отдельного Admin.gs может не быть).
> **Перед деплоем сюда: собрать такую же docx-выгрузку всех .gs из ПРОД-проекта и
> сверить (быстро, ~15 минут).**

## Что проверено в тесте (эталон для сравнения прод-выгрузки)

Фактический Apps Script теста: 17 файлов; 11 совпадают с эталоном байт-в-байт; 4 с дрейфом
(Utils без Admin-блока, Flowmeter = Task 359, RoleMatrixGate = Task 319, RoleMatrixInit —
опечатки) + лишний Admin.gs с ОПАСНОЙ копией setupTriggers (runtime безопасен: алфавитный
порядок Admin < Code — канон Code.gs перекрывает).

## План замены для прода (после сверки выгрузки; версии — из репозитория `kip8`, HEAD)

| # | Файл | Действие | Что изменится |
|---|------|----------|---------------|
| 1 | `Utils.gs` | ЗАМЕНИТЬ | встроенный Admin-блок в конце; опасного setupTriggers в версии НЕТ (убран Task 513) |
| 2 | `Admin.gs` | **УДАЛИТЬ ФАЙЛ**, если он есть в прод-проекте | контент встроен в Utils.gs с Task 347 |
| 3 | `Flowmeter.gs` | ЗАМЕНИТЬ | Task 376: честный `archive_write_failed` (показания не теряются) + уборка 513 |
| 4 | `RoleMatrixGate.gs` | ЗАМЕНИТЬ | Task 340: право `workschedule.view.min` (ограниченный просмотр графика) |
| 5 | `RoleMatrix.gs` | ЗАМЕНИТЬ | уборка 513: −`roleMatrixHasPermission`, −`roleMatrixGetAccessForEmail` |
| 6 | `RoleMatrixInit.gs` | ЗАМЕНИТЬ | уборка 513: −`_colLetter`; опечатки (создаёт/хелпер) учтены в Task 514 |
| 7 | `SessionsDevicePolicy.gs` | ЗАМЕНИТЬ | уборка 513: −`sdpDebug` |
| — | `FlowmeterInit.gs`, `StatusCodesInit.gs` | ПРОПУСТИТЬ | одноразовые, в Apps Script разворачивать не нужно |

`Code.gs` НЕ трогать — канон `setupTriggers` (фильтрует только hourlyCleanup) жив там.

## Шаги

1. Собрать выгрузку всех .gs из прод-проекта (как в тесте) → сверить (задача для
   ассистента, ~15 минут) → убедиться в списке файлов замены.
2. Для каждого файла из списка: открыть → выделить всё → вставить из репозитория → Ctrl+S.
3. Удалить `Admin.gs`, если он есть.
4. Сверка: `setupTriggers` — ОДИН (Code.gs); `sdpDebug`, `statusCodesDeployAll`,
   `roleMatrixHasPermission`, `roleMatrixGetAccessForEmail`,
   `flowmeterCleanupCommentMetadata`, `flowmeterFixDates`, `_colLetter` — исчезли.
5. Проверить приложение: вход/OTP, журнал кабелей, расходомеры, расписание,
   ограниченный просмотр графика.
6. Триггеры: `hourlyCleanup` (Every 1 hour) на месте.
7. Журнал выполнения (Ctrl+Enter) — без новых ошибок.

## Откаты

- До уборки 513: `git show pre-task513:scripts/<файл>.gs` (тег в обоих репо)
- Версии теста (если прод совпадал с тестом): `git show 2097d1e7:scripts/Flowmeter.gs`,
  `git show 51bdde92:scripts/RoleMatrixGate.gs`
- Admin.gs целиком: последний блок `git show pre-task513:scripts/Utils.gs`
