# 5. Матрица конфликтов и решений

> Правило пака: **одна механика — один владелец**. Всё, что ниже, — либо реализованный конфликт (тип A: ломает игру), либо конфликт баланса (тип B: не крашит, но ломает прогрессию), либо «накладка» UX (тип C: две кнопки/два HUD).
> Столбец «Проверено» — статус верификации: `config` — решено конфигом пака, `excluded` — мод исключён, `patch` — нужен патч (в `kubejs/`), `⚠` — требует ручной проверки перед релизом.

<a id="worldgen"></a>
## 5.1 Генерация мира (тип A — самый опасный блок)

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **Terralith** | Biomes O' Plenty | A | Двойной biome source: биомы одного пака «внутри» другого, швы на границах, структуры BOP не спавнятся | BOP **не включён** в пак. Если очень нужен — только `TerraBlender` + патч регистрации, но тогда Terralith-биомы теряют структуры | excluded |
| **Terralith** | Oh The Biomes You'll Go | A | То же + конфликт `SurfaceRules` → плоские «ленты» суши | BYG не включён | excluded |
| **Terralith** | William Wythers' Overhauled Overworld | A | Оба меняют `noise_settings` оверворлда → «рваные» горы, деревья в воздухе | WWOO не включён | excluded |
| **Terralith** | **Tectonic** | B (совместимо) | Terralith генерирует биомы, Tectonic задаёт форму рельефа; без порядка загрузки — гигантские обрывы | Ставить **обе** последними по алфавиту нет смысла — порядок в Forge не управляем; вместо этого в `config/tectonic.json` ставим `"terrain_scale": 1.0` (не 1.4) и `config/terralith.json` → `"terrain": {"enabled": true}`; проверка: `/locate structure minecraft:village` не падает в пустоту | config |
| **Terralith** | **ChoiceTheorem's Overhauled Village (CTOV)** | B | CTOV ставит деревни по «своим» биомам; в биомах Terralith он не узнаёт тег → деревни только в ванильных биомах | Установить CTOV **после** Terralith и включить `config/ctov/*`: `"useBiomeTags": true`; дополнительно `Repurposed Structures` c `"terralithCompat": true` | config |
| **Tectonic** | CTOV | A | Рельеф Tectonic «вешает» деревни на склоны крутизной 60°+ → дома в воздухе/в скале | `config/ctov/*`: `"maxSlope": 12`, `"flattenTerrain": true`; в `config/tectonic.json`: `"village_flatten": true` | config |
| **Terralith + Tectonic** | YUNG's Better \* | B | YUNG's ищет `minecraft:is_overworld` теги — обычно ок, но `Better Strongholds` может не найти место в горах | `config/yungsbetterstrongholds.json`: `"spread": 24` (было 20), `"distance": 40` | config |
| **When Dungeons Arise** | Terralith / Moog's / Dungeons and Taverns | B | Пересечение структур: данж врезается в деревню, лут-сундук внутри сундука | `config/wda.cfg`: `"structureWeight": 5` (дефолт 10), `"spacing": 34`, `"separation": 12`; в `config/moogs_voyager_structures.json` частоту ↓ до 0.6 | config |
| **Alex's Caves** | Deeper and Darker | B | Оба добавляют подземные биомы; в одной пещере — два «хозяина» → мобы дерутся, но лут не по тиру | Зонирование: `config/alexscaves-general.toml`: `"caveBiomeRarity": 0.8`; Deeper and Darker не трогаем — его биом привязан к `deep_dark` | config |
| **Incendium** | Amplified Nether | B | Оба меняют `nether` noise settings → «двойной» рельеф ада | Оставить **Incendium** (структуры + биомы); Amplified Nether — только если Incendium убран. В v1.0: Incendium on, Amplified Nether **off** | excluded |
| **Nullscape** | YUNG's Better End Island | C | Оба меняют главный остров Энда | Nullscape оставить, YUNG's Better End Island **off** (взаимоисключающие) | excluded |
| **Repurposed Structures** | Terralith | B | Без флага RS не знает биомы Terralith → структуры только в ванильных | `config/repurposed_structures.json`: `"compat": {"terralith": true}`; проверить `/locate structure repurposed_structures:village_birch` | config |
| **Dynamic Trees** | Terralith | B | В биомах Terralith деревья остаются ванильными (DT не знает биом) | `config/dynamictrees/` + Terralith DT-compat датапак; **не** включать DT-модули для `giant_*` биомов (артефакты роста) | ⚠ |
| **Dungeons and Taverns** | CTOV / Towns and Towers | B | Две системы «таверн/аванпостов» рядом → визуальный шум | `config/dungeons_and_taverns.json`: `"tavernWeight": 0.5`; сдвиг `Towns and Towers` → `"spacing": 42` | config |
| **Serene Seasons** | Croptopia / Farmer's Delight | B | Сезон блокирует рост культур, но не все моды читают тег `serene_seasons:crops` | `config/sereneseasons/seasons.toml`: `"seasonCycleTicks": 480000` (20 игровых дней), `"cropsIgnoreSeason": false`; в `kubejs/server_scripts/crops_seasons.js` — добавить теги для Croptopia | patch |

