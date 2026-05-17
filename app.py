import streamlit as st
import json
import pandas as pd
import csv
import re
import urllib.parse
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="Character Skill Calculator",
    page_icon="⚔️",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    with open('characters.json', 'r', encoding='utf-8') as f:
        chars = json.load(f)
        return {c['name']: {'categories': c['categories'], 'rank': c['rank']} for c in chars}

@st.cache_data
def get_rank_data(all_categories):
    global_order = {}
    cat_orders = defaultdict(dict)
    current_cat = None
    idx_global = 0
    
    with open('rank.tsv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row: continue
            
            # Check if first cell is a known category
            first_cell = row[0].strip().replace('"', '')
            if first_cell in all_categories:
                current_cat = first_cell
            
            if not current_cat: continue
            
            for i, cell in enumerate(row):
                # Clean but handle category name in first cell
                if i == 0 and cell.strip().replace('"', '') == current_cat:
                    clean_cell = cell.replace('"', '').replace(current_cat, '').strip()
                else:
                    clean_cell = cell.replace('"', '').strip()
                
                if not clean_cell: continue
                
                names = re.split(r'[\s,、\n]+', clean_cell)
                for name in names:
                    name = name.strip()
                    if not name: continue
                    
                    # Per-category order
                    if name not in cat_orders[current_cat]:
                        cat_orders[current_cat][name] = len(cat_orders[current_cat])
                    
                    # Global order (fallback)
                    if name not in global_order:
                        global_order[name] = idx_global
                        idx_global += 1
                        
    return global_order, cat_orders

char_map = load_data()
factions = ['炎国', 'サルゴン', 'ヴィクトリア', 'イェラグ', 'ラテラーノ', 'エーギル', '共同防衛']
roles = ['投資家', '調和', '先見', '精密', '堅守', '強襲', '奇跡', '不屈', '俊敏', '助力', '器用']

global_order, cat_orders = get_rank_data(set(factions + roles))

# Category to Characters mapping
cat_to_chars = defaultdict(list)
for name, data in char_map.items():
    for cat in data['categories'].keys():
        cat_to_chars[cat].append(name)

# Initialize session state from URL if present
if 'selected_chars' not in st.session_state:
    if "chars" in st.query_params:
        try:
            char_list = st.query_params["chars"].split(",")
            # Filter only valid character names
            st.session_state['selected_chars'] = set(c for c in char_list if c in char_map)
        except Exception:
            st.session_state['selected_chars'] = set()
    else:
        st.session_state['selected_chars'] = set()
else:
    # Sync with query parameters if they changed (e.g. from clicking a delete link)
    if "chars" in st.query_params:
        try:
            url_chars = set(c for c in st.query_params["chars"].split(",") if c in char_map)
            if url_chars != st.session_state['selected_chars']:
                st.session_state['selected_chars'] = url_chars
                # Reset all checkbox states so they get re-evaluated correctly
                for key in list(st.session_state.keys()):
                    if key.startswith("cb_"):
                        st.session_state[key] = False
        except Exception:
            pass
    elif st.session_state['selected_chars'] and "chars" not in st.query_params:
        # If query parameters are completely cleared, reset selection
        st.session_state['selected_chars'] = set()
        for key in list(st.session_state.keys()):
            if key.startswith("cb_"):
                st.session_state[key] = False

# Master sync function
def sync_all_checkboxes(name, new_status):
    if new_status:
        st.session_state['selected_chars'].add(name)
    else:
        st.session_state['selected_chars'].discard(name)
    
    # Update ALL possible checkbox keys for this character
    for cat in char_map[name]['categories'].keys():
        key = f"cb_{cat}_{name}"
        st.session_state[key] = new_status
    
    # Update URL query params
    if st.session_state['selected_chars']:
        st.query_params["chars"] = ",".join(sorted(list(st.session_state['selected_chars'])))
    else:
        if "chars" in st.query_params:
            del st.query_params["chars"]

def on_checkbox_change(name, cat):
    key = f"cb_{cat}_{name}"
    new_status = st.session_state[key]
    sync_all_checkboxes(name, new_status)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #060515 0%, #151435 50%, #060515 100%); color: white; }
    h1 { font-weight: 800; background: linear-gradient(to right, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem !important; }
    .glass-card { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.15); padding: 1.5rem; margin-bottom: 1rem; }
    .stat-value { font-size: 3.5rem; font-weight: 800; color: #00d2ff; text-shadow: 0 0 15px rgba(0, 210, 255, 0.6); }
    
    /* ULTRA READABLE CHECKBOXES */
    .stCheckbox label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    .stCheckbox label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-shadow: 0 0 8px rgba(0,0,0,1), 0 0 2px rgba(0,0,0,1) !important;
    }
    
    .category-header { 
        color: #00e5ff; 
        border-bottom: 2px solid rgba(0, 229, 255, 0.4); 
        margin-top: 1.2rem; 
        margin-bottom: 0.8rem; 
        font-weight: 900;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        color: #888;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 198, 255, 0.1);
        color: #00c6ff !important;
    }
    
    /* SLEEK COMPACT RED DELETE BUTTONS */
    div[data-testid="column"] button {
        padding: 4px 10px !important;
        font-size: 0.9rem !important;
        height: auto !important;
        min-height: unset !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
        color: #ff4b4b !important;
        border: 1px solid rgba(255, 75, 75, 0.2) !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
        box-shadow: 0 0 8px rgba(255, 75, 75, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1>Skill Synergy & Ranks</h1>', unsafe_allow_html=True)

# Search and Reset
c_search, c_reset = st.columns([4, 1])
with c_search:
    search_query = st.text_input("🔍 Search Characters", placeholder="Enter name...")
with c_reset:
    if st.button("🗑️ Clear All"):
        st.session_state['selected_chars'] = set()
        # Reset all keys in session state
        for key in list(st.session_state.keys()):
            if key.startswith("cb_"):
                st.session_state[key] = False
        # Clear URL params
        st.query_params.clear()
        st.rerun()

# Calculations
selected_names = sorted(list(st.session_state['selected_chars']), key=lambda x: global_order.get(x, 999))
cat_totals = defaultdict(int)
rank_freq = defaultdict(int)
for name in selected_names:
    data = char_map[name]
    for cat in data['categories'].keys():
        cat_totals[cat] += 1
    rank_freq[data['rank']] += 1

# Special Rule: 調和 bonus
if cat_totals.get('調和', 0) >= 1:
    for cat in factions:
        if cat == '共同防衛':
            continue
        cat_totals[cat] += 1

grand_total = sum(cat_totals.values())

# Define thresholds
threshold_3 = set(['炎国', 'サルゴン', 'ヴィクトリア', 'イェラグ', 'ラテラーノ', 'エーギル', '共同防衛'])
threshold_2 = set(['投資家', '先見', '精密', '堅守', '強襲', '奇跡', '不屈', '俊敏', '助力', '器用'])
threshold_1 = set(['調和'])

active_cats = set()
for cat, total in cat_totals.items():
    if cat in threshold_3 and total >= 3: active_cats.add(cat)
    elif cat in threshold_2 and total >= 2: active_cats.add(cat)
    elif cat in threshold_1 and total >= 1: active_cats.add(cat)


# Selection Section
# st.markdown('<div class="glass-card">', unsafe_allow_html=True)
tab_f, tab_r = st.tabs(["Factions (陣営)", "Roles (役割)"])

def render_checklists(categories_list):
    cols = st.columns(len(categories_list))
    for i, cat in enumerate(categories_list):
        with cols[i]:
            header_text = f"{cat}"
            if cat_totals[cat] > 0:
                header_text += f" ({cat_totals[cat]})"
            st.markdown(f'<div class="category-header">{header_text}</div>', unsafe_allow_html=True)
            
            names = sorted(cat_to_chars[cat], key=lambda x: cat_orders[cat].get(x, 999))
            for name in names:
                if search_query and search_query.lower() not in name.lower():
                    continue
                
                key = f"cb_{cat}_{name}"
                # Ensure the checkbox state matches the master set
                st.session_state[key] = name in st.session_state['selected_chars']
                
                st.checkbox(name, key=key, on_change=on_checkbox_change, args=(name, cat))

with tab_f:
    render_checklists([f for f in factions if f in cat_to_chars])

with tab_r:
    role_cats = [r for r in roles if r in cat_to_chars]
    # More columns for roles
    r_cols = st.columns(4)
    for i, cat in enumerate(role_cats):
        with r_cols[i % 4]:
            header_text = f"{cat}"
            if cat_totals[cat] > 0:
                header_text += f" ({cat_totals[cat]})"
            st.markdown(f'<div class="category-header">{header_text}</div>', unsafe_allow_html=True)
            
            names = sorted(cat_to_chars[cat], key=lambda x: cat_orders[cat].get(x, 999))
            for name in names:
                if search_query and search_query.lower() not in name.lower():
                    continue
                key = f"cb_{cat}_{name}"
                st.session_state[key] = name in st.session_state['selected_chars']
                st.checkbox(name, key=key, on_change=on_checkbox_change, args=(name, cat))

# st.markdown('</div>', unsafe_allow_html=True)

# Dashboard
col_l, col_r = st.columns([1, 1])

with col_l:
    # st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
    st.markdown('<p style="text-transform: uppercase; letter-spacing: 2px; color: #8888ff;">Total Skill Points</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stat-value">{grand_total}</p>', unsafe_allow_html=True)
    
    count = len(selected_names)
    color = "#00d2ff" if count <= 9 else "#ff4b4b"
    st.markdown(f'<p style="font-size: 1.5rem; color: {color}; font-weight: 900;">{count} / 9 SELECTED</p>', unsafe_allow_html=True)
    if count > 9:
        st.warning("⚠️ Limit exceeded (9 max)")
    # st.markdown('</div>', unsafe_allow_html=True)
    
with col_r:
    # st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Category Breakdown")
    if cat_totals:
        # Define threshold groups
        threshold_3 = set(['炎国', 'サルゴン', 'ヴィクトリア', 'イェラグ', 'ラテラーノ', 'エーギル', '共同防衛'])
        threshold_2 = set(['投資家', '先見', '精密', '堅守', '強襲', '奇跡', '不屈', '俊敏', '助力', '器用'])
        threshold_1 = set(['調和'])

        # Filter categories with 0 points
        display_cats = [(cat, total) for cat, total in cat_totals.items() if total > 0]
        # Sort by total points (descending)
        display_cats.sort(key=lambda x: x[1], reverse=True)

        if display_cats:
            break_cols = st.columns(3)
            for i, (cat, total) in enumerate(display_cats):
                # Determine if it should be displayed "thinly"
                is_thin = cat not in active_cats
                
                style = 'opacity: 0.4; font-weight: 300;' if is_thin else 'font-weight: 700;'
                with break_cols[i % 3]:
                    st.markdown(f'<div style="{style}">{cat}: {total}</div>', unsafe_allow_html=True)
        else:
            st.write("No categories with points.")
    else:
        st.write("No selection yet.")
    # st.markdown('</div>', unsafe_allow_html=True)

# Squad Table
with col_l:
    if selected_names:
        st.markdown("### Squad Composition")
        
        # Header Row
        col_char, col_rank, col_cats, col_tot, col_act = st.columns([2.5, 1.5, 4.5, 1.2, 1.2])
        col_char.markdown("**Character**")
        col_rank.markdown("**Rank**")
        col_cats.markdown("**Categories**")
        col_tot.markdown("**Total**")
        col_act.markdown("<div style='text-align: center; font-weight: bold;'>Action</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 4px 0 12px 0; border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
        
        for name in selected_names:
            data = char_map[name]
            is_active_char = any(cat in active_cats for cat in data['categories'].keys())
            
            if is_active_char:
                text_color = "#ffffff"
                weight_style = "font-weight: 700;"
                cat_active_style = "color: #00d2ff; font-weight: 800; text-shadow: 0 0 10px rgba(0, 210, 255, 0.4);"
                cat_inactive_style = "opacity: 0.4; font-weight: 300;"
            else:
                text_color = "#cccccc"
                weight_style = "font-weight: 400; opacity: 0.7;"
                cat_active_style = "color: #0055aa; font-weight: 800;"
                cat_inactive_style = "color: #555555; font-weight: 400;"

            cat_items = []
            for cat in data['categories'].keys():
                if cat in active_cats:
                    cat_items.append(f'<span style="{cat_active_style}">{cat}</span>')
                else:
                    cat_items.append(f'<span style="{cat_inactive_style}">{cat}</span>')
            cats_html = ", ".join(cat_items)
            
            # Align each row's cells perfectly with the header
            col_char, col_rank, col_cats, col_tot, col_act = st.columns([2.5, 1.5, 4.5, 1.2, 1.2])
            col_char.markdown(f"<div style='color: {text_color}; {weight_style}; padding-top: 8px;'>{name}</div>", unsafe_allow_html=True)
            col_rank.markdown(f"<div style='color: {text_color}; padding-top: 8px;'>⭐ {data['rank']}</div>", unsafe_allow_html=True)
            col_cats.markdown(f"<div style='color: {text_color}; padding-top: 8px;'>{cats_html}</div>", unsafe_allow_html=True)
            col_tot.markdown(f"<div style='color: {text_color}; font-weight: 700; padding-top: 8px;'>{sum(data['categories'].values())}</div>", unsafe_allow_html=True)
            with col_act:
                # Native button - completely reload-free using callback to respect widget lifecycle!
                st.button("🗑️", key=f"del_{name}", help=f"Remove {name}", on_click=sync_all_checkboxes, args=(name, False))
            
            st.markdown("<hr style='margin: 6px 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)


with col_r:
    st.markdown("### Rank Distribution")
    if selected_names:
        chart_data = pd.DataFrame({
            'Rank': [f"R{r}" for r in range(1, 7)],
            'Count': [rank_freq[r] for r in range(1, 7)]
        }).set_index('Rank')
        st.bar_chart(chart_data)
    st.markdown('</div>', unsafe_allow_html=True)



if len(selected_names) == 9:
    st.balloons()
