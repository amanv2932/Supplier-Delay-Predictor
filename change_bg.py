import os

def update_file(filepath, old_color, new_color):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_color, new_color)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('app.py', '#F8FAFC', '#FAF9F6')
update_file('.streamlit/config.toml', '#F8FAFC', '#FAF9F6')
