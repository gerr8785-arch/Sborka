# 6. Порядок установки и загрузки

> Три уровня порядка: **(A) порядок сборки инстанса** (что ставить в каком порядке, чтобы не ловить краши), **(B) порядок первого запуска** (когда включать worldgen, когда прогрев), **(C) порядок загрузки датапаков** (единственное, чем реально управляет Minecraft).

## A. Сборка инстанса (17 шагов)

| # | Шаг | Действие | Проверка |
|---|---|---|---|
| 1 | Окружение | Установить **Java 17.0.9 (Temurin)**. `java -version` → `17.0.9`. Удалить Java 8/21 из PATH | `bash scripts/validate_dependencies.sh --env-only` |
| 2 | Prism | Prism Launcher ≥ 8.0 → *Add Instance* → **Forge 1.20.1** → версия **47.2.20** | В инстансе `mmc-pack.json` содержит `net.minecraftforge:47.2.20` |
| 3 | Память | Instance → Settings → Java: `-Xms6G -Xmx12G` + флаги из [launch-args.txt](launch-args.txt) | Запуск: в логе `Using G1GC` и `Xmx12G` |
| 4 | Пустой запуск | Запустить пак **без модов** (папка `mods/` пуста) — убедиться, что ванильный 1.20.1 стартует | Меню игры без крашей |
| 5 | Библиотеки | Скопировать **20 библиотек** (категория LIB из [MODLIST](../docs/MODLIST.md)) | `validate_dependencies.sh --stage libs` |
| 6 | Запуск с библиотеками | Библиотеки без потребителей грузятся молча; ошибка = несовместимая версия Java | Лог: `0 errors` |
| 7 | Ядро RPG (A) + Combat (B) | Apotheosis-трио, Iron's Spells, Better Combat-тройка, RPG Series, PMMO, Puffish, Origins, KubeJS-стек, Pehkui | **Обязательный тестовый запуск**: именно тут вылезают миксин-конфликты анимаций |
| 8 | Магия (C) | Ars Nouveau, Botania, Goety, Malum, Hexerei, Occultism | Запуск; `/reload`; проверить `Tag: irons_spellbooks:schools` |
| 9 | Экипировка (D) | Tetra, Curios-контент, Artifacts, Jewelry, рюкзаки, Corail | Проверить: 8 слотов Curios в инвентаре, нет дублей тултипов |
| 10 | Выживание (H) + навыки (I) | TAN, First Aid, Diet, Farmer's Delight-стек, Croptopia, Aquaculture, Productive Bees | Проверить: HUD жажды/температуры/диеты не перекрывают друг друга |
| 11 | Мобы (G) + Данжи/боссы (F) | Alex's Mobs, Ice and Fire, Cataclysm, Mowzie's, BMD, Gateways, Twilight, Aether | Запуск в **пустом мире** (superflat) — проверка регистрации сущностей |
| 12 | Мир и структуры (E) | Terralith, Tectonic, CTOV, Towns and Towers, WDA, YUNG's, Alex's Caves, Deeper and Darker, Incendium, Nullscape | **Новый мир**, `/locate structure` × 6 (см. шаг 15) |
| 13 | Квесты/репутация (J) | FTB Quests-стек, Bountiful, Easy NPC, Guard Villagers, Villager Names, KubeJS-скрипты пака | `/ftbquests editing_mode` → видна книга «Aetherfall» |
| 14 | Строительство (L), UI (M), оптимизация (N) | Decor, JourneyMap, JEI, Jade, FancyMenu, Embeddium+Oculus, ModernFix, FerriteCore, Canary, Packet Fixer | Запуск с шейдерами: BSL 8.2 Medium → 60+ FPS |
| 15 | Конфиги пака | Скопировать `config/opts/*.conf` в `config/` инстанса (см. [§7](../SPECIFICATION.md#config-plan)); `kubejs/` пака в инстанс | `/reload` в мире |
| 16 | Датапаки | `world/datapacks/`: `aetherfall_core`, `origins_plus_plus`, `terralith_dt_compat` (см. раздел C) | `/datapack list` → все `enabled` |
| 17 | Прогрев и релиз | `/chunky radius 3500` → `/chunky start` → дождаться → бэкап мира | [checklist.md](checklist.md) полностью ✓ |

<a id="server"></a>
## A2. Dedicated server (для мультиплеера)

```bash
# 1. Сервер
mkdir -p ~/aetherfall-server && cd ~/aetherfall-server
wget https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.2.20/forge-1.20.1-47.2.20-installer.jar
java -jar forge-1.20.1-47.2.20-installer.jar --installServer
# 2. Моды: ВСЁ, кроме 12 client-only (см. MODLIST, столбец Side = client)
# 3. Память (user_jvm_args.txt)
echo "-Xms8G -Xmx8G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+AlwaysPreTouch -XX:+DisableExplicitGC" > user_jvm_args.txt
# 4. Конфиги сервера
#   server.properties:
#     view-distance=8        (клиенто-рендер 10, сервер 8 — экономия TPS)
#     simulation-distance=6
#     max-tick-time=-1       (иначе watchdog убьёт сервер на прогреве чанков)
#     network-compression-threshold=256
#     sync-chunk-writes=false
#     spawn-protection=0     (защита — через Open Parties and Claims)
#   config/forge-server.toml: alwaysSetupTerrainOffThread=true
# 5. Simple Voice Chat: открыть UDP 24454
# 6. Прогрев: /chunky radius 3000 → /chunky start
```

**Критично для 200+ модов в MP:**
- `Packet Fixer` и `Connectivity` — **обязательны** (иначе `Internal Exception: packet larger than max` при заходе).
- Все датапак-моды (Terralith/Incendium/Nullscape/CTOV/Repurposed) — **одинаковые версии** на клиенте и сервере, иначе `Missing registry entries`.
- `Open Parties and Claims` — до первого захода игроков создать партию `/opac party create Aetherfall`.

## B. Порядок первого запуска (по времени)

| Время | Действие | Почему |
|---|---|---|
| t+0 | Запуск нового мира **через инстанс клиента** (не сервер) — так видно ошибки регистрации сразу | Краш на загрузке мира читаемее в клиенте |
| t+1 мин | Проверить: экран выбора расы появился (Origins) | если нет — `config/origins/` или датапак Origins++ не подключён |
| t+2 мин | `/reload` → проверить `datapack list` | датапак-моды грузятся при создании мира |
| t+5 мин | `/chunky radius 3500`, `/chunky start` | без прогрева первые исследования = TPS 8 |
| t+40–90 мин | Прогрев закончен → бэкап `world/` (zip) | базовая точка для тестов |
| t+90 мин | Открыть для сервера/игроков | — |

## C. Порядок загрузки датапаков (единственный реально управляемый)

Датапаки применяются **по алфавиту** (`enabled` список в `level.dat`, но фактический merge — по имени папки). Наши имена подобраны так, чтобы порядок был правильным:

```
world/datapacks/
├── 00_aetherfall_core/          ← наши теги, лут-таблицы, PMMO-контент, репутация (ПЕРВЫМ)
├── 01_origins_plus_plus/        ← расы (переопределяет дефолтные origins)
├── 02_terralith/                ← biome source
├── 03_tectonic/                 ← модификатор рельефа ПОВЕРХ terralith
├── 04_ctov/                     ← деревни (читает биом-теги после 02)
├── 05_repurposed_structures/    ← структуры в биомах terralith
├── 06_towns_and_towers/
├── 07_dungeons_and_taverns/
├── 08_incendium/ 09_nullscape/  ← ад/энд
└── 10_aetherfall_quests/        ← FTB Quests-главы (последними: ссылаются на предметы всех модов)
```

**Правило:** всё, что ссылается на контент других модов (наши квесты, лут-таблицы), — **последним**; всё, что определяет биомы, — **раньше** структур.

## D. Чего делать НЕЛЬЗЯ (порядок, который ломает пак)

| Действие | Последствие |
|---|---|
| Ставить worldgen-моды после создания мира | `Missing registry entries`, порча чанков на границах |
| Обновлять Terralith/Tectonic/CTOV на существующем мире без бэкапа | «швы» в ландшафте, деревни в воздухе, потеря прогрева |
| Менять версию Apotheosis отдельно от Apothic Attributes | `mixin apply failed` на старте |
| Добавлять моды **после** прогрева Chunky | новые структуры появятся только в новых чанках → «пустые» зоны |
| Запускать сервер с `max-tick-time=60000` | watchdog убьёт сервер на прогреве 3000 блоков |

**Самопроверка раздела:** шаги ✓ (17 + сервер + датапаки), порядок загрузки задокументирован ✓, антипаттерны ✓.
