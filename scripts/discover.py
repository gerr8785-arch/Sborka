import json, urllib.parse, urllib.request, time

API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "sborka-pack-builder/1.0 (contact: repo owner)"}

def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(2 + attempt * 2)

def search(q, limit=8, mc="1.20.1", loader="fabric"):
    facets = json.dumps([["project_type:mod"], [f"versions:{mc}"], [f"categories:{loader}"]])
    url = f"{API}/search?query={urllib.parse.quote(q)}&limit={limit}&facets={urllib.parse.quote(facets)}&index=relevance"
    return get(url)

QUERIES = [
 "sodium","performance","shaders","fishing","aquaculture","farmer","farming","cooking","food",
 "quests","quest","villager","villages","race","origins","rpg","magic","spell","weapon",
 "backpack","storage","decoration","furniture","cozy","seasons","structures","worldgen","biomes",
 "map","minimap","waystones","trade","professions","animals","pets","dragons","bosses","dungeons",
 "crops","bees","alchemy","smithing","mounts","horses","companions","sound","ambient","weather",
 "inventory","sorting","quality of life","library","api","compat","delight","lets do","tectonic","terralith",
]
out = []
for q in QUERIES:
    try:
        res = search(q)
    except Exception as e:
        out.append(f"\n### {q}\nERROR {e}\n")
        continue
    out.append(f"\n### {q}\n")
    for h in res.get("hits", []):
        dl = h["downloads"]
        out.append(f"- `{h['slug']}` | {h['title']} | {dl//1000}k dl | {', '.join(h['display_categories'][:6])} | {h['description'][:110]}")
print("\n".join(out))
