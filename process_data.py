import json, xmltodict
import mwparserfromhell
import gzip
import bz2
import re

DUMP_ARTICLES = "simplewiki-20260101-pages-articles-multistream.xml.bz2"
DUMP_PAGELINKS = "simplewiki-20260101-pagelinks.sql.gz"
OUT_JSON = "smoldata.json"

all_categories = {}
all_pages = {}

# === MzansiPedia SA Filter ===
SA_CATEGORY_PATTERNS = [
    "south africa", "south african",
    "cape colony", "natal colony",
    "apartheid in south africa",
    "provinces of south africa",
    "ethnic groups in south africa",
    "world heritage sites in south africa",
    "settlements in south africa",
    "history of south africa",
    "culture of south africa",
    "geography of south africa",
    "economy of south africa",
    "environment of south africa",
    "government of south africa",
    "politics of south africa",
    "society of south africa",
    "health in south africa",
    "sport in south africa",
    "military of south africa",
    "religion in south africa",
    "languages of south africa",
    "transport in south africa",
    "education in south africa",
    "buildings and structures in south africa",
    "organisations based in south africa",
    "south african people",
    "films set in south africa",
    "television series set in south africa",
    "television shows set in south africa",
    "deaths in south africa",
]

SA_TITLE_KEYWORDS = [
    # Provinces and major cities
    "cape town", "johannesburg", "durban", "pretoria", "soweto",
    "port elizabeth", "bloemfontein", "kimberley", "polokwane",
    "nelspruit", "rustenburg", "stellenbosch", "franschhoek",
    "knysna", "hermanus", "george (south africa)",
    "gauteng", "western cape", "eastern cape", "kwaZulu-natal",
    "limpopo", "free state", "north west", "northern cape",
    # Landmarks and nature
    "table mountain", "kruger national park", "robben island",
    "drakensberg", "augrabies", "cape of good hope", "garden route",
    "big five", "fynbos", "bushveld", "karoo", "cape point",
    "tsitsikamma", "blyde river canyon", "sossusvlei",
    # Key historical figures
    "nelson mandela", "oliver tambo", "robert sobukwe", "steve biko",
    "desmond tutu", "chris hani", "helen susman",
    "fw de klerk", "thabo mbeki", "jacob zuma", "cyril ramaphosa",
    "shaka", "dingane", "mpande",
    # Culture and history
    "apartheid", "boer war", "voortrekker", "zulu kingdom",
    "south african cuisine", "biltong", "bobotie", "bunny chow",
    "amapiano", "kwaito", "maskandi", "mbube",
    "sangoma", "inyanga", "matric dance", "shebeen",
    "izikhothane", "pantsula", "gumboot dance",
    # Sport
    "springboks", "bafana bafana", "south african rugby",
    "cricket south africa", "currie cup", "premier soccer league",
    # Languages
    "afrikaans", "isizulu", "isixhosa", "sesotho",
    "setswana", "tshivenda", "siswati", "isindebele",
    "xitsonga", "south african english",
    # Government and institutions
    "south african parliament", "nelson mandela foundation",
    "south african reserve bank", "sasol", "gold fields",
    "south african film",
]

SA_TITLE_KEYWORDS_SET = {kw.lower() for kw in SA_TITLE_KEYWORDS}

def is_mzansi_page(title, categories):
    """Check if a page is South Africa-related."""
    cats_lower = [c.lower() for c in categories]
    for cat in cats_lower:
        if any(pattern in cat for pattern in SA_CATEGORY_PATTERNS):
            return True
    title_lower = title.lower()
    if any(kw in title_lower for kw in SA_TITLE_KEYWORDS_SET):
        return True
    return False

