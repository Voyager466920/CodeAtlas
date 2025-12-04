import os
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".idea", ".vscode", "venv", "env", "dist", "build", "coverage"
}

IGNORE_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini"
}

def get_file_structure(path: str, max_files: int = 2000):
    """
    Recursively traverses the directory and returns a structure suitable for visualization.
    """
    root = Path(path)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid directory path: {path}")

    def traverse(current_path: Path):
        nonlocal file_count
        if file_count > max_files:
            raise ValueError(f"File limit exceeded (>{max_files}). Please select a smaller directory.")
            
        name = current_path.name
        is_dir = current_path.is_dir()
        
        item = {
            "name": name,
            "path": str(current_path),
            "type": "directory" if is_dir else "file",
            "children": []
        }

        if is_dir:
            try:
                # Sort: Directories first, then files
                entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name.lower()))
                
                for entry in entries:
                    if entry.name in IGNORE_DIRS or entry.name in IGNORE_FILES:
                        continue
                    
                    # Skip hidden files/dirs starting with .
                    if entry.name.startswith("."):
                        continue

                    # Increment count for every item visited
                    file_count += 1
                    item["children"].append(traverse(Path(entry.path)))
            except PermissionError:
                pass # Skip directories we can't access
        
        return item

    file_count = 0
    return traverse(root)
