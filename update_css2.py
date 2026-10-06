import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_css = """    /* Sidebar selectboxes */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #1E293B !important;
    }

    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div > div {
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: none !important;
        background-color: transparent !important;
    }
"""

content = re.sub(r'/\* Sidebar selectboxes \*/.*?(?=/\* dropdown popup list)', new_css, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
