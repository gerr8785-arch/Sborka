#!/usr/bin/env python3
# Генератор config/opts/<mod-id>.conf — «готовый конфиг + обоснование каждого значения».
import os, textwrap
OUT = "config/opts"
os.makedirs(OUT, exist_ok=True)

MODS = [
("apotheosis", "Apotheosis 7", "config/apotheosis/*.json (common/settings, affixes, gems, spawner, enchantments)",
 [("affixes.tiered_rarity_weights","common 60 / uncommon 25 / rare 10 / epic 4 / mythic 1","45 / 28 / 15 / 8 / 4",
   "в паке 26 боссов и 3 источника данжей: мифика должна быть наградой за тир, а не падать с зомби"),
  ("affixes.max_affixes_per_item","uncommon 1, rare 2, epic 3, mythic 4","uncommon 1, rare 2, epic 3, mythic 4 (оставить) + tiered_items_scale_difficulty: false",
   "10 аффиксов на предмете ломают курируемый билд; зависимость от сложности отключена, иначе лут в Alex's Caves = бог-режим"),
  ("enchantments.boss_enchantment_chance","0.25","0.45",
   "Apotheosis навешивает усиленные зачарования на элитных мобов; 45 % делает ночные волны угрожающими"),
  ("gems.enable_gems","true","true (gem drop rate 0.06 вместо 0.1)",
   "самоцветы — часть системы сокетов; реже, потому что сокетов больше чем у ванилы"),
  ("spawner.modify_spawner","true","false",
   "спавнеры в кастомных данжах (WDA/Cataclysm) используют NBT данжа; правка Apotheosis ломает лут-пул данжа"),
  ("worldgen.ore_veins","true","true, но только для тиров 1–2 (см. balance.md)",
   "жилы нужны для горного прогресса, но не должны давать адамантий на спавне")]),

("irons_spellbooks", "Iron's Spells 'n Spellbooks", "config/irons_spellbooks-common.toml + client.toml + server.toml",
 [("maxMana","100 (base attribute)","100 + 15 за уровень таланта (Puffish)",
   "мана — боевой ресурс: 100 хватает на 2 средних заклинания, рост только через таланты/экипировку"),
  ("manaRegenMultiplier","1.0","0.65",
   "иначе на 20-м уровне маг не выходит из боя; 0.65 заставляет пить зелья и использовать посохи с регенерацией"),
  ("spellCooldownMultiplier","1.0","1.15",
   "пакет RPG Series даёт много мгновенных скиллов — кулдаун компенсирует"),
  ("castAnimationOverridesAttack","false","true",
   "совместимость с Better Combat: каст не должен проигрывать замах меча"),
  ("mobSpellcastersEnabled","true","true, но school_weights: fire 30 / ice 25 / lightning 20 / ender 15 / blood 10",
   "мобы-кастеры — источник угрозы тира 2+; веса ограничивают самый сломанный (blood)"),
  ("lootInChests","true","true, scroll chance 0.12",
   "свитки в сундуках — основной способ выучить школу без «покупки в лавке»")]),

("bettercombat", "Better Combat", "config/bettercombat/ (client/server json)",
 [("attack.attackRange","3.0","2.9 (мечи), 3.2 (копья), 2.6 (кинжалы)",
   "дальность подогнана под Simply Swords: кинжал должен требовать сближения"),
  ("attack.sweepMultiplier","0.5","0.35",
   "AOE-замах иначе обесценивает бой с ордами и ломает баланс Iron's Spells"),
  ("dualWield.attackPenalty","0.2","0.28",
   "дуал-вилд с Apotheosis-аффиксами слишком силён; штраф возвращает смысл щиту"),
  ("combo.enabled","true","true, comboWindowTicks=14",
   "окно комбо 0.7 с — не «кнопкодавство», но награда за ритм"),
  ("parry.enabled","false (частично)","true, parryWindowTicks=8, parryStunTicks=12",
   "парирование — механика категории B: 0.4 с окно, 0.6 с стан — учит таймингу без бесконечного контроля")]),

("combat_roll", "Combat Roll", "config/combat_roll.json",
 [("cooldown","30 ticks","22 ticks","перекат должен быть тактикой, а не стилем передвижения"),
  ("invulnerabilityTime","10 ticks","6 ticks","i-frames 0.3 с: уклонение возможно, но не «бессмертие»"),
  ("staminaCost","8","12","связка с выносливостью First Aid-независимой шкалой (см. liveskills.md)"),
  ("distance","3.0","3.2","перекат выводит из зоны удара обычного моба, но не из боссовой арены"),
  ("allowRollDuringAttack","true","false","иначе каст+перекат = непробиваемая комбинация")]),

("firstaid", "First Aid", "config/firstaid-common.toml",
 [("healthPerPart","20","0 (использовать процентную модель)","иначе сумма частей ≠ max HP Apotheosis"),
  ("usePercentage","false","true","обязательная совместимость с атрибутными бустами Apotheosis/Puffish"),
  ("headDamageMultiplier","1.5","1.5","хедшот = смертельно — поощряет шлем и позиционирование"),
  ("legsBreakSpeedPenalty","0.5","0.4","перелом ноги: -60 % скорости, лечится шиной (крафт Farmer's Delight)"),
  ("debuffOnShieldedHit","true","false","магический щит Iron's Spells должен поглощать удар без травмы"),
  ("damageOnDeath","true","false (вместо этого — Corail Tombstone)","двойной штраф за смерть запрещён дизайном «честного хардкора»")]),

("toughasnails", "Tough As Nails", "config/toughasnails-common.toml",
 [("thirst.enabled","true","true, thirstDepletionRate 0.85","жажда — базовый цикл, но не должна требовать пить каждые 3 минуты"),
  ("temperature.enabled","true","true, temperatureModifier 0.9","мягче дефолта: First Aid уже даёт травмы"),
  ("seasonalTemperatureModifier","false","true (с Serene Seasons)","зимой нужна одежда — это гейт, а не наказание"),
  ("purifiedWaterBottleStackSize","1","8","QoL: иначе рюкзак занят бутылками весь тир 1")]),

("serene_seasons", "Serene Seasons", "config/sereneseasons/seasons.toml",
 [("seasonCycleTicks","240000 (10 дней)","480000 (20 игровых дней)","20 дней = успеваешь посеять и собрать дважды; 10 дней фрустрирует"),
  ("startingSeason","SPRING","SPRING","старт всегда в весну — новичок не наказан слепым выбором"),
  ("cropsIgnoreSeason","false","false","сезон должен блокировать фермерство (навык I.3), кроме теплиц"),
  ("subSeasonTicks","24000","24000 (1 игровой день)","плавные переходы, нет шока от смены сезона"),
  ("snowInWinter","true","true, но только выше Y=90","снег по всему миру = проблемы с CTOV и Terralith")]),

("projectmmo", "Project MMO", "config/pmmo/*.json (settings, perks, requirements)",
 [("general.xpGainMultiplier","1.0","0.75","пак даёт 4 навыка × много действий: без множителя 0.75 прокачка до 100 занимает <20 ч"),
  ("general.maxLevel","100","100 (Mining/Farming/Fishing/Cooking/Husbandry), 50 (Crafting)","100 — долгая цель; Crafting быстрее, т.к. меньше действий"),
  ("general.levelCurve","quadratic","quadratic, baseXpPerLevel 120","кривая должна «выпрямляться» на 60+: см. таблицу в liveskills.md"),
  ("requirement.enforce","true","true для предметов тира 3+ (адамантий, мифрил, элитные инструменты)","гейтинг экипировки по навыку — ключ к «ремесло важно»"),
  ("perks.enabled","true","true (только пассивные: +HP, +скорость добычи, +шанс дропа)","активные перки дублируют дерево талантов Puffish"),
  ("salvage.enabled","false","true, salvageRatio 0.35","разбор снаряжения → материалы: связывает Кузнечное дело и экономику")]),

("puffish_skills", "Pufferfish's Skills", "config/puffish_skills/config.json + skills/*.json",
 [("pointsPerLevel","1","1","1 очко за уровень XP: 30 уровней = 30 очков из ~140 нужных на всё дерево"),
  ("startPoints","0","3","3 стартовых очка = «выбор при создании» (см. SPEC §8)"),
  ("respec.enabled","false","true, cost 1 «Эхо Раскола» (крафт)","респек есть, но платный — выбор значим"),
  ("maxPoints","∞","120","потолок: нельзя выкупить всё дерево за гринд"),
  ("categories","—","4 ветки: Path of the Blade / Arcana / Wilds / Fortune, по 8–12 узлов","30+ узлов обязательно; синергии на пересечении веток (см. quest-tree.md)")]),

("origins", "Origins (Forge)", "config/origins/ + world/datapacks/01_origins_plus_plus",
 [("origin_selection_screen","true","true, forced_on_first_join: true","выбор расы — обязательный шаг, без него пак не начинается"),
  ("allow_orb_of_origin","false","false (только за 1 «Эхо Раскола» + 30 уровень)","смена расы — поздняя награда, не кнопка"),
  ("power_cooldowns.mobility","default","×1.2","мобильные пассивки (прыжок, планер) не должны обесценивать маунтов"),
  ("layers","origin, class (2 слоя)","origin + class + 3 talent-слоя через KubeJS","3 слоя = раса/класс/таланты, как в спеке")]),

("kubejs", "KubeJS", "kubejs/config/common.properties + startup/server/client_scripts",
 [("announceReload","true","false","консольный спам в мультиплеере"),
  ("packmode","normal","normal (expert — только для сезонного ивента)","packmode позволяет переключать баланс без пересборки"),
  ("enableRecipeLogging","false","true (только на этапе сборки)","нужен для отладки унификации рецептов"),
  ("script_priority","—","серверные скрипты: 1) unification 2) tags 3) reputation 4) quests bridge","порядок важен: теги должны существовать до проверок")]),

("terralith", "Terralith", "config/terralith.json (или datapack-конфиг)",
 [("terrain.enabled","true","true","рельеф Terralith оставляем, Tectonic накладывает форму сверху"),
  ("biome_size","2","1.5","уменьшение размера биомов → больше разнообразия в радиусе прогулки, но без «лоскутности»"),
  ("structure_density","1.0","1.0","структуры регулируем на стороне WDA/YUNG's, а не тут")]),

("tectonic", "Tectonic", "config/tectonic.json",
 [("terrain_scale","1.4","1.0","1.4 даёт горы высотой 400+ — мобы застревают, деревни в воздухе; 1.0 — «эпично, но играбельно»"),
  ("continentalness","default","усиленный (+15 %)","нужны настоящие континенты для кораблей Small Ships"),
  ("village_flatten","false","true","CTOV-деревни должны стоять ровно"),
  ("cave_carving","true","true, но с cave_scale 0.85","иначе пещеры прорезают горы насквозь и ломают YUNG's Mineshafts")]),

("ctov", "ChoiceTheorem's Overhauled Village", "config/ctov/*.json",
 [("useBiomeTags","false","true","обязательно для Terralith: иначе деревни только в ванильных биомах"),
  ("maxSlope","8","12","чуть мягче: у Tectonic крутые склоны, иначе деревни пропадают"),
  ("flattenTerrain","false","true","посадка домов на рельеф Tectonic"),
  ("villageSpacing","34","40","деревни — центры квестов; 40 чанков = «дойти за 10 минут», а не «через одну»"),
  ("villagerCount","vanilla","+25 % (но не более 18 на деревню)","нужны NPC для 5 фракций и квестодателей")]),

("wda", "When Dungeons Arise", "config/wda.cfg (server)",
 [("structureWeight","10","5","70+ данжей на дефолте превращают мир в «данж-парк»"),
  ("spacing","20","34","разносим структуры, чтобы между ними была «пустая» природа"),
  ("separation","8","12","исключает наложение данжей"),
  ("dungeonLootMultiplier","1.0","0.85","лут тирингуем через LootJS, множитель чуть ниже — компенсация количества"),
  ("enableNetherStructures","true","false","ад отдан Incendium — иначе двойные структуры")]),

("gateways", "Gateways to Eternity", "config/gateways/gateways.json",
 [("waveCount","10","5 (тир 1) … 12 (тир 5)","волны = «рогалик-слой» данжей: 5 волн хватает на тир 1"),
  ("rewardLootTable","gateways:default","кастомная: aetherfall:gateway_tier_<n>","награда должна соответствовать тиру, а не быть случайной"),
  ("mobScaling","false","true, scalingPerWave 1.12","каждая волна +12 % HP/урона — иначе поздние волны тривиальны"),
  ("gatewayCooldown","0","6000 ticks (5 мин)","нельзя фармить бесконечно в одной точке")]),

("cataclysm", "L_Ender's Cataclysm", "config/cataclysm-common.toml",
 [("bossHealthMultiplier","1.0","0.85","Cataclysm-боссы рассчитаны на «сильного игрока без пака»; у нас 3 источника аффиксов — снижаем HP"),
  ("bossDamageMultiplier","1.0","1.0","урон не трогаем: угроза должна остаться"),
  ("structureRarity","default","+35 % реже (config: structure_spacing)","8 боссов не должны стоять через 200 блоков"),
  ("allowBossMusic","true","true","атмосфера — категория E")]),

("mowzies", "Mowzie's Mobs", "config/mowziesmobs-common.toml",
 [("spawnRateMultiplier","1.0","0.8","мобы Mowzie сильны для раннего тира — реже спавн"),
  ("bossBar","true","true","—"),
  ("generateStructures","true","true, но spacing 32","структуры боссов не должны мешать деревням")]),

("alexsmobs", "Alex's Mobs", "config/alexsmobs.toml",
 [("spawnRates.global","1.0","0.85","90+ мобов при дефолте вытесняют ванильную фауну и ванильных врагов"),
  ("dangerousMobSpawnRate","1.0","0.9","—"),
  ("mobSpawnBiomeWeights","default","оставить","фауна по биомам — ядро «экосистемы»"),
  ("enableLavaSquid","true","false","бесполезный моб, ломает баланс рыбалки в аду")]),

("alexscaves", "Alex's Caves", "config/alexscaves-general.toml",
 [("caveBiomeRarity","1.0","0.8","6 подземных биомов при 1.0 перекрывают друг друга"),
  ("caveBiomeDistance","default","+20 % (разносим)","игрок должен «путешествовать», а не падать из одного биома в другой"),
  ("biomeAmbience","true","false (при включённых шейдерах)","конфликт с Oculus (см. conflicts 5.7)"),
  ("nostalgiaMode","false","true (ограничить пресеты тиром)","опционально: часть контента только после тира 3")]),

("iceandfire", "Ice and Fire", "config/iceandfire-common.toml",
 [("generateDragonSkeletons","true","true, но реже (spacing 40)","—"),
  ("dragonSpawnChance","1.0","0.6","драконы — эндгейм-маунты; при 1.0 небо закрыто драконами"),
  ("dragonBlockBreaking","true","false до тира 4 (событие «Пробуждение»)","иначе дракон сносит деревню новичка"),
  ("generateCyclops","true","true","—"),
  ("hippogryphSpawnChance","1.0","0.5","летающий маунт должен быть редкой находкой")]),

("twilightforest", "Twilight Forest", "config/twilightforest-common.toml",
 [("progressionRules","true","true","запрет входа в поздние зоны до убийства босса — родной гейтинг, не выключать"),
  ("portalCreation","true","true, но требуется «Ключ Вейла» (крафт тир 2)","портал не должен быть доступен на 10-й минуте"),
  ("bossHealth","vanilla","×1.0","TF-боссы сбалансированы, бусты не нужны")]),

("aether", "The Aether", "config/aether-common.toml",
 [("spawnRateWhirlwind","default","0.8","—"),
  ("accessorySlotCount","8","оставить 8 (Curios-независимые)","внимание: свои слоты, не Curios — не конфликтуют"),
  ("startupLoot","true","true (стартовые книги в сундуке портала)","")]),

("croptopia", "Croptopia", "config/croptopia.json",
 [("generateSeeds","true","true, но seedDropChance 0.45","60+ культур не должны заполнить всю траву"),
  ("growthChance","default","×0.9","чуть медленнее — ценность фермерства"),
  ("enableSaltOre","true","true (нужен для готовки)","")]),

("farmersdelight", "Farmer's Delight", "config/farmersdelight-common.toml",
 [("enableRichSoil","true","true","—"),
  ("enableVanillaCropLootModification","true","true, но с шансом 0.25","ножи дают больше урожая — регулируем"),
  ("enableTomatoVineTreasure","true","true","")]),

("aquaculture", "Aquaculture 2", "config/aquaculture.json",
 [("enableLoot","true","true","—"),
  ("fishCatchChance","default","уменьшить редких на 20 %","30+ рыб: редкие должны быть редкими"),
  ("neptuniumEnchantability","default","+1","нептуниум — награда за навык рыбалки 40+")]),

("productivebees", "Productive Bees", "config/productivebees-common.toml",
 [("beeRarity","default","+30 % к редкости редких пчёл","генетика должна требовать усилий"),
  ("generateBeeNests","true","true, но не чаще 1 на 3 чанка",""),
  ("advancedBeehives","true","true после тира 3","")]),

("diet", "Diet", "config/diet/diet_groups.json + diet.json",
 [("nutrient_decay_rate","default","0.75× (медленнее)","5 нутриентов + жажда + травмы — слишком много давления"),
  ("apply_nutrients_to_drinks","true","false","напитки не должны кормить"),
  ("death_penalty","default","сброс 25 % нутриентов","смерть и так наказывает (могила)")]),

("corail_tombstone", "Corail Tombstone", "config/tombstone-common.toml",
 [("graves.grave_effects","soulbound etc.","только grave_soulbound для квестовых предметов",""),
  ("death_handling.keep_inventory","false","false, но degradation_time 45 мин","вещи сохраняются 45 минут — «честная» смерть"),
  ("loss_penalty.xp_loss","default","5 % (вместо 30 %)","штраф есть, но не откат на час"),
  ("angel_of_death.enabled","true","false","не хотим «бесплатных» телепортов к могиле"),
  ("grave_key.enabled","true","true","ключ — крафт, не покупка")]),

("ftbquests", "FTB Quests", "config/ftbquests/ (server: quests.json — в датапаке)",
 [("disable_gui_recipe_locking","false","true","гейтинг рецептов ломает Tetra/EMI-подсказки"),
  ("drop_item_rewards","true","false","награды — предметы в инвентарь, без «выпало на пол»"),
  ("hide_until_unlocked","false","true","не показывать главы тира 5 новичку"),
  ("team_sharing","true","true","кооп в MP обязателен (5–10 игроков)"),
  ("quest_refresh_days","—","3 игровых дня (KubeJS-ротация)","см. reputation-system.md §J.3")]),

("bountiful", "Bountiful", "config/bountiful/bountiful.json",
 [("bountyRefreshTime","24000 ticks (1 день)","48000 (2 дня)","доска не должна быть станком для фарма"),
  ("maxBounties","3","3 (тир 1–2), 5 (с репутацией Почёт)","связка с репутацией"),
  ("rewardMultiplier","1.0","0.9","Bountiful — «мелкая работа», а не основной доход")]),

("easynpc", "Easy NPC", "config/easy_npc/ + скрипты пака",
 [("enableTrading","true","true, но цены только через KubeJS","4 мода меняют торговлю — один владелец"),
  ("defaultInteraction","right-click","right-click + F (анкор)","F удобнее для квестов"),
  ("lookAtPlayerRange","8","12","диалоги начинаются при взгляде — спека J.3")]),

("guardvillagers", "Guard Villagers", "config/guardvillagers.json",
 [("guardCountPerVillage","2","4","деревня должна переживать первую ночь, но не быть неприступной"),
  ("attackHostilePlayers","false","true (через тег #aetherfall:hostile_to_guards)","негативная репутация → агрессия стражи"),
  ("guardFollowRange","16","20","")]),

("waystones", "Waystones", "config/waystones-server.toml",
 [("costPerTeleport","0","8 монет × расстояние/100","экономика Numismatic Overhaul как топливо"),
  ("allowGlobalWaystones","true","false до тира 3","иначе путешествие/логистика обесценены"),
  ("generateInVillages","true","true (1 на деревню)","точка телепорта = центр квестов")]),

("numismatic", "Numismatic Overhaul", "config/numismatic.json",
 [("coinDropChance","0.35","0.3","деньги из мобов — не основной доход"),
  ("villagerTradesUseCoins","true","true","валюта для репутационной торговли"),
  ("coinStackSize","64","64","")]),

("jei", "JEI", "config/jei/jei-client.toml + world/client config",
 [("hideMode","default","MOD_NAME (скрывать предметы по вкладке мода)","238 модов: без скрытия вкладки не находимы"),
  ("search.history","true","true",""),
  ("enableBookmarking","true","true",""),
  ("plugins.hideMobSpawnInfo","false","false","нужна информация о мобах (JER)")]),

("journeymap", "JourneyMap", "config/journeymap/journeymap.cfg",
 [("mapping.enabled","true","true на клиенте, false на сервере","серверное картирование = нагрузка на TPS"),
  ("radar.enabled","true","false (античит/честность MP)","радар = читерство в PvP-серверах"),
  ("waypoint.max","80","150","вайпоинты для квестов «найди структуру»"),
  ("journal.enabled","true","true","связка с FTB Quests (журнал открытий)")]),

("jade", "Jade", "config/jade/*.json",
 [("showBlockDetails","true","true",""),
  ("entityHealth","true","true (важно для боссов)",""),
  ("showItemStorage","true","true","")]),

("embeddium", "Embeddium", "config/embeddium-sodium-options.json",
 [("performance.chunk_builder_threads","auto","auto (6 на i5-10400F)",""),
  ("quality.render_distance","12","10","цель 60+ FPS с шейдерами"),
  ("performance.use_no_error_g_l_context","false","true","даёт +2–4 % FPS, отключает GL-проверки (не отлаживать с ним)")]),

("oculus", "Oculus", "config/oculus.properties",
 [("enableShaders","true","true, shaderPack BSL_v8.2.04",
   "BSL — оптимальный баланс «атмосфера/производительность» на RTX 3060"),
  ("shadowQuality","1.0","0.75","тени — главный убийца FPS"),
  ("disableUpdateNotification","false","true","—")]),

("modernfix", "ModernFix", "config/modernfix-mixins.properties",
 [("mixin.perf.dynamic_resources","true","false (конфликт с FerriteCore)",""),
  ("mixin.perf.dedicated_reload_executor","true","true","ускоряет /reload"),
  ("mixin.bugfix.world_leaks","true","false","перекрывает MemoryLeakFix"),
  ("mixin.perf.blast_search_trees","true","true","")]),

("canary", "Canary", "config/canary.properties",
 [("mixin.entity.collisions","true","true",""),
  ("mixin.ai.poi","true","true","важнейшая оптимизация для деревень CTOV"),
  ("mixin.world.block_entity_ticking","true","true","")]),

("entityculling", "EntityCulling", "config/entityculling.json",
 [("tracingDistance","128","64","на 10 чанках 128 — избыточно"),
  ("disableF3","false","true","")]),

("packetfixer", "Packet Fixer", "config/packetfixer.properties",
 [("maxPacketSize","1048576","8388608","200+ модов: теги и рецепты в одном пакете иначе рвут соединение"),
  ("maxPacketSizeServer","1048576","8388608","")]),

("spark", "spark", "config/spark/config.json",
 [("enableProfiling","true","true (только для админов)","диагностика TPS на сервере"),
  ("enableDataBroadcasting","true","false","не светить данные в веб-профили")]),

("tetra", "Tetra", "config/tetra/ + kubejs/server_scripts/tetra_bettercombat.js",
 [("honing.enabled","true","true, honingBonus 0.08","заточка — часть «Кузнечного дела», но не должна заменять аффиксы"),
  ("modules.maxPerItem","default","2 базовых + 2 улучшения","модульный бог-меч ломает тир-гейт"),
  ("workbenchTierGate","false","true (верстак 3-го тира требует Mining 40)","связка навык ↔ экипировка")]),

("curios", "Curios API", "config/curios-common.toml / curios-server.toml",
 [("slots.charm","1","2 (по 1 за репутацию «Уважение» у Алхимиков и Торговцев)","слоты — награда за репутацию"),
  ("slots.ring","2","4 (2 базовых, 2 через таланты)",""),
  ("slots.belt","1","1",""),
  ("slots.back","0","1 (только Sophisticated Backpacks)","второй «спина» = дубль рюкзаков")]),

("sophisticatedbackpacks", "Sophisticated Backpacks", "config/sophisticatedbackpacks-server.toml",
 [("backpackUpgradeSlots","1","2","апгрейды — прогрессия, но не бесконечная"),
  ("stackUpgradeMultiplier","2","2",""),
  ("inventoryInteractionSound","true","false","")]),

("legendarytooltips", "Legendary Tooltips", "config/legendarytooltips.json",
 [("tooltipStyle","default","aetherfall (кастом в ресурспаке пака)","брендинг пака"),
  ("showRarityIcons","true","true","синергия с редкостями Apotheosis"),
  ("compactMode","false","true (→ меньше наложения с Jade)","")]),

("chunky", "Chunky", "config/chunky.json",
 [("radius","5000","3500 (v1.0)","3500 блоков хватает на 3 тира прогрессии; 5000 = +4 часа CPU"),
  ("shape","square","square",""),
  ("silent","false","true","иначе спам в чате")]),

("vampirism", "Vampirism", "config/vampirism-*.toml",
 [("factionNameOverride","Vampirism","Кровный Долг (UI)","не путать с репутацией деревень"),
  ("vampireLevels.maxLevel","14","14",""),
  ("hunterLevels.maxLevel","14","14",""),
  ("villageAggression","true","true (×0.8 частота)","вторжения — ивент, а не фон")]),

("goety", "Goety", "config/goety-common.toml",
 [("minionLimit","default","8 + 1 за каждые 10 уровней Necromancy-ветки","ограничение армии — иначе TPS"),
  ("soulEnergyCost","default","×1.15","некромант не должен быть сильнее мага по ресурсам"),
  ("enableCultists","true","true после тира 3","")]),

("ars_nouveau", "Ars Nouveau", "config/ars_nouveau-common.toml",
 [("manaRegenMultiplier","1.0","0.8","мана Ars — топливо крафта, не боевой ресурс"),
  ("spellDamageMultiplier","1.0","0.75","иначе «самосборные» заклинания обходят Iron's Spells по урону"),
  ("worldgen.archwoodForest","true","true","")]),

("botania", "Botania", "config/botania-common.toml",
 [("passiveFlowerDecay","true","true, decaySpeed ×0.8",""),
  ("enderDaggerDamage","default","×1.0",""),
  ("regenSustainCost","default","×1.1","чуть дороже — баланс маны между модами")]),

("opac", "Open Parties and Claims", "config/openpartiesandclaims-server.toml",
 [("claims.maxClaimsPerPlayer","10","25","базы игроков + деревни"),
  ("claims.blockInteractionsOutsiders","true","false для «дружелюбных» блоков (двери, кнопки)","иначе квесты в деревнях невозможны"),
  ("parties.maxPartySize","8","10 (сервер на 5–10 игроков)","")]),

("voicechat", "Simple Voice Chat", "config/voicechat/voicechat-server.properties",
 [("port","24454","24454 (UDP открыть!)",""),
  ("max_voice_distance","48","32","голос не должен работать через полмира"),
  ("enable_groups","true","true","группы для данж-рейдов")]),

("connectivity", "Connectivity", "config/connectivity.properties",
 [("loginTimeoutSeconds","30","90","200+ модов: логин с реестрами идёт 40–70 с"),
  ("handshakeTimeoutSeconds","default","60","")]),

("lootjs", "LootJS (скрипты пака)", "kubejs/server_scripts/loot/*.js",
 [("tiered_loot_rule","—","тир 1: железо/кожа; тир 3: алмаз/апофеоз rare; тир 5: mythic + фрагменты артефактов","лут должен соответствовать тиру локации, а не мобу"),
  ("boss_unique_drops","—","1 гарантированный уникальный дроп с каждого из 26 боссов",""),
  ("remove_vanilla_dupes","—","удалить дубли руд/слитков (unification) через LootJS + KubeJS recipes","")]),

("kubejs_scrub", "KubeJS — чистка JEI (скрипт пака)", "kubejs/client_scripts/hide_items.js",
 [("hidden_categories","—","технические предметы (spawn eggs кастомных мобов, пустые вёдра, debug-блоки)","238 модов: без чистки в JEI 6000+ записей"),
  ("hide_mode","—","скрывать только бесполезное, не «сложное»","новичок должен видеть сложные предметы — это мотивация")]),
]

