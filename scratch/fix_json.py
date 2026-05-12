import json

with open('characters.json', 'r', encoding='utf-8') as f:
    chars = json.load(f)

for char in chars:
    for cat in char['categories']:
        char['categories'][cat] = 1

with open('characters.json', 'w', encoding='utf-8') as f:
    json.dump(chars, f, ensure_ascii=False, indent=2)
