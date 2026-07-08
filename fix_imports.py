import os
import glob

files = glob.glob('app/api/endpoints/*.py')
for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    content = content.replace("from .. import models, schemas, database", "from app import models, schemas\nfrom app.core import database")
    content = content.replace("from .. import models, schemas", "from app import models, schemas")
    
    with open(file, 'w') as f:
        f.write(content)
print("Fixed imports")
