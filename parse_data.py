import csv
import json
import re
import io

def parse_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Section 1 (Factions): Names 98-133, Skills 180-186
    # Section 2 (Roles): Names 134-176, Skills 187-197
    
    char_block_1 = "".join(lines[97:133])
    skill_block_1 = "".join(lines[179:186])
    
    char_block_2 = "".join(lines[133:176])
    skill_block_2 = "".join(lines[186:197])

    def process_block(block):
        result = []
        f = io.StringIO(block)
        reader = csv.reader(f)
        for row in reader:
            if not row or not any(row):
                continue
            row = [cell.strip() for cell in row]
            if row[0]: # New category
                result.append(row)
            else: # Continuation
                if result:
                    for i in range(min(len(row), len(result[-1]))):
                        if row[i]:
                            if result[-1][i]:
                                result[-1][i] += "\n" + row[i]
                            else:
                                result[-1][i] = row[i]
        return result

    data_1_chars = process_block(char_block_1)
    data_1_skills = process_block(skill_block_1)
    data_2_chars = process_block(char_block_2)
    data_2_skills = process_block(skill_block_2)

    char_map = {} # character_name -> { category: skills }

    def add_to_map(chars_rows, skills_rows):
        skill_dict = {row[0]: row[1:] for row in skills_rows}
        for char_row in chars_rows:
            cat = char_row[0]
            skills_cols = skill_dict.get(cat, [])
            for i in range(min(len(char_row[1:]), len(skills_cols))):
                names_raw = char_row[i+1]
                skill_val_raw = skills_cols[i]
                
                if not names_raw or not skill_val_raw:
                    continue
                
                try:
                    skill_match = re.search(r'\d+', skill_val_raw)
                    if not skill_match: continue
                    skill_val = int(skill_match.group())
                except ValueError:
                    continue
                
                names = [n.strip() for n in re.split(r'[\n,]', names_raw) if n.strip()]
                for name in names:
                    if name not in char_map:
                        char_map[name] = {}
                    char_map[name][cat] = skill_val

    add_to_map(data_1_chars, data_1_skills)
    add_to_map(data_2_chars, data_2_skills)

    return char_map

def parse_rank(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return {}
    
    f = io.StringIO(content)
    reader = csv.reader(f, delimiter='\t')
    
    rank_map = {}
    try:
        header = next(reader)
    except StopIteration:
        return {}
    
    rows = []
    for row in reader:
        if not row or not any(x.strip() for x in row): continue
        if row[0].strip():
            rows.append([cell.strip() for cell in row])
        else:
            if rows:
                for i in range(min(len(row), len(rows[-1]))):
                    content = row[i].strip()
                    if content:
                        if rows[-1][i]:
                            rows[-1][i] += "\n" + content
                        else:
                            rows[-1][i] = content
                            
    for row in rows:
        for i in range(1, min(len(row), 7)):
            rank = i
            names_raw = row[i]
            names = [n.strip() for n in re.split(r'[\n,]', names_raw) if n.strip()]
            for name in names:
                rank_map[name] = rank
                
    return rank_map

if __name__ == "__main__":
    char_map = parse_csv('data.csv')
    rank_map = parse_rank('rank.tsv')
    
    output = []
    for name, categories in char_map.items():
        output.append({
            "name": name,
            "categories": categories,
            "rank": rank_map.get(name, 0)
        })
        
    with open('characters.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Parsed {len(output)} unique characters.")
    print(f"Silverash Rank: {rank_map.get('シルバーアッシュ')}")
