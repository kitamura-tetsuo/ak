import csv
import re

def get_character_order(filepath):
    order = []
    seen = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Use csv reader with tab delimiter to handle the TSV
        # Note: The file has messy quotes, so we might need to clean up
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            for cell in row:
                # Clean up quotes and newlines
                clean_cell = cell.replace('"', '').replace('\n', '').strip()
                if not clean_cell:
                    continue
                
                # Split by comma or other delimiters if multiple names are in one cell
                # Based on the file view, some cells have "Name1\nName2" which becomes "Name1Name2" if we just replace \n
                # Let's try to split by potential delimiters if they exist, but mostly names seem to be in their own cells or separated by newlines in the original source
                
                # The file view showed:
                # 3: ワンチィン"	"ワイフー
                # 4: 琳琅スワイヤー"	"マルベリー
                
                # Actually, the csv reader might handle the quotes correctly if we use the right quotechar.
                # Let's try to just get the names.
                
                # Some names might be categories (like '炎国', 'サルゴン'). 
                # We should probably filter out known categories if they are at the start of a row.
                
                # Let's just collect everything that looks like a character name.
                # If it's in characters.json, it's a character.
                
                names = re.split(r'[\s,、\n]+', clean_cell)
                for name in names:
                    name = name.strip()
                    if name and name not in seen:
                        order.append(name)
                        seen.add(name)
    return order

if __name__ == "__main__":
    import json
    with open('characters.json', 'r', encoding='utf-8') as f:
        chars = json.load(f)
        valid_names = {c['name'] for c in chars}
        
    full_order = get_character_order('rank.tsv')
    filtered_order = [name for name in full_order if name in valid_names]
    
    print(f"Total names found: {len(full_order)}")
    print(f"Valid character names found: {len(filtered_order)}")
    print("First 10 names:", filtered_order[:10])
