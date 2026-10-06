import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the forced dark sidebar CSS so the light theme from config.toml applies gracefully
content = re.sub(r'\[data-testid="stSidebar"\].*?\{.*?\}', '', content, flags=re.DOTALL)
content = content.replace('background-color: #FAF9F6;', 'background-color: #F8FAFC;')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
