import uvicorn
import os
import sys

if __name__ == "__main__":
    # Import app
    from backend.main import app
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
