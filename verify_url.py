import urllib.request
import urllib.error

url = "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

print(f"Testing URL: {url}")

try:
    req = urllib.request.Request(url, method="HEAD")
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print("URL is valid.")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except Exception as e:
    print(f"Error: {e}")
