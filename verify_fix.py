
import os
import sys
import asyncio

# Add backend to path
sys.path.append(os.getcwd())

from backend.main import get_model_status

async def test_model_status():
    print("Testing model status...")
    status = await get_model_status()
    print(f"Model status: {status}")
    
    # We expect exists to be False because we only have split files
    # and we modified the code to ignore them.
    if status["exists"] is False:
        print("SUCCESS: Model correctly reported as missing (ignoring split files).")
    else:
        print("FAILURE: Model reported as found (still detecting split files or single file exists).")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_model_status())
