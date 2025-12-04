import requests
import os
import json
import sys

sys.path.append(os.getcwd())

def test_export():
    url = "http://localhost:8000/export_report"
    root_path = os.path.abspath("test_export_dir")
    
    if not os.path.exists(root_path):
        os.makedirs(root_path)
        
    payload = {
        "root_path": root_path,
        "files": [
            {
                "name": "test_file.py",
                "path": os.path.join(root_path, "test_file.py"),
                "summary": "This is a test summary.",
                "keywords": ["test", "python"]
            },
            {
                "name": "another_file.js",
                "path": os.path.join(root_path, "another_file.js"),
                "summary": "Another summary.",
                "keywords": ["javascript", "code"]
            },
            {
                "name": "nested.py",
                "path": os.path.join(root_path, "subdir", "nested.py"),
                "summary": "Nested file summary.",
                "keywords": ["python", "nested"]
            }
        ]
    }
    
    try:
        # Note: This requires the server to be running. 
        # Since I cannot easily start the server and keep it running in the background while running this script in the same environment without blocking,
        # I will simulate the logic directly by importing the function if possible, or just assume manual verification is needed for the full integration.
        # However, I can try to import the function from main.py and run it directly if I mock the request object.
        
        from backend.main import export_report, ExportRequest
        import asyncio
        
        req = ExportRequest(**payload)
        
        # Run the async function
        result = asyncio.run(export_report(req))
        
        print("Export result:", result)
        
        report_path = os.path.join(root_path, "analysis_report.md")
        if os.path.exists(report_path):
            print(f"Success: {report_path} created.")
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
                print("Content preview:")
                print(content[:200])
        else:
            print("Failure: Report file not found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_export()
