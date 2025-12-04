# CodeAtlas - File Structure Visualization Tool

CodeAtlas is a developer tool that visualizes directory structures and uses a Small Language Model (SLM) to summarize the contents of each file.

## 📥 Download

**[Download CodeAtlas v1.0.0 (Windows .exe)](https://github.com/Voyager466920/CodeAtlas/releases/tag/v1.0.0)**

## Features

*   **Folder Structure Visualization**: Visualizes the folder structure of a specified path as a mind map.
*   **AI File Analysis**: Uses a local SLM to summarize file contents and extract keywords.
*   **Markdown Export**: Saves the analyzed results in Markdown table format.
*   **Local Execution**: All data is processed locally and is not sent externally.

## Installation (For Developers)

If you want to run the source code directly instead of using the executable:

1.  **Python Installation**: Python 3.8 or higher is required.
2.  **Clone Repository**:
    ```bash
    git clone https://github.com/Voyager466920/CodeAtlas.git
    cd CodeAtlas
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *   Note: A compiler might be required for `llama-cpp-python`. Refer to the [official documentation](https://github.com/abetlen/llama-cpp-python) if errors occur.

## Model Setup

This tool uses the `Qwen2.5-7B-Instruct` model (GGUF format). **The model file is not included in the GitHub repository and must be downloaded manually.**

1.  Create a `models` folder in the project root.
2.  Download `qwen2.5-7b-instruct-q4_k_m.gguf` (or a compatible model) from Hugging Face and place it in the `models` folder.
3.  Ensure the filename matches `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf` (or update the path in `backend/services/slm.py`).

## Usage

### Windows

Double-click `run.bat` or run it from the terminal:

```cmd
run.bat
```

### Manual Execution

```bash
python backend/main.py
```

Access `http://localhost:8000` in your browser.

---

# CodeAtlas - 파일 구조 시각화 도구 (Korean)

이 도구는 디렉토리 구조를 시각화하고, SLM(Small Language Model)을 사용하여 각 파일의 내용을 요약해주는 개발자용 도구입니다.

## 📥 다운로드 (Download)

**[CodeAtlas v1.0.0 다운로드 (Windows .exe)](https://github.com/Voyager466920/CodeAtlas/releases/tag/v1.0.0)**

## 기능

*   **폴더 구조 시각화**: 지정된 경로의 폴더 구조를 마인드맵 형태로 시각화합니다.
*   **AI 파일 분석**: 로컬 SLM을 사용하여 파일의 내용을 요약하고 키워드를 추출합니다.
*   **Markdown 내보내기**: 분석된 결과를 Markdown 표 형태로 저장할 수 있습니다.
*   **로컬 실행**: 모든 데이터는 로컬에서 처리되며 외부로 전송되지 않습니다.

## 설치 방법 (개발자용)

실행 파일(.exe)이 아닌 소스 코드를 직접 실행하려면 다음 단계를 따르세요.

1.  **Python 설치**: Python 3.8 이상이 설치되어 있어야 합니다.
2.  **저장소 복제**:
    ```bash
    git clone https://github.com/Voyager466920/CodeAtlas.git
    cd CodeAtlas
    ```
3.  **의존성 설치**:
    ```bash
    pip install -r requirements.txt
    ```
    *   참고: `llama-cpp-python` 설치 시 컴파일러가 필요할 수 있습니다. 오류 발생 시 [llama-cpp-python 공식 문서](https://github.com/abetlen/llama-cpp-python)를 참고하세요.

## 모델 설정

이 도구는 `Qwen2.5-7B-Instruct` 모델(GGUF 포맷)을 사용합니다. **GitHub에는 모델 파일이 포함되어 있지 않으므로 직접 다운로드해야 합니다.**

1.  프로젝트 루트에 `models` 폴더를 생성합니다.
2.  Hugging Face 등에서 `qwen2.5-7b-instruct-q4_k_m.gguf` (또는 호환되는 모델)을 다운로드하여 `models` 폴더에 넣습니다.
3.  파일명이 `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf`와 일치해야 합니다. (또는 `backend/services/slm.py`에서 경로 수정)

## 실행 방법

### Windows

`run.bat` 파일을 더블 클릭하거나 터미널에서 실행하세요.

```cmd
run.bat
```

### 수동 실행

```bash
python backend/main.py
```

브라우저에서 `http://localhost:8000`으로 접속하여 사용합니다.

## 주의 사항

*   **보안**: 이 도구는 로컬 개발 환경에서 사용하도록 설계되었습니다. 공용 네트워크나 서버에 배포할 경우 추가적인 보안 설정이 필요합니다.
*   **시스템 파일 접근**: 보안을 위해 시스템 디렉토리(Windows, Program Files 등)에 대한 분석은 차단되어 있습니다.
