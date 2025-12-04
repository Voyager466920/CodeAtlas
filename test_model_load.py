
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

try:
    from llama_cpp import Llama
    print("llama_cpp imported successfully")
except ImportError:
    print("llama_cpp NOT installed")
    sys.exit(1)

base_dir = os.path.abspath(".")
model_dir = os.path.join(base_dir, "models")
split_file = os.path.join(model_dir, "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf")

print(f"Testing model loading from: {split_file}")

if not os.path.exists(split_file):
    print("Split file does not exist!")
    sys.exit(1)

try:
    llm = Llama(
        model_path=split_file,
        n_ctx=2048,
        verbose=True
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
