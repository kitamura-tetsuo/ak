import csv
import re
from collections import defaultdict

def get_per_category_order(filepath, categories):
    cat_orders = defaultdict(dict)
    current_cat = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row: continue
            
            # Check if the first cell is a known category
            first_cell = row[0].strip().replace('"', '')
            if first_cell in categories:
                current_cat = first_cell
            
            if not current_cat: continue
            
            # Collect all names in this row
            for i, cell in enumerate(row):
                # Skip the first cell if it's the category name
                if i == 0 and cell.strip().replace('"', '') == current_cat:
                    # But wait, the category name cell might ALSO contain character names if it's messy
                    # In our TSV, it seems the category name is alone in the first cell, or followed by tabs
                    clean_cell = cell.replace('"', '').replace(current_cat, '').strip()
                else:
                    clean_cell = cell.replace('"', '').strip()
                
                if not clean_cell: continue
                
                names = re.split(r'[\s,、\n]+', clean_cell)
                for name in names:
                    name = name.strip()
                    if name and name not in cat_orders[current_cat]:
                        cat_orders[current_cat][name] = len(cat_orders[current_cat])
                        
    return cat_orders

if __name__ == "__main__":
    factions = ['炎国', 'サルゴン', 'ヴィクトリア', 'イェラグ', 'ラテラーノ', 'エーギル', '共同防衛']
    roles = ['投資家', '調和', '先見', '精密', '堅守', '強襲', '奇跡', '不屈', '俊敏', '助力', '器用']
    all_cats = set(factions + roles)
    
    orders = get_per_category_order('rank.tsv', all_cats)
    
    for cat in ['炎国', '投資家']:
        print(f"--- {cat} ---")
        sorted_names = sorted(orders[cat].items(), key=lambda x: x[1])
        for name, idx in sorted_names:
            print(f"{idx}: {name}")
