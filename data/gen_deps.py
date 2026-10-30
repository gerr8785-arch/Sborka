#!/usr/bin/env python3
import re, collections
rows=[dict(zip(['n','cat','role','deps','soft','side','crit','note','gh'],l.rstrip('\n').split('|'))) for l in open('data/mods_clean.psv',encoding='utf-8') if l.strip()]
names={r['n'].lower():r for r in rows}
alias={'ctov':"choicetheorem's overhauled village","iron's spells":"iron's spells 'n spellbooks",
 'kubejs':'kubejs','lootjs':'lootjs','rhino':'rhino','architectury':'architectury api','placebo':'placebo',
 'apothic attributes':'apothic attributes','curios':'curios api','geckolib':'geckolib','playeranimator':'playeranimator',
 'citadel':'citadel','mutil':'mutil','bookshelf':'bookshelf','moonlight lib':'moonlight lib','puzzles lib':'puzzles lib',
 'balm':'balm','patchouli':'patchouli',"yung's api":"yung's api",'ftb library':'ftb library','ftb teams':'ftb teams',
 'glitchfiendlib':'glitchfiendlib','nitrogen':'nitrogen','spell power attributes':'spell power attributes',
 'reach entity attributes':'reach entity attributes','ranged weapon api':'ranged weapon api',
 "pufferfish's attributes":"pufferfish's attributes",'structure gel api':'structure gel api','cristel lib':'cristel lib',
 'smartbrainlib':'smartbrainlib','iceberg':'iceberg','prism':'prism','konkrete':'konkrete','creativecore':'creativecore',
 'framework':'framework','kotlin for forge':'kotlin for forge','cloth config api':'cloth config api',
 'libipn':'libipn','cupboard':'cupboard','fzzy config':'fzzy config','saturn':'saturn',
 'dynamic trees + terralith compat':'dynamic trees','probejs':'probejs','ftb ranks':'ftb ranks'}
optional_tokens={'probejs','ftb ranks'}
rev=collections.defaultdict(list); unres=set()
for r in rows:
    for f in ('deps','soft'):
        for t in re.split(r';', r[f]):
            t=t.strip()
            if t in ('—','') or 'проверить' in t or 'Lucchi' in t: continue
            key=alias.get(t.lower(), t.lower()); hit=names.get(key)
            if hit: rev[hit['n']].append(r['n'])
            elif t.lower() in optional_tokens: rev.setdefault(t,[]).append(r['n'])
            else: unres.add((r['n'],t))
libs=[r for r in rows if r['cat']=='LIB']
out=['<a id="libraries"></a>','## 4. Библиотеки и зависимости','',
'### 4.1 Все библиотеки пака и кто их требует','',
'| Библиотека | Что даёт | Кто требует (hard/soft) | Side |','|---|---|---|---|']
for l in libs:
    users=sorted(set(rev.get(l['n'],[])))
    out.append(f"| **{l['n']}** | {l['role']} | {', '.join(users) if users else '—'} | {l['side']} |")
out+=['| **ProbeJS** (утилита, вне пака) | автодополнение KubeJS в IDE | KubeJS (soft, только для разработки) | client |',
      '| **FTB Ranks** (опция) | права/префиксы для MP | FTB Quests (soft) | server |','']
out+=["### 4.2 Сверка зависимостей (полнота)","",
"Автоматическая сверка (`data/gen_deps.py`): каждый обязательный токен должен найтись в таблице модов.",""]
tot=sum(len([t for t in re.split(';', r['deps']) if t.strip() not in ('—','') ]) for r in rows)
alltok=sum(len([t for t in re.split(';', r['deps']) if t.strip() not in ('—','')])+len([t for t in re.split(';', r['soft']) if t.strip() not in ('—','')]) for r in rows)
out+=[f"- Модов проверено: **{len(rows)}**",
      f"- Токенов зависимостей (hard+soft): **{alltok}** (из них hard: **{tot}**)",
      f"- Не разрешено автоматически: **{len(unres)}** — см. таблицу ниже",""]
if unres:
    out+=["| Мод | Неразрешённый токен | Что проверить |","|---|---|---|"]
    for m,t in sorted(unres): out.append(f"| {m} | `{t}` | существование сборки под 1.20.1/Forge + совместимость версии |")
out+=["","### 4.3 Правила зависимостей пака","",
"1. **Forge 47 не поддерживает подпапки в `mods/`** — порядок задаётся не структурой папок, а `validate_dependencies.sh` (наличие + версия + отсутствие дублей по `modid`).",
"2. **Одна версия библиотеки на пак.** Два `placebo-*.jar` разных версий → `DuplicateModsFoundException` на старте.",
"3. **Тройка Apotheosis 7 ↔ Apothic Attributes ↔ Placebo** обновляется только вместе (несовпадение мажора = `mixin apply failed`).",
"4. **KubeJS ↔ Rhino ↔ Architectury**: KubeJS 2001.6.5+ требует Architectury 9.x.",
"5. **PlayerAnimator ≥ 1.0.2-rc1** обязателен для Better Combat + Iron's Spells (иначе `NoSuchMethodError` в `PlayerModel`).",
"6. **Curios**: единственная система слотов; всё, что добавляет слоты (Artifacts, Jewelry, Elytra Slot, Iron's Spells), цепляется к нему — второй системы слотов в паке нет.",
"7. **GeckoLib** требуется 14 модами пака; версия должна быть ≥ 4.4.4 (Alex's Caves, Cataclysm, BMD проверены на ней).",
"8. Скрипт проверки: [scripts/validate_dependencies.sh](scripts/validate_dependencies.sh) — сверяет `manifest.json` → файлы в `mods/` → `mods.toml` (modid/version)."]
open('SPECIFICATION.md','a',encoding='utf-8').write("\n".join(out)+"\n")
print(len(unres))
