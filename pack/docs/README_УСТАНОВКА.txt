==========================================================
 СБОРКА "Sborka RPG" — уютная RPG-песочница
 Minecraft 1.20.1 · Fabric · ~105 модов · оптимизировано под слабые ПК
==========================================================

ЧТО ВНУТРИ АРХИВА
  client/            ← готовый клиентский инстанс (mods, config, options.txt)
  server/            ← готовый сервер (mods, server.properties, eula.txt)
  README_УСТАНОВКА.txt ← этот файл

----------------------------------------------------------
1. УСТАНОВКА КЛИЕНТА (самый простой способ — Prism Launcher)
----------------------------------------------------------
Вариант А (рекомендуется): файл *.mrpack
  1) Скачай и установи Prism Launcher (бесплатный, prismlauncher.org).
  2) Prism → Add Instance → Modrinth → «Import from file» → выбери .mrpack.
  3) Prism сам скачает нужную версию Fabric (Fabric Loader 0.20.1) и все моды.
  4) Выдели памяти: Settings → Instance → Memory → 3 ГБ (минимум 2.5 ГБ).

Вариант Б: папка client/
  1) Поставь Fabric Loader 0.20.1 для Minecraft 1.20.1 (fabricmc.net/use).
  2) Скопируй содержимое client/ в папку инстанса (туда же, где лежит mods).
  3) Запусти игру.

----------------------------------------------------------
2. УСТАНОВКА СЕРВЕРА (если хочешь играть с друзьями)
----------------------------------------------------------
  1) Скопируй папку server/ на машину с Java 17+.
  2) Первый запуск: java -Xmx3G -jar fabric-server-launch.jar nogui
     (файл fabric-server-launch.jar скачается скриптом установки или возьми
      готовый из официального установщика Fabric для 1.20.1 / loader 0.20.1)
  3) В eula.txt уже стоит eula=true.
  4) В server.properties уже выставлены слабые настройки (view-distance=6).

----------------------------------------------------------
3. НАСТРОЙКИ ДЛЯ СЛАБОГО ПК (уже применены в options.txt)
----------------------------------------------------------
  • renderDistance 6, simulationDistance 5, графика Fast, частицы уменьшены
  • шейдеры ВЫКЛЮЧЕНЫ (config/iris.properties.example)
  • Sodium + Lithium + Krypton + C2ME + ImmediatelyFast + EntityCulling + More Culling
  • Если всё ещё лагает: Sodium Options → Graphics «Fast», renderDistance 4,
    и отключи в Mod Menu: Falling Leaves, Visuality, Not Enough Animations,
    Ambientsounds (Deleting: они чисто косметические).
  • Если FPS высокий и хочется красоты: включи шейдеры (Complementary Reimagined)
    и подними renderDistance до 10–12.

----------------------------------------------------------
4. ЧТО ЕСТЬ В СБОРКЕ (кратко)
----------------------------------------------------------
  Расы/классы: Origins + Medieval Origins Revival + Origins++ + Extra Origins
               + Origins: Classes + OriginsTweaks (~120 рас)
  Квесты:      Odyssey Quests (дерево заданий) + Bountiful (контракты на доске
               у жителей деревни — «квесты у жителей»)
  Рыбалка:     Tide 2, Fish of Thieves, Fishing Real, Random Fishing Crates,
               Enchanted Fishing Line
  Готовка:     Farmer's Delight + More Delight + End's Delight +
               Cooking for Blockheads + Farm & Charm + Vinery + Candlelight
  Фермерство:  Overweight Farming, Farming for Blockheads (рынок семян),
               Serene Seasons (сезоны), Smarter Farmers (жители пересеивают)
  Деревни:     ChoiceTheorem's Overhauled Village, Towns & Towers,
               Villages & Pillages, Dungeons & Taverns, VillagersPlus,
               Guard Villagers, Villager Names, Trade Cycling
  Магия/бой:   Wizards, Jewelry, Paladins & Priests, Archers, Rogues & Warriors,
               Simply Swords, Better Combat, Combat Roll, Artifacts, RPG Difficulty
  Мир:         Terralith, Incendium, Structory (+Towers), YUNG's Better Dungeons
               & Mineshafts, When Dungeons Arise, Deeper and Darker
  Уют/декор:   Handcrafted, Twigs, Supplementaries, Waystones, Inmis (рюкзаки),
               Comforts (спальники), Nature's Compass
  Атмосфера:   AmbientSounds, Presence Footsteps, Immersive Melodies,
               Falling Leaves, Visuality, Eating Animation, Visual Workbench,
               Traveler's Titles
  Фауна:       Critters and Companions, Naturalist, Friends & Foes

----------------------------------------------------------
5. ПЕРВЫЕ ШАГИ В ИГРЕ
----------------------------------------------------------
  1) При первом входе выбери расу (Origins) и класс (Origins: Classes).
  2) Открой квесты: клавиша «J» (Odyssey Quests) — там ветки «Деревня»,
     «Рыбалка», «Кухня», «Магия».
  3) Найди деревню и доску контрактов (Bountiful) — это задания от жителей.
  4) Построй кровать и спальник (Comforts), поставь Waystone для телепортов.
  5) Нажми «R» для просмотра рецептов (REI), «M» — миникарта.

----------------------------------------------------------
6. ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК
----------------------------------------------------------
  • Игра не запускается: проверь, что выделено ≥3 ГБ ОЗУ и Java 17
    (в Prism: Settings → Java → 17.0.x).
  • Конфликт модов: пришлите logs/latest.log — в сборке уже проверены
    зависимости, но обновления модов могут изменить ситуацию.
  • Сервер: «Can't keep up» при генерации нового мира — это нормально,
    дай ему 5–10 минут прогрева (или используй Chunky для предгенерации).

Приятной игры! Сборка собрана и протестирована автоматически:
все 105 модов прошли проверку зависимостей, а серверный запуск с полным
набором модов завершился успешно (см. отчёт в репозитории).