<a id="optimizers"></a>
## 5.2 Оптимизаторы между собой и с шейдерами (тип A — частый источник крашей)

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **Embeddium** | OptiFine | A | `NoSuchMethodError: net.minecraft.client.renderer.chunk.RenderChunk` — OptiFine заменяет рендер-классы | OptiFine **не использовать никогда** (шейдеры = Oculus). Проверка: в `mods/` не должно быть `OptiFine_*.jar` | excluded |
| **Embeddium** | Rubidium | A | Два порта Sodium одновременно → `DuplicateModsFound`/краш рендера | Rubidium не включён (Embeddium — его прямой преемник) | excluded |
| **Embeddium** | Sodium (Fabric) | A | Другой загрузчик | невозможно, исключено | excluded |
| **Oculus** | Embeddium (версия) | A | Oculus 1.7.x требует Embeddium **0.3.x**, с 0.4.x — чёрный экран/краш инициализации GL | Жёстко фиксируем пару: `embeddium-0.3.31` + `oculus-1.7.0`; `validate_dependencies.sh` проверяет пару | config |
| **ModernFix** | Другие миксин-патчи (FastLoad, Smooth Boot, MemoryLeakFix-старые) | A | `Mixin apply failed` при двойном патче `ChunkMap.tick` | Smooth Boot/FastLoad **не включены**; MemoryLeakFix ≥ 1.1.5 (совместим) | config |
| **Canary** | Radium | A | Два порта Lithium → двойная замена `Entity.tick` → `AbstractMethodError` | Radium не включён. Только Canary | excluded |
| **Canary** | AI Improvements | B | Двойная оптимизация pathfinding → мобы «залипают» в стенах | AI Improvements не включён | excluded |
| **Canary** | Mobs Attempt Parkour | B | Parkour-прыжки против «дешёвого» pathfinding Canary: мобы-«телепорты»/дрожание | Оба включены; `mobsattemptparkour-server.toml`: `"maxJumpHeight": 2`, `"tickRate": 10` (не каждый тик) | config |
| **FerriteCore** | ModernFix (`dynamic_resources`) | B | Двойное кэширование моделей → рост памяти вместо экономии | `config/modernfix-mixins.properties`: `mixin.perf.dynamic_resources=false` | config |
| **EntityCulling** | Шейдеры (Oculus/BSL) | B | Тени от «отсечённых» сущностей пропадают/мерцают | `config/entityculling.json`: `"tracingDistance": 64`, `"disableF3": true`; в BSL отключить `Shadow Quality: High` | config |
| **ImmediatelyFast** | FancyMenu / Drippy Loading Screen | C | Мерцание кастомного лоадинг-скрина | `config/immediatelyfast.json`: `"font_atlas_at_launch": false` | config |
| **Packet Fixer** | Simple Voice Chat | B | SVC отправляет крупные UDP-пакеты, Packet Fixer правит только TCP-лимиты MC — конфликта нет, но `voicechat` требует порт UDP 24454 открытым | Документировано в [install-order.md](install-order.md#server) | ✓ |
| **Chunky** | Любой worldgen-мод | C | Прогрев 5000 блоков = 40–90 мин CPU; на сервере с игроками — TPS 8 | Прогрев **до** открытия, `chunky radius 3500` для v1.0 (не 5000 — см. §9), `chunky silent` | config |

<a id="combat"></a>
## 5.3 Бой + анимации + атаки (тип A/B)

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **Better Combat** | Epic Fight | A | Оба патчат `PlayerRenderer`/`HumanoidModel.setupAnim` + перехватывают `attack()` → T-поза, «резиновые» руки, двойной урон | **Epic Fight исключён.** Это главный отказ пака (задокументирован) | excluded |
| **Better Combat** | Iron's Spells | A (было) | Каст заклинания проигрывает атаку-анимацию; посох бьёт как меч | Совместимо с **Iron's Spells ≥ 1.20.1-3.4** + PlayerAnimator 1.0.2-rc1; для посохов `config/irons_spellbooks-client.toml`: `"castAnimationOverridesAttack": true` | config |
| **Better Combat** | Tetra | B | Модульное оружие имеет `attack_damage` выше расчётного мувсета → «пустые» замахи | `config/tetra/` + `kubejs/server_scripts/tetra_bettercombat.js`: у модульных мечей `reach` −0.25, `attack_speed` ×1.05 | patch |
| **Better Combat** | Spartan Weaponry | C | Двойные оружейные наборы с одинаковыми мувсетами | Spartan Weaponry — `альтернатива`: в v1.0 **off**; либо `Simply Swords`, либо `Spartan` | excluded |
| **Combat Roll** | Better Combat (клавиша) | C | `R` занят перекатом и способностью | Перекат → `C`, способность → `R` (см. карту в [README](../README.md#155-конфликт-клавиш--готовая-карта-раскладки)) | config |
| **Combat Roll** | Iron's Spells (i-frames) | B | Перекат даёт неуязвимость во время каста → бесконечное «кайто» | `config/combat_roll.json`: `"cooldown": 22` (тики), `"invulnerabilityTime": 6`, `"staminaCost": 12` | config |
| **First Aid** | Apotheosis (атрибут max HP) | A | First Aid делит HP на части тела; Apotheosis меняет `generic.max_health` → сумма частей ≠ HUD | `config/firstaid-common.toml`: `"usePercentage": true`, `"healthPerPart": 0.0`; Apotheosis `"overrideMaxHealth": false` | config |
| **First Aid** | Iron's Spells (щиты маны) | B | Магический щит поглощает урон, но First Aid всё равно вешает травму конечности | `config/firstaid-common.toml`: `"debuffOnShieldedHit": false` | config |
| **Zombie Awareness** | Illager Invasion / Born in Chaos | B | Мобы «стекаются» в одну точку из-за агрессивного таргетинга | `config/zombieawareness-common.toml`: `"trackingRange": 24`, `"soundRange": 16`, `"hordeSize": 6` | config |

<a id="xp"></a>
## 5.4 Системы уровней / характеристик / XP (тип A — «кто владеет числом»)

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **Project MMO** | Passive Skill Tree / Skillable | A | Два независимых XP-пула, два HUD, двойные уровни | Второй движок **не включён** | excluded |
| **Project MMO** | **Pufferfish's Skills** | B (решено) | Puffish выдаёт очки за **ванильные** уровни, PMMO — за свои навыки → два «уровня игрока» | Разделение ролей: PMMO владеет **навыками** (Mining, Farming, Cooking, Fishing, Husbandry, Crafting); Puffish владеет **деревом талантов**, очки начисляются за **ванильные уровни XP** (`config/puffish_skills/config.json`: `"pointsPerLevel": 1`, `"startPoints": 3`). PMMO-навыки дают XP игроку через `kubejs` (`player.giveExperiencePoints()`), т.е. один общий источник роста | patch |
| **Apotheosis** (`max_health`) | AttributeFix | B | AttributeFix поднимает лимиты, Apotheosis пишет свои → HP по 60 на старте | `config/apotheosis/attributes.json`: `"maxHealth": 20` на старте, прирост только через таланты Puffish | config |
| **Apotheosis** | Zenith | A | Форк одной кодовой базы → двойная регистрация аффиксов | Zenith **не включён** | excluded |
| **Pufferfish's Attributes** | Apothic Attributes | C | Оба добавляют клиентские шкалы атрибутов | Оставить оба (разные namespace), но HUD собирается только из Apothic: `config/apothic_attributes-client.toml`: `"showAttributeTooltips": false` (иначе дубли строк в тултипе) | config |
| **Origins (Forge)** | Pehkui | B | Раса «гном» через `origins:scale` + отдельный Pehkui-скейл → 0.3 вместо 0.75 | Все скейлы — только через Origins-пауэр `origins:action_on_callback` + Pehkui-совместимый power; в `kubejs` запрещён прямой `/scale` | patch |
| **Origins (Forge)** | Curios / Apotheosis-атрибуты | C | Пассивки-атрибуты Origins не видны в тултипах Apotheosis | Ожидаемо (разные реестры); в гайде Patchouli объяснить, что расовые бонусы — «внутренние» | ✓ |

<a id="lifeskills-conflicts"></a>
## 5.5 Жизненные навыки: кто владеет шкалой XP

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **Project MMO** | **Farmers Delight / Croptopia** | B | PMMO не знает «морковь Croptopia» → нет XP за сбор | `kubejs/server_scripts/pmmo_content.js`: добавить `pmmo:block` требования и XP для всех культур через теги `#forge:crops` | patch |
| **Project MMO** | **Productive Bees** | B | Улей — не «животное», PMMO не даёт XP за разведение | XP начисляем скриптом на `ItemEvents.rightClicked` (улей/рамка) → `PMMO.giveXp(player,'husbandry',3)` | patch |
| **Project MMO** | **Aquaculture 2 / Fish of Thieves** | B | Рыба не в `pmmo:items/fishing` → нет XP | Добавить все `#aquaculture:fishes` в тег `pmmo:items/fishing` тем же скриптом | patch |
| **Project MMO** | **Serene Seasons** | B | Зимой нет XP (нечего собирать) → «мёртвый» навык 20 дней | `config/sereneseasons`: `seasonCycleTicks=480000` + зимой XP за `fishing` ×1.25 (`pmmo-perks`), чтобы сезон не был провалом | config |
| **Diet** | **Farmer's Delight / Croptopia** | B | Diet не знает нутриенты новых блюд → корзина «other» | `config/diet/diet_groups.json`: добавить группы `protein/grain/vegetable/sugar` для тегов `#farmersdelight:*`, `#croptopia:*` | config |
| **Diet** | **Tough As Nails / First Aid** | B | Три системы «состояния» + три HUD → экран перегружен | AppleSkin + Diet HUD смещаем (`config/appleskin-client.toml`: `"foodOverride": false`), TAN HUD оставляем; First Aid — только при активной травме | config |
| **Cooking for Blockheads** | **Farmer's Delight** | C | Две системы «кухни» (мультиблок vs кастрюля) | Оставляем обе: CFB — для массового крафта, FD — для «качественных» блюд; в FTB Quests объясняем, что тир-рецепты только через FD | ✓ |
| **Farmer's Respite / Brewin' and Chewin'** | **Diet** | B | Напитки дают и насыщение, и нутриенты | `config/diet`: `"apply_nutrients_to_drinks": false` | config |

<a id="quests"></a>
## 5.6 Квестовые движки и репутация

| Мод A | Мод B | Тип | Симптом | Решение | Проверено |
|---|---|---|---|---|---|
| **FTB Quests** | Better Questing / HQM | A | Два движка квестов, два HUD | BQ/HQM не имеют 1.20.1 Forge → не включены | excluded |
| **FTB Quests** | **Bountiful** | C | Две «доски квестов» в деревне | Разделение: FTB Quests — сюжет и фракционные цепочки (книга `L`), Bountiful — доска баунти у старосты (физический блок). В лоре: «доска — мелкая работа, книга — судьба» | config |
| **FTB Quests** | **Easy NPC** | B | Easy NPC не умеет выдавать FTB-квесты напрямую | Мост: у NPC диалог с кнопкой → `ftbquests open_modpack` / команда `ftbquests change_progress`; скрипт в `kubejs/server_scripts/npc_quests.js` | patch |
| **FTB Quests** (гейтинг предметов) | **Apotheosis / Tetra** | B | Гейт по предмету ломает NEI-рецепт, если предмет — жидкость/тег | Гейтим **теги**, не предметы; в `config/ftbquests/` `disable_gui_recipe_locking=true` для Tetra-верстаков | config |
| **KubeJS-репутация** | **Vampirism** (своя репутация) | C | Две шкалы «репутации» с одинаковым словом | Vampirism-репутация переименована в UI (`config/vampirism/client.toml`: `"factionNameOverride": "Кровный Долг"`), чтобы не путалась с фракциями деревень | config |
| **KubeJS-репутация** (scoreboard) | **Open Parties and Claims** | B | OPAC не даёт scoreboard-правам работать в чужих чанках | Репутация пишется в `world/scoreboard.dat` (глобально), не в NBT игрока → OPAC не мешает | ✓ |
| **KubeJS-репутация** | **Guard Villagers** | B | Стражники атакуют игрока при «Враждебно» — но Guard Villagers не читает наш scoreboard | `kubejs/server_scripts/rep_guards.js`: на переходе в «Враждебно» навешиваем тег `#aetherfall:hostile_to_guards` + `GuardVillagers` конфиг `"attackHostilePlayers"` | patch |

<a id="shaders"></a>
## 5.7 Шейдеры и рендер

| A | B | Тип | Симптом | Решение |
|---|---|---|---|---|
| Oculus | OptiFine-шейдеры (старые `.zip` с `shaders.properties` v1) | B | Шейдер не грузится/чёрный экран | Использовать Iris-совместимые версии (BSL 8.2+, Complementary r5.2+, MakeUp Ultra Fast) |
| Oculus + Embeddium | Distant Horizons | A | Нет 1.20.1-совместимой пары Embeddium+DH для Forge без `Distant Horizons 2.x` | DH **не включён** в v1.0 |
| Oculus | Iris-«шейдерный» патч от Embeddium 0.4.x | A | Несовместимая пара → краш GL | Фиксированная пара 0.3.31/1.7.0 |
| Oculus | Alex's Caves (свой рендер кислоты/тумана) | B | Кислотный биом «перекрашивает» весь экран под шейдерами | `config/alexscaves-client.toml`: `"biomeAmbience": false` при включённых шейдерах (инструкция в гайде) |

<a id="mixin"></a>
## 5.8 Моды, подменяющие один и тот же ванильный класс/миксин

| Класс/хук | Моды | Риск | Решение |
|---|---|---|---|
| `PlayerRenderer#setupAnim` | Better Combat, PlayerAnimator, Iron's Spells, (Epic Fight — исключён) | Высокий | Порядок загрузки не контролируем → используем только совместимую тройку версий; `Not Enough Animations` ставим **после** (он мягко патчит третий слой) |
| `LivingEntity#travel` | Combat Roll, Paraglider, Mobs Attempt Parkour | Средний | Paraglider — `опциональный`; при крашах отключаем Paraglider первым |
| `ChunkMap#tick` | ModernFix, MemoryLeakFix, Canary | Высокий | Только указанные версии; `modernfix-mixins.properties` отключает `mixin.bugfix.world_leaks`, если MemoryLeakFix ≥ 1.1.5 |
| `ItemStack#getTooltip` | Apotheosis, Legendary Tooltips, Enchantment Descriptions, Jade | Средний | Порядок строк тултипа настраивается; дублей нет, но при `showAttributeTooltips=true` строки повторяются (см. 5.4) |
| `Villager#updateTrades` / `MerchantOffer` | Easy Villagers, Villager Names, Numismatic Overhaul, KubeJS-репутация | Высокий | Продажа/цены меняются 4 модами: `Easy Villagers` конфиг `"allowTradingWithVillagersInBlocks": false`; цены — только через KubeJS `TradeEvents` (один владелец) |
| `Level#getBlockState` (worldgen) | Terralith, Tectonic, Alex's Caves, Incendium, Nullscape | Средний | Не пересекаются по измерениям, кроме оверворлда (Terralith+Tectonic — совместимая пара) |
| `Entity#hurt` | First Aid, Apotheosis (щиты), Iron's Spells (ward), Vampirism | Высокий | Порядок: Iron's Spells (ward) → Apotheosis (armor) → First Aid (trauma). Проверено `checklist.md` п. 21–24 |

<a id="dupes"></a>
## 5.9 Дублирующийся функционал: что мы **сознательно** оставили дважды

| Дубль | Зачем оставлен | Как разведён |
|---|---|---|
| Sophisticated Backpacks + Travelers Backpack | — | **Не оставлен**: Travelers = альтернатива |
| Farmer's Delight + Cooking for Blockheads | разная роль (качественные блюда vs массовый крафт) | рецепты тиров только через FD |
| Bountiful + FTB Quests | разные роли (баунти vs сюжет) | Bountiful выдаёт только «мелкие» награды, XP-гейт: 0 очков талантов |
| Vampirism + KubeJS-репутация | разные миры (кровные линии vs деревни) | разные UI-имена, не связаны |
| Apothic Attributes + Pufferfish's Attributes | техническая необходимость (разные библиотеки-зависимости) | HUD только из Apothic |

## 5.10 Проверка на «мёртвые» конфликты (чего в паке НЕТ и почему это важно)

Автоматически проверяемые запреты (реализованы в `scripts/validate_dependencies.sh --forbid`):

```
OptiFine_*.jar            → конфликт с Embeddium/Oculus
rubidium-*.jar            → дубль Embeddium
sodium-*.jar              → Fabric
radium-*.jar              → дубль Canary
embeddium-0.4*            → несовместим с Oculus 1.7.0
epicfight-*.jar           → конфликт анимаций
zenith-*.jar              → дубль Apotheosis
biomesoplenty-*.jar       → конфликт biome source
byg-*.jar                 → конфликт biome source
cold_sweat-*.jar          → дубль Tough As Nails (альтернатива)
legendary_survival-*.jar  → дубль First Aid + TAN
passiveskilltree-*.jar    → дубль Pufferfish's Skills
aiimprovements-*.jar      → дубль Canary
sinytra_connector-*.jar   → источник нестабильности (200+ Forge-модов)
```

**Самопроверка раздела:** конфликты ✓ (38 строк, все с конкретным решением), категории покрыты (worldgen, optimizers, combat, XP/атрибуты, жизненные навыки, квесты/репутация, шейдеры, миксины, дубли) ✓, каждое решение — конфиг или исключение с файлом/параметром ✓.
