<div align="center">

# Aetherfall: Chronicles of the Shattered Vale
### Хардкорный RPG-модпак · Minecraft 1.20.1 · Forge · 238 записей (218 контентных модов + 20 библиотек)

**Раса. Класс. Таланты. Четыре жизненных навыка. Пять фракций, которые тебя запомнят.**

</div>

---

## Оглавление

| Раздел | Файл | Якорь в спецификации |
|---|---|---|
| 1. Краткое резюме концепции | [SPECIFICATION.md](SPECIFICATION.md#concept) | `#concept` |
| 2. Технический базис | [SPECIFICATION.md](SPECIFICATION.md#tech-basis) · [config/launch-args.txt](config/launch-args.txt) | `#tech-basis` |
| 3. Полная таблица модов (238) | [docs/MODLIST.md](docs/MODLIST.md) · [manifest.json](manifest.json) · [modrinth.json](modrinth.json) | `#mod-table` |
| 4. Библиотеки и зависимости | [SPECIFICATION.md](SPECIFICATION.md#libraries) · [scripts/validate_dependencies.sh](scripts/validate_dependencies.sh) | `#libraries` |
| 5. Матрица конфликтов и решений | [config/conflicts.md](config/conflicts.md) | `#conflicts` |
| 6. Порядок установки и загрузки | [config/install-order.md](config/install-order.md) | `#install-order` |
| 7. План конфигурации (50+ конфигов) | [config/opts/](config/opts/) · [SPECIFICATION.md](SPECIFICATION.md#config-plan) | `#config-plan` |
| 8. Стартовый опыт игрока (первые 30 минут) | [SPECIFICATION.md](SPECIFICATION.md#first-30) | `#first-30` |
| 9. Баланс и кривая прогрессии | [config/balance.md](config/balance.md) | `#balance` |
| 10. Квестовая линия | [config/quest-tree.md](config/quest-tree.md) | `#quest-tree` |
| 11. Система жизненных навыков | [config/liveskills.md](config/liveskills.md) | `#liveskills` |
| 12. Репутация и квесты жителей | [config/reputation-system.md](config/reputation-system.md) | `#reputation` |
| 13. Ресурспаки, шейдеры, звук | [resources/texturepacks.txt](resources/texturepacks.txt) · [resources/shaders.txt](resources/shaders.txt) | `#resources` |
| 14. Чек-лист тестирования (48 пунктов) | [config/checklist.md](config/checklist.md) | `#checklist` |
| 15. Типичные проблемы и их лечение | [README.md](README.md#troubleshooting) | `#troubleshooting` |
| 16. Скрипты автоматизации | [scripts/](scripts/) | `#scripts` |
| 17. Расширение (20 опциональных / 10 запрещённых) | [SPECIFICATION.md](SPECIFICATION.md#extension) | `#extension` |

---

## Концепция — 5 строк питча

1. **Сломанный Вейл.** Мир расколот: каньоны, вывернутые горы, шесть подземных биомов и мёртвые города — следы катастрофы, а не декорация.
2. **Рождение героя.** При первом входе — выбор расы (7 рас), класса (8 классов) и 3 стартовых талантов. Никаких «потом докуплю»: выбор окончательный до 20-го уровня.
3. **Пять фракций помнят тебя.** Фермеры, Ремесленники, Стража, Алхимики, Торговый Дом — у каждой своя шкала в каждой деревне и общая репутация на весь регион.
4. **Четыре ремесла вместо одного меча.** Скотоводство, Рыбалка, Фермерство, Готовка — независимые шкалы 1–100 с реальными разблокировками и требованиями (Project MMO).
5. **Честный хардкор.** Смерть стоит ресурсов и времени, а не часов прогресса: могила с лутом, страховка снаряжения, никаких «неизбежных» убийств в первую ночь.

**Целевая аудитория:** 18–40 лет, играли в RLCraft / Better MC / Vault Hunters, хотят глубокой прогрессии и ролевой игры, но устали от несправедливых смертей и «модов ради модов».
**Время прохождения:** сюжетная линия — 80–120 ч; полное закрытие контента (все боссы, все фракции до «Легенды», коллекции навыков) — 250+ ч. Сервер на 5–10 игроков — сезон 3–4 месяца.

---

## Быстрый старт (Prism Launcher)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/gerr8785-arch/Sborka.git && cd Sborka

# 2. Проверь окружение (Java 17, curl, jq, python3)
bash scripts/validate_dependencies.sh --env-only

# 3. Разреши ID модов (Modrinth API, нужен интернет)
python3 scripts/hydrate_manifest.py --modrinth --mc 1.20.1 --loader forge

# 4. Создай инстанс в Prism Launcher
bash scripts/generate_instance.sh --name "Aetherfall" --mem 12G

# 5. Скачай моды
bash scripts/download_mods.sh --target "$HOME/.local/share/PrismLauncher/instances/Aetherfall/minecraft/mods"

# 6. Проверь полноту зависимостей
bash scripts/validate_dependencies.sh --instance "$HOME/.local/share/PrismLauncher/instances/Aetherfall"
```

RAM: **12 ГБ** на клиент (из 16) · сервер — **8 ГБ**. Java: **17.0.9+ (Temurin/GraalVM CE)**.

---

## Технический базис (кратко)

| Параметр | Значение | Обоснование |
|---|---|---|
| Minecraft | **1.20.1** | Последняя версия, где *весь* стек RPG-модов (Apotheosis 7, Iron's Spells, Better Combat, Origins Forge, Terralith, Alex's Caves) имеет стабильные Forge-сборки. 1.19.2 — меньше контента (нет Deeper and Darker, Alex's Caves), 1.18.2/1.16.5 — нет современного worldgen-стека. |
| Загрузчик | **Forge 47.2.20** | 200+ модов: NeoForge 1.20.1 — мёртвая ветка (все перешли на 1.21), Fabric не имеет Apotheosis/Tetra/Ice and Fire/Goety/Malum/Origins-Forge. Forge 47.2.20 — последняя стабильная 1.20.1-сборка с исправлениями загрузки. |
| Java | **17 (Temurin 17.0.9+9)** | Требование MC 1.20.1; GraalVM CE 17 даёт +5–8 % TPS на сервере. |
| RAM клиент | 12 ГБ, `-Xms6G -Xmx12G` | 200+ модов, ~2.5–3.5 ГБ heap в игре; остальное — off-heap/GLFW/GC-запас. |
| RAM сервер | 8 ГБ, `-Xms8G -Xmx8G` | Фиксированный heap против фрагментации на длинной сессии. |
| GC | G1GC + `-XX:+ParallelRefProcEnabled` | ZGC/Shenandoah на 12 ГБ дают паузы хуже; G1 проверен на 1.20.1. |
| Шейдеры | **Oculus 1.7.0 + Embeddium 0.3.x** | OptiFine несовместим с Embeddium/ModernFix — исключён (см. [conflicts.md](config/conflicts.md#shaders)). |
| Мультиплеер | Dedicated server + Prism | **43 мода помечены `client`** — на сервер их не ставить (список: `Side=client` в [docs/MODLIST.md](docs/MODLIST.md)). |

Готовая JVM-строка: [config/launch-args.txt](config/launch-args.txt).

---

## Выбранный филосовский компромисс по конфликтам

Пак строится по принципу **«один владелец каждой механики»** (подробно — [config/conflicts.md](config/conflicts.md)):

| Механика | Владелец | Что исключено и почему |
|---|---|---|
| Шкалы навыков / XP за действия | **Project MMO** | Reskillable, Level Up!, Passive Skill Tree — дубли или заброшены |
| Дерево талантов | **Pufferfish's Skills** | Passive Skill Tree (не обновлялся), Skillable (нет 1.20.1) |
| Аффиксы и редкости | **Apotheosis 7** | Zenith, RPG Loot — дубль системы атрибутов |
| Мана | **Iron's Spells 'n Spellbooks** (атрибут `irons_spellbooks:max_mana`) | Ars Nouveau использует свою ману как «топливо крафта» — не смешиваем |
| Боевые анимации/мувсеты | **Better Combat + PlayerAnimator** | **Epic Fight исключён**: перехватывает те же хуки рук, что Iron's Spells; конфликт анимаций |
| Биомы | **Terralith + Tectonic** | Biomes O' Plenty, Oh The Biomes You'll Go — конфликт biome source и «двойные» биомы |
| Квесты | **FTB Quests** | Better Questing (1.20.1 нет), HQM (нет), Bountiful оставлен как доска баунти, а не движок |
| Репутация | **KubeJS + scoreboard + FTB Quests** (кастом) | Нет ни одного мода 1.20.1, дающего многофракционную репутацию с деревнями; Vampirism оставлен как отдельная ось |
| Рюкзаки | **Sophisticated Backpacks** | Travelers Backpack — альтернатива, не ставить оба |
| Карта | **JourneyMap** | Xaero's — альтернатива |
| Оптимизация рендера | **Embeddium + Oculus** | OptiFine, Rubidium (устарел), Sodium (Fabric) |
| Оптимизация ИИ/тиков | **Canary** | Radium (дубль Lithium-порта), AI Improvements (устарел) |

---

<a id="troubleshooting"></a>
## 15. Типичные проблемы и их лечение

### 15.1 Краш при старте: `mixin apply failed`

```
org.spongepowered.asm.mixin.injection.throwables.InjectionError:
  Critical injection failure: @Inject ... in <class> failed
Caused by: NoSuchMethodError / ClassNotFoundException: <mod>.class
```

**Причина:** два мода правят один ванильный класс или версия библиотеки не та.
**Лечение по шагам:**
1. Найди в стектрейсе первый `mixin`-мод (обычно прямо в строке `Mixin <mod>.mixins.json:<mixinName>`).
2. Проверь версии: `Apotheosis 7.4.x` **требует** `Apothic Attributes 1.3.x` и `Placebo 8.6.x` — смешение 7.3/1.2 даёт именно этот краш.
3. Если виноват ModernFix — отключи в `config/modernfix-mixins.properties`: `mixin.perf.dynamic_resources=false`, `mixin.bugfix.world_leaks=false`. Перезапуск.
4. Если краш на `PlayerAnimator` + `Iron's Spells` — версия PlayerAnimator должна быть ≥ 1.0.2-rc1.
5. Не помогло — `config/` в сторону, запусти «голый» пак: краш исчез → виноват конфиг, верни файлы по одному.

### 15.2 `Missing registry entries` / `Registry remapping failed`

```
java.lang.IllegalStateException: Missing registry entries: minecraft:dimension[...]
```
**Причина:** клиент и сервер расходятся по датапакам (чаще всего — датапак-моды: Terralith, Incendium, Nullscape, CTOV, Repurposed Structures).
**Лечение:** датапак-моды должны быть **на обеих** сторонах в одинаковой версии. Проверь `logs/latest.log` на `Failed to load datapack`. Никогда не обновляй worldgen-моды в существующем мире без бэкапа (`/backup` через KubeJS или `chunky` не спасает — нужен файловый бэкап).

### 15.3 Мир грузится, но чанки «плывут» и TPS 8

- Прогрей мир: `/chunky radius 5000` → `/chunky start` (это обязательно до открытия сервера).
- `config/forge-common.toml`: `maxChunkUpdatesPerTick` не трогать; `alwaysSetupTerrainOffThread=true`.
- Проверь `spark profiler start` → 30 с → `spark profiler stop`; ищи в топе `AlexsCaves`/`Terralith` worldgen и `entity.tick`.
- Отключи `Mobs Attempt Parkour` (pathfinding-нагрузка) — минус 1–2 мс/тик на 60 мобах.

### 15.4 Десинк анимаций в мультиплеере

Better Combat/PlayerAnimator не синхронизируют атаку при >120 мс пинге. Лечение: не ставить `Mobs Attempt Parkour` одновременно с `AI Improvements` (оба патчат `LivingEntity.travel`), обнови `PlayerAnimator` до последней 1.20.1-сборки, на сервере `max-tick-time=-1` (не убивать сервер watchdog'ом при прогреве).

### 15.5 Конфликт клавиш — готовая карта раскладки

В паке **занято 16 клавиш**, ни одна не пересекается. Настраивается один раз импортом `config/opts/keybinds.txt` (Prism → instance → `options.txt`).

| Клавиша | Действие | Мод | Примечание |
|---|---|---|---|
| `1`–`9` | Хотбар | vanilla | — |
| `ЛКМ` | Атака/комбо | Better Combat | — |
| `ПКМ` | Блок/парирование (щит) | vanilla/Better Combat | удержание = блок, тайминг = парирование |
| `Shift + ЛКМ` | Тяжёлая атака | Better Combat | — |
| `C` | Перекат / уклонение | Combat Roll | переназначено с `R` |
| `R` | Способность класса №1 | Iron's Spells / RPG Series | — |
| `V` | Способность класса №2 | Iron's Spells | — |
| `X` | Ультимейт (раса+класс) | Iron's Spells (слот 5) | — |
| `Z` | Расовая пассивка | Origins | — |
| `J` | Дерево талантов | Pufferfish's Skills | переназначено с `K` |
| `K` | Жизненные навыки (Project MMO GUI) | Project MMO | — |
| `L` | Квесты | FTB Quests | переназначено с `~` |
| `M` | Карта мира | JourneyMap | переназначено с `J` |
| `N` | Репутация (`/rep`) | KubeJS-скрипт пака | команда открывает scoreboard-панель |
| `B` | Рюкзак | Sophisticated Backpacks | — |
| `F` | Взаимодействие с NPC / доска баунти | Easy NPC, Bountiful | — |
| `H` | Гайд пака | Patchouli | — |
| `G` | Выбросить предмет | vanilla | — |
| `Ctrl` | Спринт | vanilla | `C` освобождён под перекат |
| `F3` | Отладка | vanilla | + `F3+G` границы чанков |

> `Tab` — список игроков (vanilla), `Y` — не назначать (конфликт с FTB Quests «claim reward» по умолчанию — переназначено на `Shift+ЛКМ` в GUI).

### 15.6 Дюп предметов (проверять после каждого обновления мода)

Известные векторы в этом стеке: `Sophisticated Backpacks` + `Corail Tombstone` (рюкзак в могиле), `Tetra` + Better Combat (дуал-вилд с ломающимся оружием), `Easy NPC` торговля + `Bountiful`. Лечение: в `validate.yml` есть задача `dupe-smoke` (набор ручных шагов в [config/checklist.md](config/checklist.md), п. 39–42).

### 15.7 `java.lang.OutOfMemoryError: Java heap space` через 2–3 часа

`-Xmx12G` при 16 ГБ ОС — мало места под off-heap. Ставь `-Xmx10G` на клиенте, если ОС Windows с браузером. Проверь `MemoryLeakFix` (не отключать) и `config/journeymap/journeymap.cfg`: `mapping.enabled=false` на сервере.

---

## Лицензии и распространение

Пак **не распространяет** jar-файлы: манифест ссылается на официальные источники (CurseForge/Modrinth). Все моды — с открытой или разрешающей редистрибуцию лицензией; моды с запретом на включение в паки перечислены в [SPECIFICATION.md#extension](SPECIFICATION.md#extension) (раздел «10 модов, которые нельзя добавлять»).

## Статус репозитория

- Источник истины по списку модов: `data/mods_clean.psv` → `data/gen.py` → `docs/MODLIST.md`, `manifest.json`, `modrinth.json`.
- CI: `validate.yml` (структура, дубли зависимостей, JSON-схема), `resolve-manifest.yml` (ручное разрешение ID через Modrinth/CurseForge API).