TEMPLATE = """# ============================================================================
#  {name}  —  конфиг пака Aetherfall 1.0.0
#  Файл(ы) в инстансе: {path}
#  Формат: не копируй целиком как .json/.toml — это карта значений.
#          Значения «рекомендуемое» вноси в соответствующий ключ файла мода.
#  Обоснование: строка «почему» = причина, привязанная к дизайну пака.
# ============================================================================

# --- Параметры ---------------------------------------------------------------
{block}
# --- Чек-лист применения -----------------------------------------------------
#  [ ] Значения внесены и мод перезапущен (некоторые требуют полного рестарта)
#  [ ] Проверено в игре: /reload или новый мир
#  [ ] Отмечено в config/checklist.md
#  [ ] Если параметр не найден в текущей версии мода — зафиксировать в SPECIFICATION.md §7.9 (отклонения)
"""

def esc(s): return s.replace("\n"," ").strip()

for mid, name, path, params in MODS:
    w = max(len(p[0]) for p in params)
    block = []
    for key, default, rec, why in params:
        block.append(f"# {why}")
        block.append(f"{key}")
        block.append(f"    по умолчанию : {esc(default)}")
        block.append(f"    РЕКОМЕНДУЕТСЯ: {esc(rec)}")
        block.append("")
    open(os.path.join(OUT, f"{mid}.conf"), "w", encoding="utf-8").write(
        TEMPLATE.format(name=name, path=path, block="\n".join(block)))
print("файлов:", len(MODS))
