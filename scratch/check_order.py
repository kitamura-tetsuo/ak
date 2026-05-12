import csv
import re
import json

def get_rank_order():
    order = {}
    idx = 0
    with open('rank.tsv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            for cell in row:
                clean_cell = cell.replace('"', '').strip()
                if not clean_cell:
                    continue
                names = re.split(r'[\s,、\n]+', clean_cell)
                for name in names:
                    name = name.strip()
                    if name and name not in order:
                        order[name] = idx
                        idx += 1
    return order

order = get_rank_order()
with open('characters.json', 'r', encoding='utf-8') as f:
    chars = json.load(f)
    cat_to_chars = {}
    for c in chars:
        for cat in c['categories'].keys():
            if cat not in cat_to_chars: cat_to_chars[cat] = []
            cat_to_chars[cat].append(c['name'])

for cat in ['炎国', '投資家']:
    print(f"--- {cat} ---")
    names = sorted(cat_to_chars[cat], key=lambda x: order.get(x, 999))
    for name in names:
        print(f"{order.get(name, 999)}: {name}")
