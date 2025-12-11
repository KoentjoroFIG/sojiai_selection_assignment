# Airworthiness Directive (AD) Extractor & Evaluator

An automated pipeline for extracting applicability rules from Airworthiness Directive PDFs and evaluating aircraft configurations against those rules.

## 📋 Overview

This project addresses the challenge of processing hundreds of Airworthiness Directives (ADs) issued by aviation authorities (FAA, EASA). Instead of manual extraction, this pipeline:

1. **Extracts** applicability rules from AD PDFs using LLM-powered parsing
2. **Structures** the extracted rules into machine-readable JSON format
3. **Evaluates** whether specific aircraft configurations are affected by each AD

## 🏗️ Project Structure

```
AI_Assignment/
├── ad_docs/                    # Source AD PDF documents
│   ├── EASA_2025‑0254.pdf
│   └── FAA_2025‑23‑53.pdf
├── ad_extractor/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirement.txt         # Python dependencies
│   ├── api/
│   │   ├── schema.py           # Core Pydantic models
│   │   ├── ad_extractor/       # PDF extraction & LLM parsing
│   │   │   ├── ad_extractors.py      # LLM extraction strategies
│   │   │   ├── document_extractors.py # PDF text extraction
│   │   │   └── views.py              # Extraction API endpoints
│   │   ├── evaluator/          # Aircraft evaluation logic
│   │   │   ├── evaluator.py          # Core evaluation engine
│   │   │   ├── test_case.py          # Test aircraft configurations
│   │   │   └── views.py              # Evaluation API endpoints
│   │   └── ai_chat/            # AI chat interface
│   └── config/
│       └── config.py           # Application settings
├── output/                     # Extracted AD JSON & evaluation results
│   ├── EASA-2025-0254R1_parsed.json
│   ├── FAA-2025-23-53_parsed.json
│   └── evaluation_results.json
├── README.md                   # This file
└── report.md                   # Technical analysis report
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (or compatible LLM provider)

### Automated Setup (Recommended)

We provide automated setup scripts for quick installation:

#### For Windows Users

```cmd
setup.bat
```

#### For Linux/macOS Users

```bash
./setup.sh
```

**After running the script:**

1. Edit `ad_extractor/.env` and add your OpenAI API key:
   ```env
   LLM_API_KEY=sk-proj-your-key-here
   BASE_URL=https://api.openai.com/v1
   ```

---

### Manual Installation (Alternative)

If you prefer manual setup:

1. **Clone the repository**

   ```bash
   git clone https://github.com/KoentjoroFIG/sojiai_selection_assignment.git
   cd AI_Assignment
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate
   or
   source .venv\Scripts\activate

   # Unix/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   cd ad_extractor
   pip install -r requirement.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the `ad_extractor` directory:

   ```env
   LLM_API_KEY=your_openai_api_key_here
   BASE_URL=https://api.openai.com/v1
   ```

### Running the Application

0. **Ensure the virtual environment is activated**

   - On Windows:

   ```cmd
   .venv\Scripts\activate
   ```

   or

   ```bash
   source .venv\Scripts\activate
   ```

   - On Unix/macOS:

   ```bash
   source .venv/bin/activate
   ```

1. **Start the FastAPI server**

   ```bash
   cd ad_extractor
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📄 To Test It Based on The Assignment Specification

1. **Visit the Swagger UI at** `http://localhost:8000/docs`
2. **Run the endpoints in `Assignment` section in order**
   - `/ad-extractor/extraction_test` to extract AD rules from provided PDFs
   - `/evaluator/evaluation_test` to evaluate structured aircraft configurations using rule-based logic and validate it using the test cases provided
   - `/ai-chat/chat` to interactively evaluate unstructured aircraft descriptions using LLM assistance using natural language questions.
3. **Check the output files in the `output/` directory** for extracted JSON and evaluation results.
