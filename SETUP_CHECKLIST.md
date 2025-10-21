# Setup Checklist

Complete this checklist to ensure your environment is ready to run the Intelligent Claims QA Service.

## ✅ Prerequisites

### System Dependencies

- [ ] **Python 3.8+** installed
  ```bash
  python --version  # Should show 3.8 or higher
  ```

- [ ] **Tesseract OCR** installed
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

  ```bash
  tesseract --version  # Should show version info
  ```

- [ ] **Poppler** installed (for PDF processing)
  - Windows: [Download here](https://github.com/oschwartz10612/poppler-windows/releases/)
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`

## ✅ Project Setup

### 1. Virtual Environment

- [ ] Created virtual environment
  ```bash
  python -m venv venv
  ```

- [ ] Activated virtual environment
  ```bash
  # Windows
  venv\Scripts\activate

  # macOS/Linux
  source venv/bin/activate
  ```

- [ ] Verify activation (should see `(venv)` in terminal prompt)

### 2. Dependencies

- [ ] Installed Python packages
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verify installation
  ```bash
  pip list  # Should show fastapi, pytesseract, etc.
  ```

### 3. Configuration

- [ ] Reviewed `.env` file
  ```bash
  # Should contain:
  TOGETHER_API_KEY=your_key_here
  LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
  LLM_TEMPERATURE=0.0
  LLM_MAX_TOKENS=1500
  ```

- [ ] Obtained Together AI API key from https://api.together.xyz/

- [ ] Updated `TOGETHER_API_KEY` in `.env`

### 4. Verify File Structure

- [ ] Check that all directories exist:
  ```
  ├── src/           # Source code
  ├── tests/         # Test scripts
  ├── docs/          # Documentation
  ├── samples/       # Sample documents
  ├── scripts/       # Utility scripts
  └── run.py         # Main entry point
  ```

## ✅ Running the Service

### 1. Start the Server

- [ ] Start the service
  ```bash
  python run.py
  ```

- [ ] Verify server is running
  - Should see: "Application startup complete"
  - Should be accessible at: http://localhost:8000

### 2. Test the API

- [ ] Health check
  ```bash
  curl http://localhost:8000/
  ```

- [ ] Open interactive docs
  - Visit: http://localhost:8000/docs
  - Should see Swagger UI with API endpoints

### 3. Test with Sample Data

- [ ] Run test script
  ```bash
  python tests/test_service.py samples/EXAMPLE_IMAGE_1.pdf
  ```

- [ ] Verify extraction works
  - Should see "✅ Extraction successful!"
  - Should receive a `document_id`

- [ ] Test question answering
  - Should see answers to test questions

### 4. Batch Test (Optional)

- [ ] Test all samples
  ```bash
  python scripts/test_all_samples.py
  ```

## ✅ Troubleshooting

If you encounter issues:

### Tesseract Not Found
- [ ] Add Tesseract to system PATH
- [ ] Or update `src/ocr_utils.py` with explicit path:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

### Poppler Not Found
- [ ] Add Poppler `bin` folder to system PATH
- [ ] Restart terminal after adding to PATH

### API Key Error (401)
- [ ] Verify `TOGETHER_API_KEY` is correct in `.env`
- [ ] Test API key at https://api.together.xyz/playground

### Import Errors
- [ ] Ensure virtual environment is activated
- [ ] Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- [ ] Change port in `run.py`:
  ```python
  uvicorn.run("src.app:app", host="0.0.0.0", port=8001, reload=True)
  ```

## ✅ Next Steps

Once setup is complete:

- [ ] Read the [full documentation](docs/README.md)
- [ ] Review the [API reference](docs/README.md#api-endpoints)
- [ ] Test with your own claim documents
- [ ] Explore the [implementation plan](docs/flow.txt)

## 📝 Notes

- Keep your virtual environment activated when working on the project
- The `.env` file contains sensitive data - never commit it to version control
- Sample documents are in `samples/` directory
- Logs and errors will appear in the terminal where you ran `python run.py`

## 🎯 Success Criteria

You're ready to go when:

- ✅ Server starts without errors
- ✅ Health check returns 200 OK
- ✅ Sample document extraction succeeds
- ✅ Question answering works
- ✅ Interactive docs load at `/docs`

---

**Need help?** Check the [troubleshooting section](docs/README.md#troubleshooting) in the full documentation.
