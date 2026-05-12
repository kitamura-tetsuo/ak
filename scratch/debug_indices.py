import csv
import re

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
                        print(f"Index {idx}: {name}")
                        idx += 1
    return order

get_rank_order()
