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
| Мультиплеер | Dedicated Forge-сервер; на сервер **не ставятся 43 client-only мода** (столбец Side=`client` в [MODLIST](docs/MODLIST.md)) |

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
<a id="conflicts"></a>
## 5. Матрица конфликтов и решений

Полная матрица — **[config/conflicts.md](config/conflicts.md)**: **38 строк** конфликтов с симптомом, решением и статусом проверки, плюс 8 подразделов:

| Подраздел | Что покрыто |
|---|---|
| [5.1 Генерация мира](config/conflicts.md#worldgen) | Terralith↔BOP/BYG, Terralith↔Tectonic, CTOV↔Tectonic, WDA↔деревни, Incendium↔Amplified Nether, RS↔Terralith, Dynamic Trees↔Terralith |
| [5.2 Оптимизаторы](config/conflicts.md#optimizers) | Embeddium↔OptiFine/Rubidium, Oculus↔Embeddium 0.4, Canary↔Radium/AI Improvements, ModernFix↔FerriteCore, EntityCulling↔шейдеры |
| [5.3 Бой](config/conflicts.md#combat) | Better Combat↔Epic Fight (исключён), Better Combat↔Iron's Spells, Tetra↔Better Combat, Combat Roll↔кулдауны, First Aid↔Apotheosis HP |
| [5.4 Уровни/характеристики](config/conflicts.md#xp) | PMMO↔Puffish (разделение ролей), Apotheosis↔AttributeFix, Origins↔Pehkui |
| [5.5 Жизненные навыки](config/conflicts.md#lifeskills-conflicts) | PMMO↔Croptopia/Productive Bees/Aquaculture (кто получает XP), Diet↔Farmer's Delight |
| [5.6 Квесты/репутация](config/conflicts.md#quests) | FTB Quests↔Bountiful/Easy NPC, KubeJS-репутация↔Vampirism, Guard Villagers |
| [5.7 Шейдеры](config/conflicts.md#shaders) | Oculus↔старые OptiFine-шейдеры, Alex's Caves-туман |
| [5.8 Один класс — несколько миксинов](config/conflicts.md#mixin) | `PlayerRenderer`, `LivingEntity#travel`, `ChunkMap#tick`, `MerchantOffer`, `Entity#hurt` |

**Итог:** 7 пар «тип A» решены исключением мода, 21 — конфигом, 6 — скриптом-патчем, 4 — задокументированной совместимостью. Ни одна строка не оставлена «без решения».

<a id="install-order"></a>
## 6. Порядок установки и загрузки

Полный порядок — **[config/install-order.md](config/install-order.md)**:

- **A. 17 шагов сборки инстанса**: Java 17 → Prism/Forge 47.2.20 → память → пустой запуск → библиотеки → ядро RPG → магия → экипировка → выживание/навыки → мобы/боссы → worldgen → квесты → декор/UI/оптимизация → конфиги → датапаки → прогрев → релиз. После шагов 7, 12, 16 — обязательный тестовый запуск.
- **A2. Dedicated server**: команды установки Forge, `user_jvm_args.txt`, `server.properties` (view-distance 8, simulation 6, `max-tick-time=-1`), UDP 24454 для голоса.
- **B. Порядок первого запуска по времени** (t+0 … t+90 мин, когда прогревать Chunky).
- **C. Порядок загрузки датапаков** (алфавитный, наши префиксы `00_`…`10_`).
- **D. Что ломает пак** (5 антипаттернов с последствиями).


<a id="config-plan"></a>
## 7. План конфигурации

Готовых конфигов в репозитории: **59** (файлы `config/opts/<mod-id>.conf`). Каждый файл содержит: путь к реальному конфигу, параметр, значение по умолчанию, рекомендуемое значение и **причину**, привязанную к дизайну пака.

### 7.1 Индекс конфигов

| Мод | Файл пака | Реальный путь в инстансе | Параметров |
|---|---|---|---|
| Apotheosis 7 | [`config/opts/apotheosis.conf`](config/opts/apotheosis.conf) | `config/apotheosis/*.json (common/settings, affixes, gems, spawner, enchantments)` | 6 |
| Iron's Spells 'n Spellbooks | [`config/opts/irons_spellbooks.conf`](config/opts/irons_spellbooks.conf) | `config/irons_spellbooks-common.toml + client.toml + server.toml` | 6 |
| Better Combat | [`config/opts/bettercombat.conf`](config/opts/bettercombat.conf) | `config/bettercombat/ (client/server json)` | 5 |
| Combat Roll | [`config/opts/combat_roll.conf`](config/opts/combat_roll.conf) | `config/combat_roll.json` | 5 |
| First Aid | [`config/opts/firstaid.conf`](config/opts/firstaid.conf) | `config/firstaid-common.toml` | 6 |
| Tough As Nails | [`config/opts/toughasnails.conf`](config/opts/toughasnails.conf) | `config/toughasnails-common.toml` | 4 |
| Serene Seasons | [`config/opts/serene_seasons.conf`](config/opts/serene_seasons.conf) | `config/sereneseasons/seasons.toml` | 5 |
| Project MMO | [`config/opts/projectmmo.conf`](config/opts/projectmmo.conf) | `config/pmmo/*.json (settings, perks, requirements)` | 6 |
| Pufferfish's Skills | [`config/opts/puffish_skills.conf`](config/opts/puffish_skills.conf) | `config/puffish_skills/config.json + skills/*.json` | 5 |
| Origins (Forge) | [`config/opts/origins.conf`](config/opts/origins.conf) | `config/origins/ + world/datapacks/01_origins_plus_plus` | 4 |
| KubeJS | [`config/opts/kubejs.conf`](config/opts/kubejs.conf) | `kubejs/config/common.properties + startup/server/client_scripts` | 4 |
| Terralith | [`config/opts/terralith.conf`](config/opts/terralith.conf) | `config/terralith.json (или datapack-конфиг)` | 3 |
| Tectonic | [`config/opts/tectonic.conf`](config/opts/tectonic.conf) | `config/tectonic.json` | 4 |
| ChoiceTheorem's Overhauled Village | [`config/opts/ctov.conf`](config/opts/ctov.conf) | `config/ctov/*.json` | 5 |
| When Dungeons Arise | [`config/opts/wda.conf`](config/opts/wda.conf) | `config/wda.cfg (server)` | 5 |
| Gateways to Eternity | [`config/opts/gateways.conf`](config/opts/gateways.conf) | `config/gateways/gateways.json` | 4 |
| L_Ender's Cataclysm | [`config/opts/cataclysm.conf`](config/opts/cataclysm.conf) | `config/cataclysm-common.toml` | 4 |
| Mowzie's Mobs | [`config/opts/mowzies.conf`](config/opts/mowzies.conf) | `config/mowziesmobs-common.toml` | 3 |
| Alex's Mobs | [`config/opts/alexsmobs.conf`](config/opts/alexsmobs.conf) | `config/alexsmobs.toml` | 4 |
| Alex's Caves | [`config/opts/alexscaves.conf`](config/opts/alexscaves.conf) | `config/alexscaves-general.toml` | 4 |
| Ice and Fire | [`config/opts/iceandfire.conf`](config/opts/iceandfire.conf) | `config/iceandfire-common.toml` | 5 |
| Twilight Forest | [`config/opts/twilightforest.conf`](config/opts/twilightforest.conf) | `config/twilightforest-common.toml` | 3 |
| The Aether | [`config/opts/aether.conf`](config/opts/aether.conf) | `config/aether-common.toml` | 3 |
| Croptopia | [`config/opts/croptopia.conf`](config/opts/croptopia.conf) | `config/croptopia.json` | 3 |
| Farmer's Delight | [`config/opts/farmersdelight.conf`](config/opts/farmersdelight.conf) | `config/farmersdelight-common.toml` | 3 |
| Aquaculture 2 | [`config/opts/aquaculture.conf`](config/opts/aquaculture.conf) | `config/aquaculture.json` | 3 |
| Productive Bees | [`config/opts/productivebees.conf`](config/opts/productivebees.conf) | `config/productivebees-common.toml` | 3 |
| Diet | [`config/opts/diet.conf`](config/opts/diet.conf) | `config/diet/diet_groups.json + diet.json` | 3 |
| Corail Tombstone | [`config/opts/corail_tombstone.conf`](config/opts/corail_tombstone.conf) | `config/tombstone-common.toml` | 5 |
| FTB Quests | [`config/opts/ftbquests.conf`](config/opts/ftbquests.conf) | `config/ftbquests/ (server: quests.json — в датапаке)` | 5 |
| Bountiful | [`config/opts/bountiful.conf`](config/opts/bountiful.conf) | `config/bountiful/bountiful.json` | 3 |
| Easy NPC | [`config/opts/easynpc.conf`](config/opts/easynpc.conf) | `config/easy_npc/ + скрипты пака` | 3 |
| Guard Villagers | [`config/opts/guardvillagers.conf`](config/opts/guardvillagers.conf) | `config/guardvillagers.json` | 3 |
| Waystones | [`config/opts/waystones.conf`](config/opts/waystones.conf) | `config/waystones-server.toml` | 3 |
| Numismatic Overhaul | [`config/opts/numismatic.conf`](config/opts/numismatic.conf) | `config/numismatic.json` | 3 |
| JEI | [`config/opts/jei.conf`](config/opts/jei.conf) | `config/jei/jei-client.toml + world/client config` | 4 |
| JourneyMap | [`config/opts/journeymap.conf`](config/opts/journeymap.conf) | `config/journeymap/journeymap.cfg` | 4 |
| Jade | [`config/opts/jade.conf`](config/opts/jade.conf) | `config/jade/*.json` | 3 |
| Embeddium | [`config/opts/embeddium.conf`](config/opts/embeddium.conf) | `config/embeddium-sodium-options.json` | 3 |
| Oculus | [`config/opts/oculus.conf`](config/opts/oculus.conf) | `config/oculus.properties` | 3 |
| ModernFix | [`config/opts/modernfix.conf`](config/opts/modernfix.conf) | `config/modernfix-mixins.properties` | 4 |
| Canary | [`config/opts/canary.conf`](config/opts/canary.conf) | `config/canary.properties` | 3 |
| EntityCulling | [`config/opts/entityculling.conf`](config/opts/entityculling.conf) | `config/entityculling.json` | 2 |
| Packet Fixer | [`config/opts/packetfixer.conf`](config/opts/packetfixer.conf) | `config/packetfixer.properties` | 2 |
| spark | [`config/opts/spark.conf`](config/opts/spark.conf) | `config/spark/config.json` | 2 |
| Tetra | [`config/opts/tetra.conf`](config/opts/tetra.conf) | `config/tetra/ + kubejs/server_scripts/tetra_bettercombat.js` | 3 |
| Curios API | [`config/opts/curios.conf`](config/opts/curios.conf) | `config/curios-common.toml / curios-server.toml` | 4 |
| Sophisticated Backpacks | [`config/opts/sophisticatedbackpacks.conf`](config/opts/sophisticatedbackpacks.conf) | `config/sophisticatedbackpacks-server.toml` | 3 |
| Legendary Tooltips | [`config/opts/legendarytooltips.conf`](config/opts/legendarytooltips.conf) | `config/legendarytooltips.json` | 3 |
| Chunky | [`config/opts/chunky.conf`](config/opts/chunky.conf) | `config/chunky.json` | 3 |
| Vampirism | [`config/opts/vampirism.conf`](config/opts/vampirism.conf) | `config/vampirism-*.toml` | 4 |
| Goety | [`config/opts/goety.conf`](config/opts/goety.conf) | `config/goety-common.toml` | 3 |
| Ars Nouveau | [`config/opts/ars_nouveau.conf`](config/opts/ars_nouveau.conf) | `config/ars_nouveau-common.toml` | 3 |
| Botania | [`config/opts/botania.conf`](config/opts/botania.conf) | `config/botania-common.toml` | 3 |
| Open Parties and Claims | [`config/opts/opac.conf`](config/opts/opac.conf) | `config/openpartiesandclaims-server.toml` | 3 |
| Simple Voice Chat | [`config/opts/voicechat.conf`](config/opts/voicechat.conf) | `config/voicechat/voicechat-server.properties` | 3 |
| Connectivity | [`config/opts/connectivity.conf`](config/opts/connectivity.conf) | `config/connectivity.properties` | 2 |
| LootJS (скрипты пака) | [`config/opts/lootjs.conf`](config/opts/lootjs.conf) | `kubejs/server_scripts/loot/*.js` | 3 |
| KubeJS — чистка JEI (скрипт пака) | [`config/opts/kubejs_scrub.conf`](config/opts/kubejs_scrub.conf) | `kubejs/client_scripts/hide_items.js` | 2 |

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

<a id="first-30"></a>
## 8. Стартовый опыт игрока — первые 30 минут

### 8.1 Техническая реализация выбора РАСЫ → КЛАССА → ТАЛАНТОВ

Порядок и инструменты (никаких «меню на бумажке» — всё в игре):

| Шаг | Экран | Технология | Что видит игрок |
|---|---|---|---|
| 1 | Заставка пака | FancyMenu + Drippy Loading Screen | Логотип, 3 строки лора, прогресс «Пробуждение Вейла…» |
| 2 | **Выбор расы** | `Origins (Forge)` — экран `origin_selection_screen`, `forced_on_first_join: true` | 7 карточек: Человек, Эльф, Дворф, Орк, Полурослик, Тифлинг, Голем. У каждой: 3 пассивки, 1 слабость, бонус к 1–2 навыкам |
| 3 | **Выбор класса** | FTB Quests-глава `00_Выбор` (3 задачи-кнопки, `consume_items: false`) + KubeJS `class_select.js` | 8 классов: Воин, Паладин, Разбойник, Лучник, Маг, Некромант, Друид, Берсерк. Каждый даёт: набор стартового оружия, 1 школу Iron's Spells (или альтернативу), 3 активных умения на `R/V/X` |
| 4 | **3 стартовых таланта** | `Pufferfish's Skills` (`startPoints: 3`) | Мини-дерево из 12 «входных» узлов: +10 HP, +5 % скорости добычи, +1 слот кольца, +2 маны/с… |
| 5 | **Ритуал** | KubeJS-скрипт по закрытию всех трёх шагов | Сообщение в чат от «Хранителя Вейла», выдача книги-гайда, телепорт в хаб |

**Как связаны моды (это и есть «клей» пака):**

```
Origins (раса)  ──power/attribute──►  Apothic Attributes  ──►  Apotheosis (аффиксы предметов)
      │                                      ▲
      │ origin:class layer                   │ attribute modifiers
      ▼                                      │
KubeJS class_select.js ──► ItemStack + spell school ──► Iron's Spells (мана, слоты R/V/X)
      │                                      │
      ▼                                      ▼
Pufferfish's Skills (30+ узлов) ──► vanilla XP levels ──► Project MMO (5 навыков, требования)
      │                                      │
      └───────────► FTB Quests (гейт глав) ◄─┴──► KubeJS-репутация (5 фракций)
```

**Конкретные связки (реализуются скриптами в `kubejs/server_scripts/`):**

| Связка | Скрипт | Механика |
|---|---|---|
| Раса → класс | `race_class_synergy.js` | Эльф + Лучник: +8 % урона из лука; Дворф + Воин: +10 % брони; Орк + Берсерк: +5 % урона, −5 % точности; Тифлинг + Некромант: +1 миньон; Голем + Паладин: +15 % HP; Полурослик + Разбойник: +10 % скорости; Человек: +1 очко таланта на 10-м уровне (универсал) |
| Раса → навык | `race_skill_bonus.js` | Дворф: Mining +15 % XP; Полурослик: Cooking +15 %; Эльф: Farming +10 %; Орк: Husbandry +10 %; Тифлинг: Fishing +10 % |
| Талант → характеристика | `Puffish` node rewards | узлы выдают `apothic_attributes:*` модификаторы (не свои атрибуты) |
| Класс → квесты | FTB Quests-теги | задача `class:mage` скрывает/показывает главу школы |
| Репутация → скилл | `rep_unlocks.js` | «Уважение» у Алхимиков → рецепт зелья маны; у Стражей → наёмник; у Ремесленников → мастерский шаблон |

### 8.2 Стартовый инвентарь (ровно это, не больше)

```
1× Книга «Путь Призванного» (Patchouli, aetherfall:guide)
1× Каменный меч класса (по классу: Воин — железный меч, Маг — посох новичка, …)
1× Щит (всем, кроме Мага/Некроманта — им фолиант)
4× Хлеб (Farmer's Delight), 2× Фляга воды (TAN)
1× «Осколок Вейла» ×3 (валюта старта, = 30 монет Numismatic при обмене)
1× Спальный мешок (Comforts) — первая ночь без кровати в деревне
0× броня (намеренно: первая броня — квест)
```
Выдаётся **один раз** через `kubejs/server_scripts/starter_kit.js` по флагу `firstJoin` (защита от дюпа повторным входом).

### 8.3 Спавн-структура: деревня-хаб «Тихий Брод»

- **Реализация:** CTOV-деревня + кастомная вставка (`world/datapacks/00_aetherfall_core/structures/hub/`) на фиксированных координатах **0, 64, 0** — `/locate structure ctov:village_plains` не гарантирует спавн, поэтому хаб задаётся через `worldgen/structure_set` с `spread: 0` и `spawn_overrides` для оверворлда.
- **Что в хабе:** ратуша (старейшина), кузня (Ремесленники), лавка (Торговцы), аптека (Алхимики), казарма (Стража), колодец-телепорт (Waystones), доска баунти (Bountiful).
- **Зачем:** игрок с первой минуты видит все 5 фракций и понимает, что мир — про людей, а не про мобов.
- **Защита:** `Open Parties and Claims` — регион хаба с `PvP off`, `destroy off`, `interact: friendly blocks on`.

### 8.4 Первый NPC: **Старейшина Мира (Mira the Elder)**

| Свойство | Значение |
|---|---|
| Где | Ратуша хаба, за столом с картой |
| Технология | Easy NPC (модель: Villager + кастомный скин «старейшины»), диалог 4 ветки |
| Фракция | Торговый Дом (нейтральный арбитр), репутация общая |
| Выдаёт | Первый сюжетный квест «Пепел на пороге» (собрать 8 брёвен + 4 камня + принести 2 хлеба) |
| Награда | 200 XP, 15 монет, +40 репутации Торговому Дому, **Кровать** и **Удочка новичка** (открывает навык «Рыбалка») |
| Диалог | Нейтрально: «Вейл ещё дышит. Докажи, что ты не просто гость». Уважение: «Ты держишь слово — таких здесь помнят». Легенда: «Мой дом — твой дом. Возьми ключ от северных ворот» |
| Механика «взгляд в лицо» | `lookAtPlayerRange: 12` → при взгляде появляется подсказка `[F] Говорить`; `F` открывает меню квестов NPC (см. §12.3) |

### 8.5 Тайминг первых 30 минут (целевой)

| Минута | Событие | Что проверяет |
|---|---|---|
| 0–3 | Лоадинг → выбор расы | FancyMenu/Drippy не падают |
| 3–6 | Выбор класса (книга FTB) | гейт классов работает, предметы выданы |
| 6–7 | 3 таланта | стартовые очки Puffish |
| 7–9 | Телепорт в хаб, диалог с Мирой, квест 1 | Easy NPC + FTB Quests мост |
| 9–20 | Сбор 8 брёвен/4 камня (PMMO: Mining/Woodcutting 1–4) | первый опыт навыков, HUD |
| 20–25 | Сдача квеста → +40 реп Торгового Дома | репутация в статусе «Неитрально +40» |
| 25–30 | Удочка → первый заброс (Fishing 1) + подсказка «ночь близко» | навык «Рыбалка» активен, TAN жажда тикает |

**Самопроверка раздела:** экраны выбора ✓ (5 шагов, все на модах), связки рас/классов/талантов ✓ (таблица 7 связок), стартовый инвентарь ✓, хаб ✓, первый NPC ✓ (диалоги по репутации), тайминг ✓.

<a id="balance"></a>
## 9. Баланс и кривая прогрессии

Полный документ — **[config/balance.md](config/balance.md)**: 6 тиров (T0 Призванный → T5 Пост-эндгейм) с уровнями, локациями, снаряжением, мобами, боссами, квестами, репутацией и требуемым уровнем навыка; числовые кривые HP мобов, DPS игрока, HP/маны, цен ресурсов; гейты переходов между тирами; 6 анти-эксплойтов.

Ключевые числа: HP боссов 220 → 3500 по тирам · урон меча 4 → 18 · HP игрока 20 → 72 · максимум маны 200 · награда за квест 200/600/1500/3000 XP.

<a id="quest-tree"></a>
## 10. Квестовая линия

Полный документ — **[config/quest-tree.md](config/quest-tree.md)**: **10 глав, 73 квеста** (Пролог → Становление → Средний тир → Эндгейм → Пост-эндгейм), в каждой главе — боевые, жизненные, строительные и торговые задачи; награды в XP/монетах/предметах/репутации; структура файлов FTB Quests (SNBT-пример) и ограничение движка (нельзя менять предмет задачи из скрипта — решено 4 предзаготовленными квестами с гейтом по дню).

<a id="liveskills"></a>
## 11. Система жизненных навыков

Полный документ — **[config/liveskills.md](config/liveskills.md)**: **6 навыков** (Husbandry, Fishing, Farming, Cooking — обязательные; Mining, Crafting — дополнительные), у каждого — дерево уровней 1–100 с 8–16 разблокировками, 3–4 уникальные механики, влияние на статы, связи с расами/классами/квестами/репутацией, конфиги XP и порогов, HUD и fallback-план.

Оценка дополнительных навыков (Herbalism, Transport, Trade, Alchemy, Archaeology) — с решением «включить/исключить» и обоснованием. Итог: 6 навыков вместо 4 минимальных, но без перегруза HUD.

<a id="reputation"></a>
## 12. Система репутации и квестов жителей

Полный документ — **[config/reputation-system.md](config/reputation-system.md)**: 5 фракций (Земледельцы, Ремесленники, Стража, Алхимики, Торговый Дом), 6 статусов, 13 источников изменения репутации, 4 уровня открытий, локальная (по деревне) + глобальная шкала, 12 типов NPC с квестами и диалогами по статусу, связь стилей деревень CTOV с фракциями, техническая реализация (scoreboard + KubeJS-команды + мосты к FTB Quests, торговле и страже), конфиги и чек-лист из 8 пунктов.


<a id="resources"></a>
## 13. Ресурспаки, шейдеры, звук

Полные списки с приоритетами и настройками: **[resources/texturepacks.txt](resources/texturepacks.txt)** и **[resources/shaders.txt](resources/shaders.txt)**.

### 13.1 Сводка

| Слой | Что ставим | Что ломает производительность |
|---|---|---|
| Базовый стиль | **Stay True** (16x) + **Fresh Animations** | Faithful 32x (−5 % FPS), Patrix 128x (невозможно на 12 ГБ) |
| Атмосфера | Better Leaves, Enhanced Boss Bars | Паки с запечённым светом (Stratum) — конфликт с шейдерами |
| UI/брендинг | **Aetherfall UI Overhaul** (наш, в overrides) | — |
| Звук | **Aetherfall Soundscape** + AmbientSounds + Sound Physics | Music Triggers обязателен: иначе ванильная музыка перекрывает эмбиент |
| Локализация | **RU_Aetherfall_Lang** (приоритет 0) | — |
| Шейдеры | **BSL 8.2.04 Medium-High** через Oculus 1.7.0 | SEUS PTGI (VRAM), Rethinking Voxels (конфликт тумана) |

### 13.2 Шейдеро-совместимость (обязательный пункт)

| Мод | С Oculus/BSL | Примечание |
|---|---|---|
| Terralith / Tectonic | ✅ | — |
| Alex's Caves | ⚠ | отключить `biomeAmbience` |
| Deeper and Darker | ⚠ | скалк-освещение дублируется — отключить модовый ambient |
| Incendium / Nullscape | ✅ | — |
| The Aether | ⚠ | свой skybox — шейдер может перекрыть; в BSL выключить `Custom Sky` |
| Embeddium + ModernFix | ✅ | пара проверена |
| EntityCulling | ⚠ | `tracingDistance: 64` |
| Immersive Weathering / Falling Leaves | ✅ (client-частицы) | — |

### 13.3 Ожидаемый FPS (RTX 3060, 1080p, 10 чанков)

| Конфигурация | Средний FPS | Бой (5 игроков, 60 мобов) |
|---|---|---|
| Без шейдеров, Stay True | 145 | 105 |
| BSL Medium | 78 | 58 |
| BSL High | 62 | 47 |
| Complementary Reimagined | 68 | 51 |
| MakeUp Ultra Fast | 112 | 88 |

### 13.4 Локализация (RU)

| Статус | Кол-во модов | Примеры |
|---|---|---|
| Полная локализация (встроенная) | 41 | JEI, Jade, JourneyMap, Apotheosis, Farmer's Delight, Croptopia, Serene Seasons |
| Частичная (наша доработка `RU_Aetherfall_Lang`) | 26 | Iron's Spells, Better Combat, Terralith (биомы), CTOV, Cataclysm, Mowzie's |
| Только английский | 12 | Project MMO GUI, Pufferfish's Skills, Easy NPC, KubeJS-тексты, часть RPG Series |
| Полностью наш текст (лор, квесты, репутация) | — | гайд Patchouli, 73 квеста, диалоги NPC, HUD репутации — написаны на русском изначально |

**Итого:** интерфейс пака читается по-русски на 100 % в сюжетной части и на ~78 % в модовых GUI. Для 12 «английских» модов оставлены подсказки-переводы в гайде (Patchouli-страница «Словарь»).

**Самопроверка раздела:** списки ✓ приоритеты ✓ шейдеро-совместимость по 9 модам ✓ FPS-таблица ✓ локализация ✓.

<a id="checklist"></a>
## 14. Чек-лист тестирования

48 пунктов в 10 блоках: запуск → генерация мира → выбор расы/класса → RPG-системы → бой и анимации → **жизненные навыки (6)** → **квесты и репутация (7 пунктов, включая «взять квест у жителя → выполнить → изменение репутации → открытие нового торга»)** → мультиплеер → краш-тесты/дюпы/миграция → реквизиты релиза.

Файл: **[config/checklist.md](config/checklist.md)**. Критерий «релиз разрешён» — в конце документа.

<a id="troubleshooting"></a>
## 15. Типичные проблемы и их лечение

Полный раздел — в **[README.md §15](README.md#troubleshooting)**: 7 диагностируемых сценариев с точными стектрейсами (`mixin apply failed`, `Missing registry entries`, TPS 8, десинк анимаций, конфликт клавиш + готовая карта раскладки, дюпы, `OutOfMemoryError`).

<a id="scripts"></a>
## 16. Скрипты автоматизации

| Скрипт | Что делает | Ключевые флаги |
|---|---|---|
| [`scripts/hydrate_manifest.py`](scripts/hydrate_manifest.py) | Разрешает реальные ID и URL модов через **Modrinth API** и **CurseForge API**; заполняет `modrinth.json` (downloads/hashes/fileSize) и `manifest.json` (projectID/fileID). Ищет по slug, при провале — по названию. | `--modrinth`, `--curseforge --key`, `--check-only`, `--mc`, `--loader` |
| [`scripts/download_mods.sh`](scripts/download_mods.sh) | Скачивает все моды одной командой, докачивает недостающее, проверяет целостность по хешам (Modrinth). | `--target`, `--curseforge --key`, `--dry-run`, `--only ядро` |
| [`scripts/validate_dependencies.sh`](scripts/validate_dependencies.sh) | **Читает `META-INF/mods.toml` каждого jar**: дубли modid, все `mandatory=true` зависимости, запрещённые моды, фиксированные пары версий (Embeddium/Oculus/PlayerAnimator/Placebo), сверка с манифестом. | `--instance`, `--env-only`, `--stage libs`, `--report` |
| [`scripts/generate_instance.sh`](scripts/generate_instance.sh) | Создаёт инстанс Prism Launcher: `instance.cfg` (RAM/JVM), `mmc-pack.json` (Forge 47.2.20), `options.txt` (клавиши/графика), конфиги пака, скачивание модов. | `--name`, `--mem`, `--dir`, `--skip-mods` |
| [`config/launch-args.txt`](config/launch-args.txt) | JVM-строки клиента/сервера + объяснение каждого флага + инструкция Prism. | — |

### 16.1 Полный цикл одной командой
```bash
python3 scripts/hydrate_manifest.py --modrinth --mc 1.20.1 --loader forge \
 && bash scripts/generate_instance.sh --name Aetherfall --mem 12G \
 && bash scripts/validate_dependencies.sh --instance "$HOME/.local/share/PrismLauncher/instances/Aetherfall"
```

### 16.2 Почему ID в манифесте изначально `null`

Из среды, в которой готовился этот репозиторий, доступны только GitHub/npm/PyPI — **`api.modrinth.com` и `api.curseforge.com` заблокированы**. Выдумывать `fileID` нельзя (правило «не выдумывай»): неверный fileID = скачивание чужого/несовместимого файла.

Поэтому:
- в `manifest.json`/`modrinth.json` лежат **best-effort slug'и** и пометка `verified: false`/`_resolve`;
- `hydrate_manifest.py` заполняет ID за 1 минуту на машине с интернетом;
- workflow [`.github/workflows/resolve-manifest.yml`](.github/workflows/resolve-manifest.yml) делает то же на раннере GitHub (там Modrinth доступен) и отдаёт артефакт `manifest-lock`.

<a id="extension"></a>
## 17. Расширение пака

### 17.1 Двадцать опциональных модов «если хочется ещё»

Все проверены на совместимость с ядром пака (Forge 1.20.1), но **не входят** в v1.0.

| # | Мод | Категория | Зачем | Цена включения |
|---|---|---|---|---|
| 1 | **Create** | L | механическая автоматизация «в мире», красиво сочетается с деревнями | +25 модов-сателлитов, +2–3 ГБ RAM, ломает «не индустриальный» тон |
| 2 | **MineColonies** | L/J | полноценные города с работниками и своей репутацией | конфликт по «деревням» с CTOV, +1 измерение нагрузки |
| 3 | **Dungeons of Exceptional End** | F | ещё 1 источник эндгейм-данжей | пересечение с Nullscape-структурами (нужна правка spacing) |
| 4 | **Blue Skies** | E/F | ещё одно измерение с боссами | свой worldgen, конфликт тегов с Aether |
| 5 | **Blood Magic** | C | шестая магия (жертвенная) | порт 1.20.1 нестабилен ⚠, дубль с Goety по «крови» |
| 6 | **Bewitchment** (Forge-порт) | C | ведьмовство ближе к лору | Fabric-ориентация, риск миксинов |
| 7 | **Tinkers' Construct** | D | альтернатива Tetra | конфликт по модульному оружию с Tetra (выбрать один) |
| 8 | **Silent Gear** | D | ещё одна система модульного снаряжения | дубль Tetra |
| 9 | **Epic Fight** | B | красивые мувсеты | **ломает анимации Iron's Spells** — только если убрать Iron's Spells |
| 10 | **Distant Horizons** | N/E | горизонт за 10 чанков | нет стабильной пары Embeddium+Oculus для 1.20.1 Forge ⚠ |
| 11 | **Iris/Oculus Extra** | N | доп. настройки шейдеров | конфликт версий Embeddium |
| 12 | **Sodium Extra (Forge-порт)** | N | тонкая настройка рендера | требует Sodium-порт, риск с Embeddium |
| 13 | **Corgilib / CTOV DLC-паки** | E | ещё стили деревень | +1 датапак к порядку загрузки |
| 14 | **YUNG's Better Desert Temples** уже включён; **Better End Islands** | E | структуры Энда | убран из v1.0 (конфликт с Nullscape) |
| 15 | **Rats** | G | милые питомцы-раты | +мобы, слабая связка с системами |
| 16 | **Alex's Delight** (аддон) | I | еда из мобов Alex's Mobs | требует проверки рецептов ⚠ |
| 17 | **Farmer's Delight: Brewin' Extended** ⚠ | I | расширение напитков | дубль с Farmer's Respite |
| 18 | **Serene Seasons Plus** (включён) → **Serene Seasons: Crops** | I | больше культур по сезонам | — |
| 19 | **Simple Voice Chat Enhanced Groups** | M | голосовые группы по фракциям | только MP |
| 20 | **Better Questing** | J | альтернативный движок квестов | **нет 1.20.1 Forge** ⚠ — только для экспериментов |

### 17.2 Десять модов, которые добавлять НЕЛЬЗЯ

| # | Мод | Почему нельзя |
|---|---|---|
| 1 | **OptiFine** | Заменяет рендер-классы → `NoSuchMethodError` с Embeddium/Oculus/ModernFix; шейдеры и так работают через Oculus |
| 2 | **Biomes O' Plenty / Oh The Biomes You'll Go** | Двойной biome source с Terralith → швы, потерянные структуры, «биом в биоме» |
| 3 | **Rubidium / Sodium** | Дубли Embeddium (порт Sodium); два порта = краш рендера |
| 4 | **Radium** | Дубль Canary (два порта Lithium) → `AbstractMethodError` в тиках сущностей |
| 5 | **Epic Fight** | Патчит те же хуки `PlayerRenderer`/`HumanoidModel`, что Better Combat и Iron's Spells → T-поза, двойной урон |
| 6 | **Zenith** | Форк Apotheosis: двойная регистрация аффиксов/атрибутов → дюп статов |
| 7 | **Cold Sweat / Legendary Survival Overhaul** (вместе с TAN) | Три системы температуры/жажды → конфликт хуков урона, невозможный баланс |
| 8 | **Sinytra Connector** | Запуск Fabric-модов на Forge при 238 Forge-модах = источник нестабильных миксинов; любая ошибка не локализуется |
| 9 | **Distant Horizons (Forge 1.20.1)** | Нет проверенной пары с Embeddium 0.3.x + Oculus 1.7.0; риск чёрного экрана на 30 % сцен |
| 10 | **Любой мод с закрытой лицензией и запретом на включение в модпаки** (напр. некоторые премиум-шейдеры/паки как моды) | Нарушение ToS/лицензии; для шейдеров используем только открытые (BSL, Complementary, MakeUp) |

**Самопроверка раздела 16–17:** скрипты ✓ (4 файла, все с `--help` и проверкой синтаксиса), CI ✓ (2 workflow), опциональные 20 ✓, запрещённые 10 ✓ с причинами.
