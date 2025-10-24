#!/usr/bin/env python3
"""
Fix all models to use custom UUID type for SQLite compatibility
"""
import os
import re

models_dir = "backend/app/models"
models = ["project.py", "feedback.py", "revision.py", "action_item.py", "notification.py"]

for model_file in models:
    filepath = os.path.join(models_dir, model_file)
    
    if not os.path.exists(filepath):
        print(f"⚠ Skipping {model_file} - file not found")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace the import
    if "from sqlalchemy.dialects.postgresql import UUID" in content:
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import UUID",
            ""
        )
        
        # Add our custom UUID import after Base import
        content = re.sub(
            r'(from app\.db\.session import Base)',
            r'\1\nfrom app.db.types import UUID',
            content
        )
        
        # Replace UUID(as_uuid=True) with UUID()
        content = content.replace("UUID(as_uuid=True)", "UUID()")
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✓ Fixed {model_file}")
    else:
        print(f"⚠ {model_file} - no UUID import found")

print("\n✓ All models updated!")
