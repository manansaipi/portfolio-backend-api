import os

os.makedirs('app/models', exist_ok=True)
os.makedirs('app/schemas', exist_ok=True)

# Split models
with open('app/models.py', 'r') as f:
    content = f.read()

base_imports = """from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sqlalchemy
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

def get_wib_time():
    return datetime.now(ZoneInfo("Asia/Jakarta"))

def generate_uuid():
    return str(uuid.uuid4())
"""

models_map = {
    'project.py': 'class Project',
    'experience.py': 'class Experience',
    'writing.py': 'class Writing',
    'comment.py': 'class Comment',
    'certificate.py': 'class Certificate',
    'terminal_log.py': 'class TerminalLog',
}

init_content = ""

for filename, class_start in models_map.items():
    start_idx = content.find(class_start)
    if start_idx == -1: continue
    
    # Find next class or end of file
    next_class_idx = len(content)
    for k, v in models_map.items():
        idx = content.find(v, start_idx + 1)
        if idx != -1 and idx < next_class_idx:
            next_class_idx = idx
            
    class_content = content[start_idx:next_class_idx].strip()
    
    file_content = f"{base_imports}\nfrom app.core.database import Base\n\n{class_content}\n"
    
    with open(f'app/models/{filename}', 'w') as f:
        f.write(file_content)
        
    class_name = class_start.split(' ')[1]
    init_content += f"from .{filename[:-3]} import {class_name}\n"

with open('app/models/__init__.py', 'w') as f:
    f.write(init_content)
print("Models split successfully.")
