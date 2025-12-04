import os
import ast
import json
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    print("Warning: llama_cpp not found. SLM features will be disabled.")

# Global model instance
_llm = None

def get_llm():
    global _llm
    if Llama is None:
        return None
    if _llm is None:
        import sys
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # If running as compiled exe, look in the same directory as the exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # Use relative path from the current file location
            # backend/services/slm.py -> backend/services -> backend -> root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Check for single file first (both casings)
        # Expected structure: <base_dir>/models/qwen...
        model_dir = os.path.join(base_dir, "models")
        
        possible_files = [
            "qwen2.5-7b-instruct-q4_k_m.gguf",
            "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
        ]
        
        model_path = ""
        for fname in possible_files:
            fpath = os.path.join(model_dir, fname)
            if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
                model_path = fpath
                break
        
        # Fallback if not found
        if not model_path:
            model_path = os.path.join(model_dir, "qwen2.5-7b-instruct-q4_k_m.gguf")
            
        print(f"[SLM] Base Dir: {base_dir}")
        print(f"[SLM] Looking for model at: {model_path}")
        
        if not os.path.exists(model_path) or os.path.getsize(model_path) == 0:
            print(f"[SLM] Model file not found or empty at: {model_path}")
            return None

        try:
            _llm = Llama(
                model_path=model_path,
                n_ctx=2048,  # Context window
                n_gpu_layers=-1, # Offload all layers to GPU if available
                verbose=False
            )
            print("[SLM] Model loaded successfully.")
        except Exception as e:
            print(f"[SLM] Failed to load model: {e}")
            _llm = None
    return _llm

def analyze_file_content(filename: str, content: str, language: str = "ko") -> dict:
    llm = get_llm()
    
    # Fallback to static analysis if model is not loaded or content is too large/empty
    if llm is None or not content.strip() or len(content) > 10000: # Simple length check for now
        return _static_analysis(filename, content, language)

    if language == 'en':
        system_instruction = """You are a helpful coding assistant. Analyze the following code file and provide a concise summary (1-2 sentences) and 3-5 keywords in English.
Respond ONLY in JSON format with keys "summary" and "keywords".
Do NOT use Chinese characters. Use ONLY English.
Example: {"summary": "This file implements ...", "keywords": ["Python", "API", "Auth"]}"""
    else:
        system_instruction = """You are a helpful coding assistant. Analyze the following code file and provide a concise summary (1-2 sentences) and 3-5 keywords in Korean.
Respond ONLY in JSON format with keys "summary" and "keywords".
Do NOT use Chinese characters. Use ONLY Korean.
Example: {"summary": "이 파일은 ... 기능을 구현합니다.", "keywords": ["Python", "API", "인증"]}"""

    prompt = f"""<|im_start|>system
{system_instruction}
<|im_end|>
<|im_start|>user
Filename: {filename}
Content:
```
{content[:2000]} 
```
(Content truncated if too long)
<|im_end|>
<|im_start|>assistant
"""
    
    try:
        output = llm(
            prompt,
            max_tokens=200,
            stop=["<|im_end|>"],
            echo=False
        )
        response_text = output['choices'][0]['text'].strip()
        
        # Simple cleanup to ensure JSON parsing
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result = json.loads(response_text)
        
        # Validate structure
        if "summary" not in result or "keywords" not in result:
             raise ValueError("Invalid JSON structure")
             
        return result

    except Exception as e:
        print(f"SLM analysis failed: {e}. Falling back to static analysis.")
        return _static_analysis(filename, content, language)

def _static_analysis(filename: str, content: str, language: str = "ko") -> dict:
    # Static analysis logic
    ext = os.path.splitext(filename)[1].lower()
    
    is_en = language == 'en'
    
    if is_en:
        summary = f"{os.path.basename(filename)} is a {ext} file."
        keywords = [ext.replace('.', '').upper(), "File"]
    else:
        summary = f"{os.path.basename(filename)}은 {ext} 파일입니다."
        keywords = [ext.replace('.', '').upper(), "파일"]

    if ext == '.py':
        try:
            tree = ast.parse(content)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]
            
            if classes:
                if is_en:
                    summary += f" Defines classes: {', '.join(classes[:3])}{'...' if len(classes)>3 else ''}."
                else:
                    summary += f" 클래스를 정의합니다: {', '.join(classes[:3])}{'...' if len(classes)>3 else ''}."
                keywords.extend(classes[:5])
            if functions:
                if is_en:
                    summary += f" Contains functions: {', '.join(functions[:3])}{'...' if len(functions)>3 else ''}."
                else:
                    summary += f" 함수를 포함합니다: {', '.join(functions[:3])}{'...' if len(functions)>3 else ''}."
                keywords.extend(functions[:5])
            
            keywords.append("Python")
            if is_en:
                keywords.append("Source")
            else:
                keywords.append("소스")
        except Exception:
            if is_en:
                summary += " Contains Python source code."
            else:
                summary += " Python 소스 코드를 포함합니다."
            keywords.append("Python")

    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        if is_en:
            keywords.append("Frontend")
        else:
            keywords.append("프론트엔드")
            
        if 'react' in content.lower():
            if is_en:
                summary += " Appears to be a React component."
            else:
                summary += " React 컴포넌트로 보입니다."
            keywords.append("React")
        if 'function' in content or 'const' in content:
            if is_en:
                summary += " Contains logic definitions."
            else:
                summary += " 로직 정의를 포함합니다."

    elif ext == '.html':
        if is_en:
            summary += " Defines HTML structure."
            keywords.extend(["HTML", "Structure"])
        else:
            summary += " HTML 구조를 정의합니다."
            keywords.extend(["HTML", "구조"])
        
    elif ext == '.css':
        if is_en:
            summary += " Contains style definitions."
            keywords.extend(["CSS", "Style"])
        else:
            summary += " 스타일 정의를 포함합니다."
            keywords.extend(["CSS", "스타일"])
        
    elif ext == '.md':
        if is_en:
            summary += " Appears to be a documentation file."
            keywords.extend(["Markdown", "Docs"])
        else:
            summary += " 문서 파일로 보입니다."
            keywords.extend(["Markdown", "문서"])

    return {
        "summary": summary,
        "keywords": list(set(keywords))[:8] # Limit keywords
    }
