import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update colors globally
content = content.replace('#2563EB', '#3B82F6') # Primary blue
content = content.replace('#EAEFF5', '#F8FAFC') # Main background
content = content.replace('#16A34A', '#22C55E') # On-Time Green
content = content.replace('#DC2626', '#EF4444') # Major Delay Red

# 2. Fix KPI Card text wrapping (remove white-space: nowrap from .metric-title)
content = content.replace('white-space: nowrap;', 'white-space: normal;')
content = content.replace('overflow: hidden;', '')
content = content.replace('text-overflow: ellipsis;', '')

# 3. Strip fragile CSS from sidebar
fragile_css_pattern = r'/\* Sidebar selectboxes \*/.*?(?=/\* Dropdown popups|/\* Reset Button)'
# Wait, I previously named it "/* dropdown popup list" in the last update.
fragile_css_pattern_2 = r'/\* Sidebar selectboxes \*/.*?/\* dropdown popup list.*?(?=/\* Reset Button \*/)'
content = re.sub(fragile_css_pattern_2, '', content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Update config.toml
with open('.streamlit/config.toml', 'w') as f:
    f.write('''[theme]
primaryColor="#3B82F6"
backgroundColor="#F8FAFC"
secondaryBackgroundColor="#FFFFFF"
textColor="#0F172A"
font="sans serif"

[theme.sidebar]
backgroundColor = "#0F172A"
secondaryBackgroundColor = "#1E293B"
textColor = "#FFFFFF"
borderColor = "#334155"
''')
