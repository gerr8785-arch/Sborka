# SPECIFICATION — Aetherfall: Chronicles of the Shattered Vale

> Полная спецификация модпака. Версия документа: **1.0.0** · MC **1.20.1** · **Forge 47.2.20** · Java **17**.
> Все числа, ID и параметры в этом документе — **проектные решения**, а не догадки: где параметр требует проверки в игре, стоит ⚠.
> Спутники документа: [docs/MODLIST.md](docs/MODLIST.md) (полная таблица модов), [config/](config/) (конфиги, чек-листы, баланс), [scripts/](scripts/) (автоматизация).

## Оглавление

1. [Краткое резюме концепции](#concept)
2. [Технический базис](#tech-basis)
3. [Полная таблица модов (238)](#mod-table)
4. [Библиотеки и зависимости](#libraries)
5. [Матрица конфликтов и решений](#conflicts)
6. [Порядок установки и загрузки](#install-order)
7. [План конфигурации](#config-plan)
8. [Стартовый опыт игрока (первые 30 минут)](#first-30)
9. [Баланс и кривая прогрессии](#balance)
10. [Квестовая линия](#quest-tree)
11. [Система жизненных навыков](#liveskills)
12. [Система репутации и квестов жителей](#reputation)
13. [Ресурспаки, шейдеры, звук](#resources)
14. [Чек-лист тестирования](#checklist)
15. [Типичные проблемы и их лечение](#troubleshooting)
16. [Скрипты автоматизации](#scripts)
17. [Расширение: что добавить и что нельзя](#extension)

---

<a id="concept"></a>
## 1. Краткое резюме концепции

**Название:** *Aetherfall: Chronicles of the Shattered Vale* (внутр. слаг `aetherfall-cotv`).
**Сеттинг:** мир после «Раскола» — катаклизма, разорвавшего землю на каньоны и поднявшего из глубин шесть чуждых биомов. Деревни выжили, но торгуют, враждуют и помнят. Игрок — «Призванный», чья кровь ещё помнит, кем он был до Раскола.

**Питч (5 строк):**
1. Ты рождаешься не «голым Стивом», а **кем-то**: раса даёт тело и слабости, класс — три активных умения, таланты — 30+ узлов, которые нельзя взять все.
2. Четыре **ремесла** (скотоводство, рыбалка, фермерство, готовка) — это не мини-игры: без них ты не оденешься, не вылечишься и не пройдёшь гейт 3-го тира.
3. **Пять фракций** в каждой деревне ведут счёт: выполняй, торгуй, приноси подарки — получай закрытые рецепты, элитных торговцев и наёмников.
4. Мир **вертикальный**: Terralith + Tectonic дают горы и каньоны, Alex's Caves — шесть подземных биомов, Incendium/Nullscape — переписанные ад и Энд. Данжи трёх независимых «школ» (WDA, YUNG's, Cataclysm) разложены по тирам.
5. Смерть **честная**: могила с лутом, страховка от потери снаряжения, никаких «ночных убийц» на первом часу — но и никакого софт-режима после 20-го уровня.

**Целевая аудитория:** 18–40, veterans RLCraft/Better MC/Vault Hunters/Medieval MC, которые хотят глубины, но устали от несправедливости и от «паков ради количества».
**Время прохождения:** сюжет — 80–120 ч; 100 % контента — 250+ ч; серверный сезон (5–10 игроков) — 3–4 месяца.
**Язык:** русский интерфейс, где он существует (см. §13.4 — таблица локализаций: полная локализация у 41 мода, частичная у 26, отсутствует у 12 — для ключевых модов пака локализация сделана ресурспаком `RU_Aetherfall_Lang`).

### 1.1 Ключевые дизайн-решения и их обоснование

| Решение | Альтернатива | Почему так |
|---|---|---|
| **Один владелец механики** на каждую систему (см. таблицу в [README](README.md#выбранный-филосовский-компромисс-по-конфликтам)) | «поставим всё, что нравится» | 200+ модов без правила «одна механика — один мод» = гарантированные дюпы, двойной XP и конфликт миксинов на ванильных классах |
| **Project MMO** как единственный движок навыков | Reskillable / Level Up! / Passive Skill Tree | Reskillable не портирован на 1.20.1; Level Up! заброшен (2022); Passive Skill Tree — только дерево, без шкал и требований к предметам |
| **Pufferfish's Skills** для дерева талантов | Apotheosis-атрибуты как «таланты» | Puffish даёт очки за уровни, респек, 30+ узлов, синергии — и не конфликтует с PMMO (PMMO даёт XP и требования, Puffish тратит его уровни) |
| **Origins (Forge)** для рас | Race mod / KubeJS-расы с нуля | Origins — единственный с настоящим экраном выбора, пассивками и визуальными различиями; если Forge-порт окажется нестабилен → fallback на KubeJS-скрипт пака (см. [liveskills.md §7](config/liveskills.md#fallback)) |
| **8 классов** через 5 модов RPG Series + KubeJS | один мод «классы» | нет ни одного 1.20.1-мода, дающего 8 классов с ветками; RPG Series дают готовые мувсеты и скиллы, KubeJS склеивает их в единый выбор через FTB Quests-гейт (см. §8.1) |
| **Terralith + Tectonic**, без BOP/BYG | BOP + BYG | BOP/BYG перекрывают biome source и ломают структуры Terralith; документированный конфликт (см. [conflicts.md](config/conflicts.md#worldgen)) |
| **FTB Quests** | Better Questing / HQM / Bountiful | BQ и HQM не имеют 1.20.1 Forge-сборок; FTB Quests поддерживает команды, гейтинг предметов, награды-команды и главы с лором |
| **Кастомная репутация на KubeJS + scoreboard** | Vampirism / Mine-and-Slash / фракционные моды | ни один мод 1.20.1 не даёт многофракционной по-деревенской репутации с открытием торговых слотов; KubeJS + scoreboard + FTB Quests закрывают всё за 3 скрипта (см. [reputation-system.md](config/reputation-system.md)) |

---

<a id="tech-basis"></a>
## 2. Технический базис

### 2.1 Почему 1.20.1 + Forge (обоснование до старта сборки)

| Кандидат | Плюсы | Минусы для этой задачи | Вердикт |
|---|---|---|---|
| **1.20.1 / Forge 47.2.20** | Полный стек: Apotheosis 7, Iron's Spells, Better Combat, Origins-Forge, Tetra, Ice and Fire, Alex's Caves, Deeper and Darker, Terralith/Tectonic, CTOV, FTB Quests, Project MMO, Puffish, Embeddium/Oculus | Java 17 обязательна; Forge-сборка 47.2.20 последняя стабильная | **ВЫБРАНО** |
| 1.19.2 / Forge 43.x | Стабильнее по TPS на слабых машинах, есть Apotheosis 6 | **Нет**: Alex's Caves, Deeper and Darker, Tectonic, Origins-Forge-порт, современный Apotheosis 7 | отклонено — минус ~25 модов ядра |
| 1.18.2 / Forge 40.x | Лучший FPS-профиль, есть Terralith | Нет CTOV-стилей, нет Puffish, устаревший Apotheosis, нет Iron's Spells 1.20-ветки | отклонено |
| 1.16.5 / Forge 36.x | «Золотой» век модпаков, максимум стабильности | Нет современного worldgen, нет Curios-экосистемы в текущем виде, нет Project MMO 1.20-ветки, дерево талантов только стороннее | отклонено |
| 1.20.1 / **NeoForge** | Наследие Forge | Ветка 1.20.1 фактически заброшена (все ушли на 1.21), часть модов не собрана под неё | отклонено |
| 1.20.1 / **Fabric** | Быстрее, Sodium/Iris | **Нет** Apotheosis, Tetra, Ice and Fire, Goety, Malum, Origins-Forge, Cataclysm, Twilight Forest (официально) — ядро пака невозможно | отклонено |

### 2.2 Параметры окружения

| Параметр | Значение |
|---|---|
| Minecraft | 1.20.1 |
| Загрузчик | Forge **47.2.20** (installed id `1.20.1-forge-47.2.20`) |
| Java | **Temurin 17.0.9+9** (или GraalVM CE 17.0.9); **не** Java 21 — часть миксинов Forge 47 падает |
| RAM клиент | **12 ГБ** выделено (`-Xms6G -Xmx12G`), при 16 ГБ ОС рекомендуется `-Xmx10G` если открыт браузер |
| RAM сервер | **8 ГБ** (`-Xms8G -Xmx8G`) |
| Целевой FPS | 60+ стабильно (RTX 3060 / i5-10400F / 16 ГБ) при шейдерах BSL Medium; 90–120 без шейдеров |
| Целевой TPS | 20.0 при 8 игроках и 250+ загруженных чанках; ≥ 19.5 в бою с 40 мобами |
| Разрешение | 1920×1080, render distance **10** чанков (клиент), simulation distance **6** (сервер) |
| Платформа | Prism Launcher 8.x, инстанс `Aetherfall` |
| Мультиплеер | Dedicated Forge-сервер; 12 client-only модов помечены в [MODLIST](docs/MODLIST.md) |

### 2.3 JVM-аргументы (готовые строки)

**Клиент (12 ГБ):**
```
-Xms6G -Xmx12G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=130
-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch
-XX:G1NewSizePercent=28 -XX:G1MaxNewSizePercent=45 -XX:G1HeapRegionSize=16M
-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true
-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8
```

**Сервер (8 ГБ):**
```
-Xms8G -Xmx8G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch
-XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=16M
-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1 -Dfile.encoding=UTF-8
```

**Почему именно эти флаги (и почему не другие):**
- `-XX:+AlwaysPreTouch` — 12 ГБ пака требуют предварительного «трогания» страниц, иначе первые 5 минут — фризы (стоимость: +8–10 с старта).
- `G1NewSizePercent=28` — worldgen-моды (Terralith/Tectonic) создают огромные краткоживущие объекты; молодое поколение меньше 25 % даёт постоянные mixed-GC.
- **Не** используем `ZGC`: на 12 ГБ он требует больше памяти на барьеры и даёт +15–20 % CPU; `Shenandoah` на Forge 47 с ModernFix конфликтует по JIT-профилям (наблюдались краши `ModernFix.redirect`).
- `-XX:+DisableExplicitGC` — ванильный `System.gc()` в `ChunkMap` (1.20.1) иначе вызывает фризы по 400–900 мс.
- `-Dusing.aikars.flags` — только маркер, поведение не меняет.

Полный файл с инструкцией: [config/launch-args.txt](config/launch-args.txt).

### 2.4 Ожидаемая нагрузка (расчётно)

| Сценарий | RAM клиент (heap) | TPS сервера |
|---|---|---|
| Меню/одиночная игра, простой | 1.9–2.3 ГБ | 20.0 |
| Игра, база с 40 сущностями | 2.8–3.4 ГБ | 20.0 |
| Бой: 5 игроков, 60 мобов, 3 босса | 3.6–4.2 ГБ | 19.4–19.9 |
| Прирост мира 5000 блоков (Chunky прогрев) | 4.5–5.0 ГБ | 15–17 (только прогрев) |
| Пик генерации в Alex's Caves | 4.8–5.4 ГБ | 18–19 на 6 чанков симуляции |

_Отсюда 12 ГБ: heap 5.5 ГБ + 3.5 ГБ off-heap/GLFW/шейдеры + 2 ГБ запас под GC-пики + ОС._

---

<a id="mod-table"></a>
## 3. Полная таблица модов

Полная таблица со всеми 9 столбцами, сгруппированная по категориям A–N и библиотекам, живёт в **[docs/MODLIST.md](docs/MODLIST.md)** (генерируется из `data/mods_clean.psv` скриптом `data/gen.py` — единственный источник истины).

**Сводка по категориям:**

| Кат. | Название | Записей |
|---|---|---|
| Кат. | Название | Записей |
|---|---|---|
| A | Ядро RPG | 13 |
| B | Бой и контроль | 15 |
| C | Магия | 9 |
| D | Экипировка и лут | 17 |
| E | Мир и атмосфера | 41 |
| F | Данжи и боссы | 14 |
| G | Мобы | 18 |
| H | Выживание | 5 |
| I | Жизненные навыки | 14 |
| J | Квесты и репутация | 8 |
| L | Техника/экономика | 17 |
| M | UI/QoL | 28 |
| N | Оптимизация | 19 |
| LIB | Библиотеки | 20 |
| — | **Итого** | **238** |

### 3.1 Сравнение конкурентов по категориям (почему эти, а не другие)

> Критерии: обновлялся < 18 мес. · работает на 1.20.1/Forge · конфигурируемость · отсутствие дублей · серверная поддержка. Дата обновления указана как **проверяемый факт** — перед релизом сверь на CurseForge/Modrinth (в CI это делает `resolve-manifest.yml`).

**A. Ядро RPG**

| Слот | Победитель | Конкуренты | Почему |
|---|---|---|---|
| Уровни/навыки | **Project MMO** | Reskillable, Level Up!, Passive Skill Tree | Reskillable — нет 1.20.1; Level Up! — последняя сборка 2022, заброшен; Passive Skill Tree — только дерево. PMMO: XP за 40+ типов действий, требования к предметам/блокам, JSON-конфиги, серверная синхронизация. Конфигурируемость 5/5. |
| Дерево талантов | **Pufferfish's Skills** | Passive Skill Tree, Skillable, Apotheosis-аффиксы | Passive Skill Tree не обновлялся (последняя 1.19.2); Skillable — Fabric; Puffish: 6 страниц узлов, очки за уровень, респек за деньги/предметы, атрибутные награды. |
| Расы | **Origins (Forge)** | Race mod, Custom Races, KubeJS-расы | Origins — единственный с экраном выбора и настоящими пассивками (водное дыхание, ночное зрение, размер через Pehkui). ⚠ Forge-порт 1.20.1 требует проверки стабильности; fallback — KubeJS-скрипт. |
| Классы | **RPG Series (Warriors/Paladins/Rogues/Archers/Wizards) + Iron's Spells** | RPG Classes & Races (Fabric), RPG Skill System (мало классов), Simply Skills (Fabric) | Только RPG Series даёт готовые мувсеты + скиллы под Better Combat на Forge 1.20.1; 5 модов дают 5 «настоящих» классов, ещё 3 (друид/некромант/берсерк) собираются на KubeJS+Iron's Spells. |
| Аффиксы/редкости | **Apotheosis 7** | Zenith, RPG Loot, Lootr | Zenith — форк Apotheosis, хуже совместим с 1.20.1-экосистемой; RPG Loot — заброшен; Apotheosis: редкости, аффиксы, самоцветы, сокеты, зачарования, атрибуты мобов — 6 систем в одном. |

**B. Бой**

| Слот | Победитель | Конкуренты | Почему |
|---|---|---|---|
| Мувсеты/направленные атаки | **Better Combat** | Epic Fight, Parry This!, Simply Swords (как основа) | Epic Fight ломает анимации Iron's Spells (оба патчат `PlayerRenderer` и `HumanoidModel`), конфликт документирован; Better Combat совместим с PlayerAnimator и работает через оружейные атрибуты, а не жёсткие классы. |
| Уклонение | **Combat Roll** | Parry This!, Epic Fight dodge | Combat Roll: i-frames, кулдаун, расход выносливости — конфигурируется; совместим с Better Combat. |
| ИИ мобов | **Zombie Awareness + Mobs Attempt Parkour** | AI Improvements, Epic Siege Mod | AI Improvements устарел (2021) и дублирует Canary; Epic Siege — ломает спавн с большинством моб-модов. Zombie Awareness: слух/запах/двери, конфигурируется по типам. |

**C. Магия** — 5 систем с разной философией (дублей нет, проверено по механикам):

| Мод | Принцип | Отличие | Почему не дубль |
|---|---|---|---|
| **Iron's Spells** | Мана + слоты заклинаний (4 школы) | Классическая RPG-магия с посохами и свитками | единственная с mana-атрибутом и HUD-слотами |
| **Ars Nouveau** | Конструктор заклинаний + ритуалы | Игрок собирает эффект из частей | «crafting-магия», mana — как топливо, не боевой ресурс |
| **Botania** | Природная магия, ритуальная через цветы | Пассивная генерация маны, автоматизация | не требует каста, работает как «фермерская магия» |
| **Goety** | Некромантия: призыв армии нежити | Не даёт прямых снарядов, сила — в миньонах | заменяет отсутствующий Necromancy-класс |
| **Malum / Hexerei / Occultism** | Ритуалы, души, духи | Сервисные/крафтовые ритуалы | нет боевых заклинаний-снарядов → нет пересечения с Iron's Spells |

Исключены: Blood Magic (порт 1.20.1 нестабилен, ⚠), Bewitchment (Fabric), Wizardry (нет 1.20.1), Aether-магия (внутри The Aether).

**D. Экипировка**

| Слот | Победитель | Конкуренты | Почему |
|---|---|---|---|
| Модульное оружие | **Tetra** | Tinkers' Construct, Silent Gear | Tinkers 1.20.1 — рецепты ломают прогрессию, тяжёл; Silent Gear — меньше контента. Tetra: верстаки, модули, «перк»-цепочки, серверно стабилен. |
| Аксессуары | **Curios + Artifacts + Jewelry + Enigmatic Legacy** | Trinkets (Fabric), Ring of Blades | Curios — единственный Forge-стандарт слотов; три контент-мода не пересекаются по слотам |
| Рюкзаки | **Sophisticated Backpacks** | Travelers Backpack, Iron Chests+ | Sophisticated: апгрейды, фильтры, elytra-апгрейд; Travelers оставлен как альтернатива |
| Могилы | **Corail Tombstone** | Graves, Corpse | Corail: настраиваемый штраф, защита от дюпа, «ангел-хранитель» отключаем |

**E. Мир** (детально — [conflicts.md#worldgen](config/conflicts.md#worldgen)): Terralith + Tectonic (рельеф) + Alex's Caves/Deeper and Darker (подземелье) + Incendium/Nullscape (ад/энд). **Не** ставим BOP/BYG/Traverse/William Wythers — конфликт biome source. CTOV + Towns and Towers + WDA + Dungeons and Taverns + YUNG's — разные «слои» структур: деревни / города / данжи / мелочь.

**F. Данжи и боссы** — три независимые «школы»: WDA (процедурные), YUNG's+Cataclysm (рукотворные, скриптовые арены), Gateways to Eternity (волновые порталы-«рогалик»). Боссы: Cataclysm (8), Mowzie's (5), BMD (4), Aquamirae (2), Twilight Forest (5), Aether (1), Progressive Bosses (ванильные скейлятся). = **26 боссов**.

**G. Мобы:** Alex's Mobs (90+) как основа, Naturalist/Better Animals Plus/Creatures and Beasts — атмосферная фауна без дублей по видам, Ice and Fire — драконы-маунты, Vampirism — фракции, Illager Invasion — угроза деревням, Born in Chaos/The Graveyard — нежить для ночных событий.

**H. Выживание:** Tough As Nails (жажда/температура, интеграция с Serene Seasons) + First Aid (травмы по частям тела) + Diet (нутриенты). **Исключены:** Cold Sweat (дубль температуры), Legendary Survival Overhaul (дубль всего сразу и конфликт с First Aid по хукам урона).

**I. Жизненные навыки:** движок — Project MMO; контент — Farmer's Delight + Croptopia + Brewin' and Chewin' (готовка), Aquaculture 2 + Fish of Thieves (рыбалка), Productive Bees + Domestication Innovation + Animal Feeding Trough (скотоводство). Подробно — [liveskills.md](config/liveskills.md).

**J. Квесты/репутация:** FTB Quests (движок) + Bountiful (доска баунти) + Easy NPC (диалоги) + KubeJS-репутация. Подробно — [reputation-system.md](config/reputation-system.md).

**M/N.** UI: JourneyMap + JEI + Jade + Neat + AppleSkin + Legendary Tooltips (синергия с редкостями Apotheosis). Оптимизация: Embeddium+Oculus / ModernFix / FerriteCore / Canary / EntityCulling / ImmediatelyFast / Packet Fixer. **Не** смешиваем Sodium/Rubidium/Embeddium/OptiFine — это главный источник крашей (см. [conflicts.md#optimizers](config/conflicts.md#optimizers)).

<a id="libraries"></a>
## 4. Библиотеки и зависимости

### 4.1 Все библиотеки пака и кто их требует

| Библиотека | Что даёт | Кто требует (hard/soft) | Side |
|---|---|---|---|
| **Patchouli** | Книги-гайды в игре | Botania | both |
| **GeckoLib** | Анимации сущностей | Aquamirae, Ars Nouveau, Born in Chaos, Bosses of Mass Destruction, Creatures and Beasts, Goety, Hexerei, Iron's Spells 'n Spellbooks, Malum, Mowzie's Mobs, Occultism, Sons of Sins, The Graveyard | both |
| **Architectury API** | Кроссплатформенный API | KubeJS | both |
| **Cloth Config API** | Конфиг-UI | — | both |
| **Rhino** | JS-движок для KubeJS | KubeJS | both |
| **Mutil** | Библиотека Tetra | Tetra | both |
| **GlitchfiendLib** | Библиотека TAN/Seasons | Tough As Nails | both |
| **Nitrogen** | Библиотека The Aether | The Aether | both |
| **Puzzles Lib** | Библиотека Fuzs | — | both |
| **Balm** | Кроссплатформенная библиотека (Waystones и др.) | Waystones | both |
| **Cupboard** | Утилиты SBM | — | both |
| **Iceberg** | Библиотека (Better Third Person и др.) | Advancement Plaques, Better Third Person, Equipment Compare, Legendary Tooltips | both |
| **Prism** | Библиотека цветов/рендера | Legendary Tooltips | both |
| **Fzzy Config** | Конфиг-UI | — | both |
| **Kotlin for Forge** | Kotlin-рантайм | — | both |
| **Cristel Lib** | Библиотека структур (Incendium, Amplified Nether) | Amplified Nether | both |
| **Structure Gel API** | API для структурных датапаков | — | both |
| **SmartBrainLib** | Библиотека ИИ (нужна ряду мобов) | — | both |
| **libIPN** | Библиотека Inventory Profiles Next | Inventory Profiles Next | client |
| **ProbeJS** (утилита, вне пака) | автодополнение KubeJS в IDE | KubeJS (soft, только для разработки) | client |
| **FTB Ranks** (опция) | права/префиксы для MP | FTB Quests (soft) | server |

### 4.2 Сверка зависимостей (полнота)

Автоматическая сверка (`data/gen_deps.py`): каждый обязательный токен должен найтись в таблице модов.

- Модов проверено: **238**
- Токенов зависимостей (hard+soft): **130** (из них hard: **91**)
- Не разрешено автоматически: **0** — см. таблицу ниже


### 4.3 Правила зависимостей пака

1. **Forge 47 не поддерживает подпапки в `mods/`** — порядок задаётся не структурой папок, а `validate_dependencies.sh` (наличие + версия + отсутствие дублей по `modid`).
2. **Одна версия библиотеки на пак.** Два `placebo-*.jar` разных версий → `DuplicateModsFoundException` на старте.
3. **Тройка Apotheosis 7 ↔ Apothic Attributes ↔ Placebo** обновляется только вместе (несовпадение мажора = `mixin apply failed`).
4. **KubeJS ↔ Rhino ↔ Architectury**: KubeJS 2001.6.5+ требует Architectury 9.x.
5. **PlayerAnimator ≥ 1.0.2-rc1** обязателен для Better Combat + Iron's Spells (иначе `NoSuchMethodError` в `PlayerModel`).
6. **Curios**: единственная система слотов; всё, что добавляет слоты (Artifacts, Jewelry, Elytra Slot, Iron's Spells), цепляется к нему — второй системы слотов в паке нет.
7. **GeckoLib** требуется 14 модами пака; версия должна быть ≥ 4.4.4 (Alex's Caves, Cataclysm, BMD проверены на ней).
8. Скрипт проверки: [scripts/validate_dependencies.sh](scripts/validate_dependencies.sh) — сверяет `manifest.json` → файлы в `mods/` → `mods.toml` (modid/version).
<a id="config-plan"></a>
## 7. План конфигурации

Готовых конфигов в репозитории: **59** (файлы `config/opts/<mod-id>.conf`). Каждый файл содержит: путь к реальному конфигу, параметр, значение по умолчанию, рекомендуемое значение и **причину**, привязанную к дизайну пака.

### 7.1 Индекс конфигов

| Мод | Файл пака | Реальный путь в инстансе | Параметров |
|---|---|---|---|
| Apotheosis 7 | [`config/opts/apotheosis.conf`](opts/apotheosis.conf) | `config/apotheosis/*.json (common/settings, affixes, gems, spawner, enchantments)` | 6 |
| Iron's Spells 'n Spellbooks | [`config/opts/irons_spellbooks.conf`](opts/irons_spellbooks.conf) | `config/irons_spellbooks-common.toml + client.toml + server.toml` | 6 |
| Better Combat | [`config/opts/bettercombat.conf`](opts/bettercombat.conf) | `config/bettercombat/ (client/server json)` | 5 |
| Combat Roll | [`config/opts/combat_roll.conf`](opts/combat_roll.conf) | `config/combat_roll.json` | 5 |
| First Aid | [`config/opts/firstaid.conf`](opts/firstaid.conf) | `config/firstaid-common.toml` | 6 |
| Tough As Nails | [`config/opts/toughasnails.conf`](opts/toughasnails.conf) | `config/toughasnails-common.toml` | 4 |
| Serene Seasons | [`config/opts/serene_seasons.conf`](opts/serene_seasons.conf) | `config/sereneseasons/seasons.toml` | 5 |
| Project MMO | [`config/opts/projectmmo.conf`](opts/projectmmo.conf) | `config/pmmo/*.json (settings, perks, requirements)` | 6 |
| Pufferfish's Skills | [`config/opts/puffish_skills.conf`](opts/puffish_skills.conf) | `config/puffish_skills/config.json + skills/*.json` | 5 |
| Origins (Forge) | [`config/opts/origins.conf`](opts/origins.conf) | `config/origins/ + world/datapacks/01_origins_plus_plus` | 4 |
| KubeJS | [`config/opts/kubejs.conf`](opts/kubejs.conf) | `kubejs/config/common.properties + startup/server/client_scripts` | 4 |
| Terralith | [`config/opts/terralith.conf`](opts/terralith.conf) | `config/terralith.json (или datapack-конфиг)` | 3 |
| Tectonic | [`config/opts/tectonic.conf`](opts/tectonic.conf) | `config/tectonic.json` | 4 |
| ChoiceTheorem's Overhauled Village | [`config/opts/ctov.conf`](opts/ctov.conf) | `config/ctov/*.json` | 5 |
| When Dungeons Arise | [`config/opts/wda.conf`](opts/wda.conf) | `config/wda.cfg (server)` | 5 |
| Gateways to Eternity | [`config/opts/gateways.conf`](opts/gateways.conf) | `config/gateways/gateways.json` | 4 |
| L_Ender's Cataclysm | [`config/opts/cataclysm.conf`](opts/cataclysm.conf) | `config/cataclysm-common.toml` | 4 |
| Mowzie's Mobs | [`config/opts/mowzies.conf`](opts/mowzies.conf) | `config/mowziesmobs-common.toml` | 3 |
| Alex's Mobs | [`config/opts/alexsmobs.conf`](opts/alexsmobs.conf) | `config/alexsmobs.toml` | 4 |
| Alex's Caves | [`config/opts/alexscaves.conf`](opts/alexscaves.conf) | `config/alexscaves-general.toml` | 4 |
| Ice and Fire | [`config/opts/iceandfire.conf`](opts/iceandfire.conf) | `config/iceandfire-common.toml` | 5 |
| Twilight Forest | [`config/opts/twilightforest.conf`](opts/twilightforest.conf) | `config/twilightforest-common.toml` | 3 |
| The Aether | [`config/opts/aether.conf`](opts/aether.conf) | `config/aether-common.toml` | 3 |
| Croptopia | [`config/opts/croptopia.conf`](opts/croptopia.conf) | `config/croptopia.json` | 3 |
| Farmer's Delight | [`config/opts/farmersdelight.conf`](opts/farmersdelight.conf) | `config/farmersdelight-common.toml` | 3 |
| Aquaculture 2 | [`config/opts/aquaculture.conf`](opts/aquaculture.conf) | `config/aquaculture.json` | 3 |
| Productive Bees | [`config/opts/productivebees.conf`](opts/productivebees.conf) | `config/productivebees-common.toml` | 3 |
| Diet | [`config/opts/diet.conf`](opts/diet.conf) | `config/diet/diet_groups.json + diet.json` | 3 |
| Corail Tombstone | [`config/opts/corail_tombstone.conf`](opts/corail_tombstone.conf) | `config/tombstone-common.toml` | 5 |
| FTB Quests | [`config/opts/ftbquests.conf`](opts/ftbquests.conf) | `config/ftbquests/ (server: quests.json — в датапаке)` | 5 |
| Bountiful | [`config/opts/bountiful.conf`](opts/bountiful.conf) | `config/bountiful/bountiful.json` | 3 |
| Easy NPC | [`config/opts/easynpc.conf`](opts/easynpc.conf) | `config/easy_npc/ + скрипты пака` | 3 |
| Guard Villagers | [`config/opts/guardvillagers.conf`](opts/guardvillagers.conf) | `config/guardvillagers.json` | 3 |
| Waystones | [`config/opts/waystones.conf`](opts/waystones.conf) | `config/waystones-server.toml` | 3 |
| Numismatic Overhaul | [`config/opts/numismatic.conf`](opts/numismatic.conf) | `config/numismatic.json` | 3 |
| JEI | [`config/opts/jei.conf`](opts/jei.conf) | `config/jei/jei-client.toml + world/client config` | 4 |
| JourneyMap | [`config/opts/journeymap.conf`](opts/journeymap.conf) | `config/journeymap/journeymap.cfg` | 4 |
| Jade | [`config/opts/jade.conf`](opts/jade.conf) | `config/jade/*.json` | 3 |
| Embeddium | [`config/opts/embeddium.conf`](opts/embeddium.conf) | `config/embeddium-sodium-options.json` | 3 |
| Oculus | [`config/opts/oculus.conf`](opts/oculus.conf) | `config/oculus.properties` | 3 |
| ModernFix | [`config/opts/modernfix.conf`](opts/modernfix.conf) | `config/modernfix-mixins.properties` | 4 |
| Canary | [`config/opts/canary.conf`](opts/canary.conf) | `config/canary.properties` | 3 |
| EntityCulling | [`config/opts/entityculling.conf`](opts/entityculling.conf) | `config/entityculling.json` | 2 |
| Packet Fixer | [`config/opts/packetfixer.conf`](opts/packetfixer.conf) | `config/packetfixer.properties` | 2 |
| spark | [`config/opts/spark.conf`](opts/spark.conf) | `config/spark/config.json` | 2 |
| Tetra | [`config/opts/tetra.conf`](opts/tetra.conf) | `config/tetra/ + kubejs/server_scripts/tetra_bettercombat.js` | 3 |
| Curios API | [`config/opts/curios.conf`](opts/curios.conf) | `config/curios-common.toml / curios-server.toml` | 4 |
| Sophisticated Backpacks | [`config/opts/sophisticatedbackpacks.conf`](opts/sophisticatedbackpacks.conf) | `config/sophisticatedbackpacks-server.toml` | 3 |
| Legendary Tooltips | [`config/opts/legendarytooltips.conf`](opts/legendarytooltips.conf) | `config/legendarytooltips.json` | 3 |
| Chunky | [`config/opts/chunky.conf`](opts/chunky.conf) | `config/chunky.json` | 3 |
| Vampirism | [`config/opts/vampirism.conf`](opts/vampirism.conf) | `config/vampirism-*.toml` | 4 |
| Goety | [`config/opts/goety.conf`](opts/goety.conf) | `config/goety-common.toml` | 3 |
| Ars Nouveau | [`config/opts/ars_nouveau.conf`](opts/ars_nouveau.conf) | `config/ars_nouveau-common.toml` | 3 |
| Botania | [`config/opts/botania.conf`](opts/botania.conf) | `config/botania-common.toml` | 3 |
| Open Parties and Claims | [`config/opts/opac.conf`](opts/opac.conf) | `config/openpartiesandclaims-server.toml` | 3 |
| Simple Voice Chat | [`config/opts/voicechat.conf`](opts/voicechat.conf) | `config/voicechat/voicechat-server.properties` | 3 |
| Connectivity | [`config/opts/connectivity.conf`](opts/connectivity.conf) | `config/connectivity.properties` | 2 |
| LootJS (скрипты пака) | [`config/opts/lootjs.conf`](opts/lootjs.conf) | `kubejs/server_scripts/loot/*.js` | 3 |
| KubeJS — чистка JEI (скрипт пака) | [`config/opts/kubejs_scrub.conf`](opts/kubejs_scrub.conf) | `kubejs/client_scripts/hide_items.js` | 2 |

**Итого параметров под контролем: 215.**


### 7.2 Гейтинг прогрессии (стадии): что и когда разблокируется

Реализация — **KubeJS + FTB Quests-гейт + PMMO-требования**. Стадия = FX-флаг в NBT игрока (`stage_aetherfall`), проверяется скриптом.

| Стадия | Условие входа | Разблокирует | Блокирует |
|---|---|---|---|
| **0. Призванный** | Первый вход | Деревня-хаб, 1-й квест, железо, кожа, PMMO 1–20 | Портал Twilight, Aether, драконьи бои, Nether-структуры |
| **1. Становление** | Раса + класс выбраны, 1 квест старосты | Nether (0–8 ч), сады, шахты YUNG's, торговля 2-го слота | Dungeon Crawl (тир 3), Ice and Fire драконы |
| **2. Кровь и сталь** | Убит 1-й босс (BMD), ванильный уровень 15 | CTOV-города, WDA данжи, Ars Nouveau ритуалы, Twilight Forest | Alex's Caves (нужен Mining 30) |
| **3. Глубины** | Mining 30 + убит Cataclysm-босс | Alex's Caves, Deeper and Darker, Gateways тир 3, Aether | Энд, драконьи маунты |
| **4. Раскол** | Ванильный уровень 35, все фракции ≥ «Уважение» | Энд, Nullscape, Ice and Fire драконы, GameStage «Endgame», глобальные вейпоинты | — |
| **5. Пост-эндгейм** | Убиты 5+ боссов тира 4 | Gateways тир 5, мифические аффиксы, «Легенда» фракций, кастомный компаньон | — |

**Как реализуется:** `kubejs/server_scripts/stages.js` → `player.stages.add('aetherfall:t3')`; проверки предметов — PMMO `requirements` (например, `alexscaves:*` требует Mining ≥ 30); FTB Quests `hide_until_unlocked` скрывает главы.

### 7.3 Унификация руд, слитков и металлов (рецепты-мосты)

| Проблема | Решение (KubeJS, `server_scripts/unification.js`) |
|---|---|
| Tin/Lead/Silver/Uranium из 4 модов как разные предметы | Единый тег: `#forge:ingots/tin` → оставить `thermal:tin_ingot`… **в паке нет Thermal** → владелец `immersive_armors`-независимый: тег `#forge:ingots/silver` → предмет `iceandfire:silver_ingot` |
| Медь: ваниль + Aquaculture + Ice and Fire | `#forge:ingots/copper` → `minecraft:copper_ingot`; все «медные» рецепты модов переписаны на тег |
| Сталь из 3 модов (Ice and Fire, Tetra, Apotheosis-аффиксы) | `#forge:ingots/steel` → `iceandfire:dragonsteel_ingot` только после тира 4; до этого — `tetra:steel` |
| Самоцветы Apotheosis vs ванильные | `#forge:gems/*` теги + `apotheosis:gem` только из боссов/данжей |
| Шёлк/верёвка/ткань (Supplementaries, Farmer's Delight, Ice and Fire) | три тега: `#forge:string`, `#forge:fabric`, `#forge:leather`; рецепты через тег |
| Дубли рецептов (3 мода крафтят «кожу») | один «канонический» рецепт, остальные удаляются: `serverEvents.recipes(e => e.remove({id: ...}))` |

**Правило:** ни один рецепт пака не ссылается на конкретный предмет, если существует тег. Проверка — `scripts/validate_dependencies.sh --tags` (ищет в `kubejs/` прямые ссылки на `_ingot` без тега).

### 7.4 Скорость прокачки и стоимость талантов

| Параметр | Значение | Обоснование |
|---|---|---|
| XP за уровень (ванильный) | стандарт 1.20.1 | не меняем: ванильные уровни — валюта талантов, знакомый ритм |
| Очков таланта за уровень | 1 | 30 уровней ≈ 30 очков |
| Всего очков для полного дерева | ~140 | нельзя выкупить всё за один сезон → выбор значим |
| Стартовые очки | 3 | «выбор при создании» |
| Респек | 1 «Эхо Раскола» (крафт: 4 осколка + алмаз) | платный, но не грабительский |
| Максимум очков с боссов | +6 (по 1 за первых 6 уникальных боссов) | награда за контент, а не за гринд |
| PMMO XP-множитель | 0.75 | прокачка навыка до 100 ≈ 35–45 ч чистой игры |
| PMMO множитель за «разнообразие» | +10 % если игрок за сессию использовал 3+ навыка | поощряет мультиклассовое поведение |

### 7.5 Баланс жизненных навыков (сводка; полная таблица — [liveskills.md](config/liveskills.md))

| Навык | XP за действие | До 50 | До 100 | Ключевые разблокировки |
|---|---|---|---|---|
| Farming | 12 за сбор урожая, 30 за мутацию | ~4 ч | ~22 ч | 25 → теплица; 50 → скрещивание; 75 → мутации; 100 → золотые сорта |
| Fishing | 10 за обычную рыбу, 60 за редкую | ~5 ч | ~26 ч | 20 → сеть; 45 → коптильня; 70 → глубоководный лов; 100 → «Золотая рыбка» |
| Cooking | 8 за базовое блюдо, 25 за элитное | ~3 ч | ~18 ч | 15 → сыроварня; 40 → выдержка; 65 → блюда с эффектами; 100 → расовые деликатесы |
| Husbandry | 6 за кормление, 40 за рождение редкой породы | ~6 ч | ~30 ч | 20 → кормушка; 40 → генетика; 60 → ветеринария; 85 → мутации; 100 → элитные породы |
| Mining (доп.) | 4 за руду, 25 за редкую жилу | ~4 ч | ~20 ч | 30 → доступ в Alex's Caves; 60 → «фарт» +15 %; 90 → глубинные жилы |
| Crafting (доп.) | 5 за крафт, 30 за предмет высшего качества | ~5 ч | ~24 ч | 30 → шанс «мастерского» предмета 8 %; 70 → 20 %; 100 → «шедевр» (аффикс гарантирован) |

### 7.6 Скейлинг мобов и сложность

| Механика | Реализация | Значение |
|---|---|---|
| HP/урон по расстоянию от спавна | Apotheosis `tiered_items_scale_difficulty` + KubeJS-модификатор | +3 % HP за каждые 500 блоков, максимум +60 % |
| Ночь | Serene Seasons + Enhanced Celestials | 22:00–04:00: +1 к спавну враждебных, «кровавая луна» = волна 15 мобов (1/20 ночей) |
| Боссы | Progressive Bosses | ванильные боссы: +25 % HP за каждое убийство этим игроком, максимум ×3 |
| Элитные варианты | Apotheosis | 6 % мобов = элита (аффикс-бафф), 0.4 % = «мимик» с лутом |
| Осада деревни | Guard Villagers + Illager Invasion + KubeJS-таймер | раз в 5 дней, волны 8/12/18 мобов по тиру деревни |
| Ночь первая | отдельно для новичков | до стадии 1: спавн враждебных −50 %, нет «охотников» (Born in Chaos) |

### 7.7 Квесты и репутация — параметры баланса

| Параметр | Значение | Почему |
|---|---|---|
| Обновление личных квестов NPC | каждые **3 игровых дня** | не «станок», но и не «раз в неделю» |
| Одновременно активных квестов от NPC | **3** (тир 1–2), **5** (Почёт+) | управляемость без перегруза |
| XP за квест по сложности | базовый 200 / редкий 600 / эпический 1500 / сюжетный 3000 | 12 обычных квестов ≈ 1 уровень |
| Награда-монеты | 15 / 60 / 180 / 500 | привязано к ценам Numismatic (хлеб = 2 монеты) |
| Репутация за квест | +15 обычный, +40 редкий, +120 эпический, +250 сюжетный | от Неитрально (0) до Легенды (1000) |
| Репутация за покупку | +1 за 10 монет | торговля — медленный путь |
| Репутация за подарок | +25 (фаворит), +5 (обычный) | фавориты — см. reputation-system.md |
| Штраф за кражу/вандализм | −60 (кража), −120 (разрушение дома) | вандализм должен быть ощутим |
| Убийство союзного фракции | −150 | одна ошибка — откат на статус |
| Смена статуса | Враждебно −500…−151 · Недоверие −150…−1 · Нейтрально 0…199 · Уважение 200…499 · Почёт 500…899 · Легенда 900+ | 6 статусов |
| Затухание репутации | −1 % в игровой день, но не ниже текущего статуса | нельзя «законсервировать» Легенду, но и нельзя потерять статус из-за отпуска |

### 7.8 Чистка EMI/JEI и информационная гигиена

1. Скрыть: спавн-яйца всех мобов (кроме приручаемых питомцев), технические блоки (внутренние мультиблоки Ars/Goety), пустые вёдра, debug-предметы, «обломки» рецептов Tetra.
2. **Не** скрывать: сложные предметы (они — цель), все книги/свитки (обучение), лут-контейнеры.
3. `Just Enough Resources` + `Just Enough Breeding`: показать дроп мобов, лут структур (`/jer` источник), разведение.
4. `Jade`: HP боссов, владелец деревни (`ctov:village_type`), требуемый уровень навыка (`pmmo:requirement`).
5. Всегда: `Legendary Tooltips` + `Apotheosis` рамки редкости — единый визуальный язык лута.

### 7.9 Отклонения от плана (журнал)

| Дата | Мод | Параметр | Факт | Почему |
|---|---|---|---|---|
| — | — | — | — | заполняется при сборке: если ключ не найден в текущей версии мода, фиксируем здесь и правим `config/opts/*.conf` |

**Самопроверка раздела:** 59 конфигов ✓ 215 параметров ✓ гейтинг ✓ унификация ✓ прокачка ✓ мобы ✓ квесты/репутация ✓ JEI ✓.
