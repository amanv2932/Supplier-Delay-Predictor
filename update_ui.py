import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update CSS
new_css = """<style>
    /* Global styles and typography */
    [data-testid="stAppViewContainer"] {
        background-color: #F5F7FA;
    }
    [data-testid="stSidebar"] {
        background-color: #172033;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #172033;
    }
    h1 { font-weight: 700; }
    h2 { font-weight: 600; }
    
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: none;
    }
    .metric-title {
        color: #64748B;
        font-size: 13px;
        margin-bottom: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #172033;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }
    .metric-value-text {
        color: #172033;
        font-size: 18px;
        font-weight: 700;
        margin: 0;
        line-height: 1.3;
    }
    .metric-subtext {
        color: #64748B;
        font-size: 12px;
        margin-top: 6px;
    }
    .data-overview {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .data-overview strong {
        color: #172033;
    }
    
    /* Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px 0px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
        font-weight: 600;
    }
</style>"""

# Replace CSS block
content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

# Update Streamlit theme colors via config
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as f:
    f.write('''[theme]
primaryColor="#2563EB"
backgroundColor="#F5F7FA"
secondaryBackgroundColor="#172033"
textColor="#172033"
font="sans serif"
''')

# Now fix the plot colors
# '#3498db' -> '#2563EB'
content = content.replace("['#3498db']", "['#2563EB']")
# '#e74c3c' -> '#2563EB' (Since it was the primary color for line charts)
content = content.replace("['#e74c3c']", "['#2563EB']")
# '#9b59b6' -> '#2563EB' (Box plot)
content = content.replace("['#9b59b6']", "['#2563EB']")
# '#f1c40f' -> '#2563EB' (Scatter)
content = content.replace("'#f1c40f'", "'#2563EB'")

# Fix color map
old_color_map = "{'On-Time': 'green', 'Minor Delay': 'yellow', 'Major Delay': 'red'}"
new_color_map = "{'On-Time': '#16A34A', 'Minor Delay': '#EAB308', 'Major Delay': '#DC2626'}"
content = content.replace(old_color_map, new_color_map)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
