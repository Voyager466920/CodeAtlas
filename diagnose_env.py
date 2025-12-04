import sys
import os
import importlib.util

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"CWD: {os.getcwd()}")

def check_package(name):
    spec = importlib.util.find_spec(name)
    found = spec is not None
    print(f"Package '{name}': {'Found' if found else 'Not Found'}")
    return found

check_package("llama_cpp")
check_package("huggingface_hub")
check_package("fastapi")

try:
    import llama_cpp
    print(f"llama_cpp version: {llama_cpp.__version__}")
except ImportError:
    print("Could not import llama_cpp")
except Exception as e:
    print(f"Error importing llama_cpp: {e}")
