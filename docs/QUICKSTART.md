# Quick Start Guide

Get the Intelligent Claims QA Service running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Tesseract OCR installed ([Windows installer](https://github.com/UB-Mannheim/tesseract/wiki))
- Poppler installed ([Windows download](https://github.com/oschwartz10612/poppler-windows/releases/))

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment (if not already activated)
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Verify Environment Variables

Your `.env` file is already configured with:
- ✅ TOGETHER_API_KEY
- ✅ LLM_MODEL
- ✅ LLM_TEMPERATURE
- ✅ LLM_MAX_TOKENS

## Run the Service

```bash
uvicorn app:app --reload --port 8000
```

The service will start at `http://localhost:8000`

## Test It

### Option 1: Use the Test Script

```bash
python test_service.py path/to/your/claim_document.pdf
```

### Option 2: Use the Interactive API Docs

1. Open browser: `http://localhost:8000/docs`
2. Click "Try it out" on `/extract`
3. Upload a claim document
4. Copy the `document_id` from the response
5. Use `/ask` with the `document_id` to ask questions

### Option 3: Use cURL

**Extract document:**
```bash
curl -X POST "http://localhost:8000/extract" -F "file=@sample_claim.pdf"
```

**Ask question:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "your-doc-id-here", "question": "What medications were prescribed?"}'
```

## Sample Data

Download sample medical claim documents from:
https://drive.google.com/drive/folders/1Zl8spNwE7xe8jMaG3GUiIwvkE0z73-e4?usp=sharing

## Troubleshooting

### Tesseract not found
- Make sure Tesseract is in your system PATH
- Or add to `ocr_utils.py`: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### Poppler not found
- Download Poppler for Windows
- Add the `bin` folder to your system PATH

### API Error 401
- Check that your `TOGETHER_API_KEY` is valid in `.env`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [flow.txt](flow.txt) for implementation details
- Explore the API at `http://localhost:8000/docs`

---

**Need Help?** See README.md for detailed troubleshooting and documentation.
