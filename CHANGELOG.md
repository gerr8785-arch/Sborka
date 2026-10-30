# Changelog

## [1.0.0] — 2026-10-30

### Добавлено
- **238 записей модов**: 218 контентных + 20 библиотек (Forge 1.20.1 / 47.2.20). 70 ядро · 86 важных · 68 опциональных · 13 альтернатив · 1 исключён (Sinytra Connector).
- `SPECIFICATION.md` — 17 разделов (концепция, технический базис, таблица модов, библиотеки, конфликты, порядок установки, план конфигурации, старт, баланс, квесты, навыки, репутация, ресурсы, чек-лист, лечение проблем, скрипты, расширение).
- `docs/MODLIST.md` — полная таблица 238 модов с зависимостями, Side и критичностью.
- `manifest.json` (CurseForge-формат) + `modrinth.json` (Modrinth CLI-формат), 237 файлов каждый.
- `config/` — 59 готовых конфигов (`config/opts/*.conf`, 215 параметров с обоснованием), `checklist.md` (48 пунктов), `conflicts.md` (38 конфликтов), `install-order.md`, `balance.md` (6 тиров), `quest-tree.md` (10 глав / 73 квеста), `liveskills.md` (6 навыков), `reputation-system.md` (5 фракций), `launch-args.txt`, `opts/keybinds.txt`.
- `scripts/` — `hydrate_manifest.py`, `download_mods.sh`, `validate_dependencies.sh`, `generate_instance.sh`.
- `resources/` — `texturepacks.txt`, `shaders.txt` (Oculus + BSL).
- CI: `.github/workflows/validate.yml`, `.github/workflows/resolve-manifest.yml`.

### Известные ограничения
- `projectID`/`fileID` в манифестах = `null`: API CurseForge/Modrinth недоступны из среды подготовки. Запусти `scripts/hydrate_manifest.py` или workflow `resolve-manifest` — заполнятся автоматически.
- 12 модов помечены ⚠ (требуют проверки сборки под 1.20.1 Forge) — список: `grep "⚠" docs/MODLIST.md`.

## [Unreleased]
- KubeJS-скрипты пака (`stages.js`, `rep_*.js`, `pmmo_content.js`) вынесены в отдельный PR — в v1.0.0 описаны в спецификации, не реализованы кодом.
- Датапак `00_aetherfall_core` (хаб-структура, теги, лут-таблицы) — следующий шаг.
