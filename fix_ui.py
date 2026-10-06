import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the CSS block with the updated one
new_css = """<style>
    /* Global styles and typography */
    [data-testid="stAppViewContainer"] {
        background-color: #EAEFF5;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #172033;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Sidebar selectboxes */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #FFFFFF !important;
    }
    /* Multi-select tags */
    [data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    /* Dropdown popups (these often render outside the sidebar div, so use global selector for base-web popovers) */
    ul[data-baseweb="menu"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }
    ul[data-baseweb="menu"] li {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }
    ul[data-baseweb="menu"] li:hover, ul[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #2563EB !important;
    }
    
    /* Reset Button */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: 1px solid #334155 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #1E293B !important;
    }
    
    /* Main Content Typography */
    .block-container {
        padding-top: 1rem !important; /* Reduce top padding */
    }
    h1 { font-size: 32px !important; font-weight: 700 !important; color: #0F172A !important; }
    h2 { font-size: 22px !important; font-weight: 600 !important; color: #0F172A !important; }
    h3, h4, h5, h6 { color: #0F172A !important; }
    
    /* KPI Cards */
    .metric-card {
        background-color: #FFFFFF;
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #D5DEE9;
        border-left: 3px solid #2563EB;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 1px 2px rgba(15,23,42,0.05);
        margin-bottom: 10px;
    }
    .metric-title {
        color: #64748B;
        font-size: 12px;
        margin-bottom: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .metric-value {
        color: #0F172A;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-value-text {
        color: #0F172A;
        font-size: 18px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-subtext {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
    }
    
    /* Info Strip */
    .data-overview {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #D5DEE9;
        color: #64748B;
        font-size: 13px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(15,23,42,0.05);
    }
    .data-overview strong {
        color: #0F172A;
    }
    
    /* Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        border-bottom: 1px solid #D5DEE9;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 3px solid transparent;
        color: #64748B;
        font-weight: 500;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #2563EB !important;
        border-bottom: 3px solid #2563EB !important;
        font-weight: 600;
    }
    
    /* Hide Deploy and Footer */
    header[data-testid="stHeader"] .stAppDeployButton {
        display: none !important;
    }
    footer[data-testid="stFooter"] {
        display: none !important;
    }
    
    /* AI Prediction colors */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #2563EB !important;
    }
    .stSlider [data-baseweb="slider"] div[data-baseweb="slider-track"] > div:first-child {
        background-color: #2563EB !important;
    }
</style>"""

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

# Adjust Subtitle
content = content.replace('st.markdown("A clean AI-powered logistics analytics dashboard that represents the actual shipment dataset and provides historical shipment-delay insights.")', 'st.markdown("<p style=\'font-size: 15px; color: #64748B; margin-bottom: 5px;\'>A clean AI-powered logistics analytics dashboard that represents the actual shipment dataset and provides historical shipment-delay insights.</p>", unsafe_allow_html=True)')
content = content.replace('st.markdown("---")', '')

# Fix AI prediction colors in app.py
content = content.replace("st.error(f\"**⚠️ Likely Delayed**\\\\n\\\\n**Predicted probability:** {prob:.1%}\")", "st.markdown(f\"<div style='background-color: #FFFFFF; padding: 20px; border-radius: 10px; border-left: 4px solid #DC2626; border-top: 1px solid #D5DEE9; border-right: 1px solid #D5DEE9; border-bottom: 1px solid #D5DEE9;'><h3 style='color: #DC2626 !important; margin: 0;'>⚠️ Likely Delayed</h3><p style='font-size: 18px; margin-top: 10px; color: #0F172A;'>Predicted probability: <strong>{prob:.1%}</strong></p></div>\", unsafe_allow_html=True)")
content = content.replace("st.success(f\"**✅ Likely On-Time**\\\\n\\\\n**Predicted probability:** {prob:.1%}\")", "st.markdown(f\"<div style='background-color: #FFFFFF; padding: 20px; border-radius: 10px; border-left: 4px solid #16A34A; border-top: 1px solid #D5DEE9; border-right: 1px solid #D5DEE9; border-bottom: 1px solid #D5DEE9;'><h3 style='color: #16A34A !important; margin: 0;'>✅ Likely On-Time</h3><p style='font-size: 18px; margin-top: 10px; color: #0F172A;'>Predicted probability: <strong>{prob:.1%}</strong></p></div>\", unsafe_allow_html=True)")

content = content.replace("st.markdown(f\"⚠ {f}\")", "st.markdown(f\"<span style='color: #DC2626;'>⚠ {f}</span>\", unsafe_allow_html=True)")
content = content.replace("st.markdown(f\"✓ {f}\")", "st.markdown(f\"<span style='color: #16A34A;'>✓ {f}</span>\", unsafe_allow_html=True)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Update config.toml
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as f:
    f.write('''[theme]
primaryColor="#2563EB"
backgroundColor="#EAEFF5"
secondaryBackgroundColor="#FFFFFF"
textColor="#0F172A"
font="sans serif"
''')