def process_page(xml):
    page = xmltodict.parse(xml)["page"]
    title = page["title"]
    try:
        text = page["revision"]["text"]["#text"]
    except KeyError:
        return
    if text.upper().startswith("#REDIRECT"):
        return
    text_toparse = text
    #text_toparse = re.sub('\\[\\[File:[^\\]]+\\]\\]\\n?', '', text_toparse)
    #text_toparse = re.sub('{{Infobox(?:[^{}]+(?:{{(?:[^{}]+(?:{{[^}]+}}|}))+}|}))+}', '', text_toparse, flags=re.MULTILINE)
    text_toparse = "\n".join(x for x in text_toparse.split("\n") if not x.startswith("thumb|") if not x.upper().startswith("__NOTOC__") and (len(x) == 0 or not x[0] in "{}[]|&<>-*= ")).strip("\n")
    text_toparse = re.sub(r'<ref[^>]*>.*?</ref>', '', text_toparse, flags=re.DOTALL)
    text_toparse = "\n".join(text_toparse.split("\n\n")[0].split("\n")[:8])
    #print(f"< {title} >")
    parsed_text = mwparserfromhell.parse(text_toparse).strip_code().strip()
    while len(parsed_text) > 300 and len(dot_split:=parsed_text.split(".")) > 2:
        parsed_text = ".".join(dot_split[:-2]) + "."
    while len(parsed_text) > 300 and len(dot_split:=parsed_text.split("\n")) > 2:
        parsed_text = "\n".join(dot_split[:-1])
    #print(parsed_text)
    categories = [cat.split("|")[0].split("]")[0].strip().replace(u"\u200E","").replace(u"\u200F","").replace("_", " ") for cat in text.lower().split("[[category:")[1:]]
    if "{{songs category" in text.lower():
        categories.append(title.lower().replace("category:", "")[:-len(" songs")])

    if not is_mzansi_page(title, categories):
        return

    thumb = None
    for thumbptrnword in ["logo", "screenshot", "cover", "image", "map"]:
        result = re.search(f'\\| *{thumbptrnword} *=(.+)', text, re.IGNORECASE)
        if result:
            thumb = result.group(1).strip()
            break
    if thumb is None:
        if "[[File:" in text:
            thumb = text.split("[[File:")[1].split("|")[0].split("]")[0].strip()
    if thumb is not None and len(thumb.strip()) == 0:
        thumb = f"{title}.png"

    all_pages[title] = {
        "id": int(page["id"]),
        "title": title,
        "text": parsed_text,
        "categories": categories,
        "thumb": thumb,
        "disambiguation": "{{disambiguation}}" in text.lower() or "{{disambig}}" in text.lower() or "{{numberdis}}" in text.lower(),
    }

    for category in categories:
        if category not in all_categories:
            all_categories[category] = []
        all_categories[category].append(title)

print("Processing links...")
links = {}
INSERT_SYNTAX = "INSERT INTO `pagelinks` VALUES "
with gzip.open(DUMP_PAGELINKS, "rt", encoding="utf-8") as f:
    for l in f:
        if l.startswith(INSERT_SYNTAX):
            for v in l[len(INSERT_SYNTAX)+1:-3].split("),("):
                a,_,b = v.split(",")
                if int(a) not in links:
                    links[int(a)] = []    
                links[int(a)].append(int(b))

current_entry = None
with bz2.open(DUMP_ARTICLES, "rt", encoding="utf-8") as f:
    for i,l in enumerate(f):
        if i % 1000000 == 0:
            print(f"{i/30_093_139*100:.02f}%")
        if l == "  <page>\n":
            current_entry = ""
        if l == "  </page>\n":
            current_entry += "  </page>"
            process_page(current_entry)
            current_entry = None
        if current_entry == None:
            continue
        current_entry += l

print("Subcategories...")
subCategories = {}
for k,v in all_categories.items():
    for subCat in v:
        if not subCat.lower().startswith("category:"):
            continue
        subCatVal = subCat.lower().split("category:")[1]
        if subCatVal not in subCategories:
            subCategories[subCatVal] = []
        subCategories[subCatVal].append(k)

print("Final version...")
pages2 = []
noPageMaps = {}
for page in all_pages.values():
    if page["disambiguation"] or len(re.sub("[\\s0-9]{2,4}", "", page["text"])) == 0 or re.match("^[0-9]{2,4}s?$", page["title"]) or (":" in page["title"] and page["title"].lower().split(":")[0] in ["module","category","template","wikimedia","mediawiki","wikipedia","help"]):
        noPageMaps[page["id"]] = page["title"]
        continue
    pages2.append([page["title"],page["id"],page["text"],page["thumb"],page["categories"],links[page["id"]] if page["id"] in links else []])
# pages2.sort(key=lambda x:x[0])

with open(OUT_JSON, "w") as f:
    json.dump({"pages": pages2, "noPageMaps": noPageMaps, "subCategories": subCategories}, f, separators=(',', ':'))
