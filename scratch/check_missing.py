import csv
import re
import json

def get_character_order(filepath):
    order = []
    seen = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            for cell in row:
                # Clean up but keep newlines for splitting
                clean_cell = cell.replace('"', '').strip()
                if not clean_cell:
                    continue
                
                # Split by newline or spaces
                names = re.split(r'[\s,、\n]+', clean_cell)
                for name in names:
                    name = name.strip()
                    if name and name not in seen:
                        order.append(name)
                        seen.add(name)
    return order

if __name__ == "__main__":
    with open('characters.json', 'r', encoding='utf-8') as f:
        chars = json.load(f)
        valid_names = {c['name'] for c in chars}
        
    full_order = get_character_order('rank.tsv')
    filtered_order = [name for name in full_order if name in valid_names]
    not_found = valid_names - set(filtered_order)
    
    print(f"Total names in rank.tsv: {len(full_order)}")
    print(f"Valid character names found: {len(filtered_order)}")
    print(f"Characters NOT found in rank.tsv ({len(not_found)}):")
    print(sorted(list(not_found)))
