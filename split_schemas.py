import os

with open('app/schemas.py', 'r') as f:
    content = f.read()

base_imports = """from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
"""

schemas_map = {
    'project.py': '# --- Project Schemas ---',
    'experience.py': '# --- Experience Schemas ---',
    'comment.py': '# --- Comment Schemas ---',
    'writing.py': '# --- Writing Schemas ---',
    'certificate.py': '# --- Certificate Schemas ---',
    'terminal_log.py': '# --- Terminal Log Schemas ---',
}

# The comment schema needs to be imported in writing schema because of `WritingWithComments`
# Wait, actually let's just split by sections.

init_content = ""

for filename, section_marker in schemas_map.items():
    start_idx = content.find(section_marker)
    if start_idx == -1: continue
    
    # Find next section or end of file
    next_section_idx = len(content)
    for k, v in schemas_map.items():
        idx = content.find(v, start_idx + 1)
        if idx != -1 and idx < next_section_idx:
            next_section_idx = idx
            
    section_content = content[start_idx:next_section_idx].strip()
    
    # Handle specific imports for Writing schema which depends on Comment
    extra_imports = ""
    if filename == 'writing.py':
        extra_imports = "from .comment import Comment\n"
        
    file_content = f"{base_imports}\n{extra_imports}\n{section_content}\n"
    
    with open(f'app/schemas/{filename}', 'w') as f:
        f.write(file_content)
        
    # extract classes for __init__.py
    lines = section_content.split('\n')
    for line in lines:
        if line.startswith('class '):
            class_name = line.split(' ')[1].split('(')[0].split(':')[0]
            if class_name != 'Config':
                init_content += f"from .{filename[:-3]} import {class_name}\n"

with open('app/schemas/__init__.py', 'w') as f:
    f.write(init_content)
print("Schemas split successfully.")
