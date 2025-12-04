from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys
import webbrowser
from backend.services.file_system import get_file_structure
# Lazy import slm to avoid loading model on startup immediately if not needed, 
# but here we might want it. For now, import inside endpoint or top level.
from backend.services.slm import analyze_file_content
import tkinter as tk
from tkinter import filedialog
import urllib.request

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.environ.get("PORT", "8000")
    
    # Startup model check
    import sys
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
    model_path = os.path.join(base_dir, "models", "qwen2.5-7b-instruct-q4_k_m.gguf")
    
    print(f"Checking for AI model at: {model_path}")
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        print("Model Found")
    else:
        print("Model NOT Found")
        
    webbrowser.open(f"http://localhost:{port}")
    yield

app = FastAPI(title="File Structure Viz API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=resource_path("backend/static")), name="static")

class PathRequest(BaseModel):
    path: str

class FileAnalysisRequest(BaseModel):
    path: str
    language: str = "ko"

class ExportRequest(BaseModel):
    root_path: str
    files: List[Dict[str, Any]]

@app.post("/analyze")
async def analyze_structure(request: PathRequest):
    try:
        structure = get_file_structure(request.path)
        return structure
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_file")
async def analyze_file(request: FileAnalysisRequest):
    if not os.path.exists(request.path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security: Prevent access to system directories
    forbidden_paths = [
        r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)", 
        "/etc", "/var", "/usr"
    ]
    abs_path = os.path.abspath(request.path)
    for forbidden in forbidden_paths:
        if abs_path.startswith(os.path.abspath(forbidden)):
             raise HTTPException(status_code=403, detail="Access to system directories is forbidden")

    try:
        with open(request.path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        result = analyze_file_content(os.path.basename(request.path), content, request.language)
        return result
    except Exception as e:
        print(f"Analysis error: {e}")
        return {"summary": "분석 중 오류 발생", "keywords": []}

@app.post("/export_report")
async def export_report(request: ExportRequest):
    try:
        if not os.path.exists(request.root_path):
             raise HTTPException(status_code=404, detail="Root path not found")

        report_path = os.path.join(request.root_path, "analysis_report.md")
        
        # Group files by top-level directory
        grouped_files = {}
        for file_data in request.files:
            path = file_data.get("path", "")
            try:
                rel_path = os.path.relpath(path, request.root_path)
                parts = rel_path.split(os.sep)
                if len(parts) > 1:
                    group = parts[0]
                else:
                    group = "Root"
            except ValueError:
                group = "Unknown"
            
            if group not in grouped_files:
                grouped_files[group] = []
            grouped_files[group].append(file_data)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Analysis Report\n\n")
            f.write(f"Target Directory: {request.root_path}\n\n")
            
            # Sort groups, put Root first
            sorted_groups = sorted(grouped_files.keys())
            if "Root" in sorted_groups:
                sorted_groups.remove("Root")
                sorted_groups.insert(0, "Root")
            
            for group in sorted_groups:
                f.write(f"## {group}\n\n")
                f.write(f"| File | Path | Description |\n")
                f.write(f"| :--- | :--- | :--- |\n")
                
                for file_data in grouped_files[group]:
                    name = file_data.get("name", "Unknown")
                    path = file_data.get("path", "")
                    summary = file_data.get("summary", "No summary").replace("\n", " ")
                    
                    # Create clickable link (File URI)
                    link_path = path.replace(" ", "%20").replace("\\", "/")
                    # User requested Path column to be clickable
                    path_link = f"[{path}](file:///{link_path})"
                    
                    f.write(f"| {name} | {path_link} | {summary} |\n")
                
                f.write(f"\n")
                
        return {"status": "success", "path": report_path}
    except Exception as e:
        print(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/select_directory")
async def select_directory():
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True) # Bring to front
        
        # Open directory dialog
        path = filedialog.askdirectory()
        
        root.destroy()
        
        return {"path": path}
    except Exception as e:
        print(f"Directory selection error: {e}")
        return {"path": "", "error": str(e)}

@app.get("/")
async def read_root():
    return FileResponse(resource_path("backend/static/index.html"))

# Global download state
download_state = {
    "status": "idle", # idle, downloading, completed, error
    "progress": 0,
    "total": 0,
    "error": None
}

@app.get("/model_status")
async def get_model_status():
    import sys
    # Determine base directory
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
        
    model_dir = os.path.join(base_dir, "models")
    # Check for both casing variations
    possible_files = [
        "qwen2.5-7b-instruct-q4_k_m.gguf",
        "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    ]
    
    exists = False
    found_path = ""
    
    for fname in possible_files:
        fpath = os.path.join(model_dir, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            exists = True
            found_path = fpath
            break
            
    # Default to lowercase for display if none found
    if not found_path:
        found_path = os.path.join(model_dir, "qwen2.5-7b-instruct-q4_k_m.gguf")
        
    return {"exists": exists, "path": found_path}

@app.post("/download_model")
async def download_model(background_tasks: BackgroundTasks):
    global download_state
    if download_state["status"] == "downloading":
        return {"status": "already_downloading"}
    
    download_state = {
        "status": "downloading",
        "progress": 0,
        "total": 0,
        "error": None
    }
    
    background_tasks.add_task(run_download_model)
    return {"status": "started"}

@app.get("/download_progress")
async def get_download_progress():
    return download_state

def run_download_model():
    global download_state
    
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(".")
            
        model_dir = os.path.join(base_dir, "models")
        os.makedirs(model_dir, exist_ok=True)
        target_path = os.path.join(model_dir, "qwen2.5-7b-instruct-q4_k_m.gguf")
        
        # URL for Qwen2.5-7B-Instruct-GGUF (Q4_K_M)
        # Using bartowski's quantization which is reliable and available
        url = "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
        
        def report_hook(block_num, block_size, total_size):
            download_state["progress"] = block_num * block_size
            download_state["total"] = total_size
            
        urllib.request.urlretrieve(url, target_path, report_hook)
        
        download_state["status"] = "completed"
        download_state["progress"] = download_state["total"]
        
        # Reload model if possible
        try:
            from backend.services.slm import get_llm
            # Force reload logic if needed, but get_llm checks for _llm is None.
            # We might need to reset _llm in slm.py, but for now user can just restart or we rely on next call
            pass 
        except:
            pass
            
    except Exception as e:
        download_state["status"] = "error"
        download_state["error"] = str(e)
        print(f"Download error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}

def find_free_port(start_port=8000, max_port=8100):
    import socket
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise IOError("No free ports found")

if __name__ == "__main__":
    import uvicorn
    
    # Find a free port
    try:
        port = find_free_port()
    except IOError:
        print("Error: No free ports available.")
        sys.exit(1)
        
    # Set port in environment for lifespan handler to use
    os.environ["PORT"] = str(port)
    
    # Disable reload if running as frozen executable
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
