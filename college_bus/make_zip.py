import os
import zipfile

src_dir = r'C:\Users\Lenovo\.gemini\antigravity\scratch\college_bus'
zip_path = r'C:\Users\Lenovo\Desktop\college_bus_project.zip'

exclude_dirs = {'venv', '.git', '__pycache__', '.pytest_cache'}
exclude_extensions = {'.pyc'}

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(src_dir):
        # Filter out directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, src_dir)
            zipf.write(full_path, os.path.join('college_bus', rel_path))

print(f"ZIP_CREATED_SUCCESS: {os.path.getsize(zip_path)} bytes")
