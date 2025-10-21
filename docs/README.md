# Intelligent Claims QA Service

A Python microservice for extracting structured data from medical claim documents and answering questions about them using OCR and Large Language Models.

## Overview

This service processes scanned or photographed insurance claim documents to extract key information like patient details, diagnoses, medications, procedures, and financial totals. It combines traditional OCR (Optical Character Recognition) with AI-powered language models to handle unstructured documents with varying formats.

## Features

- **Document Processing**: Upload medical claim sheets as images or PDFs
- **Intelligent Extraction**: Extract structured data including:
  - Patient information (name, age)
  - Diagnoses with ICD-10 codes
  - Medications (name, dosage, quantity)
  - Procedures and treatments
  - Admission details
  - Financial totals
  - Invoice metadata
- **Question Answering**: Ask questions about extracted claim data
- **Hybrid Approach**: Combines regex pattern matching with LLM normalization for accuracy

## Architecture

The service uses a three-stage extraction pipeline:

1. **OCR Layer** (`ocr_utils.py`): Extracts text from images/PDFs using Tesseract
2. **Regex Pre-Parser** (`preparse.py`): Deterministically extracts obvious fields using pattern matching
3. **LLM Normalizer** (`claims_llm.py`): Uses Together AI's Llama model to normalize and complete the extraction
4. **Merge Strategy** (`preparse.py`): Combines regex and LLM results for maximum accuracy

## Tech Stack

- **Framework**: FastAPI
- **OCR**: Tesseract (via pytesseract) + pdf2image
- **LLM**: Together AI API (Meta-Llama-3.1-8B-Instruct-Turbo)
- **Storage**: In-memory (suitable for demo/development)

## Prerequisites

### System Dependencies

**Windows:**
```bash
# Install Tesseract OCR
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH

# Install Poppler (for PDF processing)
# Download from: https://github.com/oschwartz10612/poppler-windows/releases/
# Extract and add bin folder to PATH
```

**macOS:**
```bash
brew install tesseract poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

### Python Requirements

- Python 3.8+
- pip

## Installation

### 1. Clone or navigate to the project directory

```bash
cd "C:\Users\sbnuf\Desktop\projects\curacel project"
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root (or edit existing one):

```env
TOGETHER_API_KEY=your_together_api_key_here
LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1500
```

**To get a Together AI API key:**
1. Sign up at https://api.together.xyz/
2. Navigate to Settings > API Keys
3. Create a new API key
4. Copy and paste it into your `.env` file

## Running the Service

Start the FastAPI server:

```bash
uvicorn app:app --reload --port 8000
```

The service will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. POST `/extract`

Extract structured data from a medical claim document.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image or PDF)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@claim_document.pdf"
```

**Example using Python:**
```python
import requests

with open("claim_document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": f}
    )

print(response.json())
```

**Response:**
```json
{
  "document_id": "abc-123-def-456",
  "data": {
    "patient": {
      "name": "Jane Doe",
      "age": 34
    },
    "diagnoses": [
      {"description": "Malaria", "icd10": null}
    ],
    "medications": [
      {
        "name": "Paracetamol",
        "dosage": "500mg",
        "quantity": "10 tablets"
      }
    ],
    "procedures": ["Malaria test"],
    "admission": {
      "was_admitted": true,
      "admission_date": "2023-06-10",
      "discharge_date": "2023-06-12"
    },
    "total_amount": "₦15,000",
    "document": {
      "source_filename": "claim_document.pdf",
      "invoice_number": "INV-001",
      "invoice_date": "2023-06-12 00:00:00",
      "facility": "General Hospital",
      "insurer": null,
      "scheme": null
    }
  }
}
```

### 2. POST `/ask`

Ask questions about an extracted document.

**Request:**
```json
{
  "document_id": "abc-123-def-456",
  "question": "How many tablets of paracetamol were prescribed?"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "abc-123-def-456",
    "question": "How many tablets of paracetamol were prescribed?"
  }'
```

**Response:**
```json
{
  "answer": "10 tablets"
}
```

### 3. GET `/documents`

List all stored documents (for debugging).

**Response:**
```json
{
  "documents": [
    {
      "document_id": "abc-123-def-456",
      "filename": "claim_document.pdf"
    }
  ]
}
```

### 4. DELETE `/documents/{document_id}`

Delete a document from storage.

## Testing

### Using Sample Documents

Sample medical claim documents are available at:
https://drive.google.com/drive/folders/1Zl8spNwE7xe8jMaG3GUiIwvkE0z73-e4?usp=sharing

Download the sample images and test the `/extract` endpoint:

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@EXAMPLE_IMAGE_1.pdf"
```

### Testing Workflow

1. **Extract document:**
   ```bash
   response=$(curl -X POST "http://localhost:8000/extract" \
     -F "file=@sample_claim.pdf")

   echo $response | jq .
   ```

2. **Get document_id from response:**
   ```bash
   doc_id=$(echo $response | jq -r '.document_id')
   ```

3. **Ask question:**
   ```bash
   curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d "{
       \"document_id\": \"$doc_id\",
       \"question\": \"What medications were prescribed?\"
     }" | jq .
   ```

## Project Structure

```
curacel-project/
├── app.py                 # FastAPI application with endpoints
├── ocr_utils.py          # OCR processing (Tesseract + pdf2image)
├── preparse.py           # Regex-based pre-parser and merge logic
├── claims_llm.py         # Together AI LLM service for extraction
├── llm.py                # Original LLM service (reference)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── flow.txt             # Implementation plan and design doc
└── README.md            # This file
```

## Key Design Decisions

### 1. Hybrid Extraction Approach

**Why regex + LLM?**
- Regex patterns extract obvious fields deterministically (faster, no API cost)
- LLM handles variations, missing fields, and normalization
- Merge strategy takes the best of both approaches

### 2. In-Memory Storage

**Trade-offs:**
- ✅ Simple, fast, no database setup required
- ✅ Suitable for development and demo
- ⚠️ Data lost on restart
- ⚠️ Not suitable for production at scale

**For production:** Consider adding Redis, PostgreSQL, or MongoDB.

### 3. Together AI (Llama 3.1 8B)

**Why this model?**
- Free tier available
- Fast inference
- Good structured output generation
- Cost-effective for extraction tasks

### 4. Synchronous OCR, Async LLM

- OCR is CPU-bound and relatively fast
- LLM calls are I/O-bound and can be slow
- Using async for LLM calls allows handling multiple requests

## Assumptions

1. **Document Format**: Assumes medical claim sheets with standard fields (patient info, diagnoses, medications, totals)
2. **Text Quality**: OCR works best with clear, high-resolution images
3. **Language**: Primarily designed for English text
4. **Currency**: Handles common currency symbols (₦, $, £, €)
5. **Date Formats**: Supports common formats (YYYY-MM-DD, DD/MM/YYYY)

## Limitations & Future Improvements

### Current Limitations

1. **Storage**: In-memory only (data lost on restart)
2. **OCR Quality**: Performance depends on document quality
3. **Handwritten Text**: Poor support for handwritten notes
4. **Multi-language**: Limited to English
5. **Concurrent Processing**: Limited by Together AI rate limits

### Potential Improvements

1. **Persistent Storage**: Add database (PostgreSQL, MongoDB)
2. **Vision Models**: Use GPT-4 Vision or Gemini Vision for better accuracy
3. **Batch Processing**: Queue system for handling multiple documents
4. **Caching**: Cache OCR results to avoid reprocessing
5. **Validation**: Add Pydantic models for strict schema validation
6. **Authentication**: Add API key authentication
7. **Rate Limiting**: Implement request rate limiting
8. **Logging**: Structured logging with ELK stack or similar
9. **Monitoring**: Add Prometheus metrics and Grafana dashboards
10. **Document Versioning**: Track changes to extracted data

## Troubleshooting

### Tesseract Not Found

**Error:** `TesseractNotFoundError`

**Solution:**
- Ensure Tesseract is installed
- Add Tesseract to system PATH
- On Windows, you may need to specify path in code:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

### Poppler Not Found

**Error:** `PDFInfoNotInstalledError`

**Solution:**
- Install poppler-utils (Linux/Mac) or poppler for Windows
- Add poppler `bin` folder to PATH

### Together AI API Errors

**Error:** `Together AI API error (401)`

**Solution:**
- Check that `TOGETHER_API_KEY` is set correctly in `.env`
- Verify API key is valid at https://api.together.xyz/

**Error:** `Together AI API error (429)` - Rate limit exceeded

**Solution:**
- Wait before retrying
- Consider upgrading Together AI plan
- Implement request queuing and retry logic

### Poor Extraction Quality

**Symptoms:** Missing fields, incorrect values

**Solutions:**
1. Ensure source image is high quality (300+ DPI)
2. Check OCR text quality: `print(ocr_text)` in `app.py`
3. Adjust regex patterns in `preparse.py` for your document format
4. Increase `LLM_MAX_TOKENS` if response is truncated
5. Try different LLM models (e.g., Llama 3.1 70B for better accuracy)

## Performance Considerations

### Typical Processing Times

- **OCR (image)**: 2-5 seconds
- **OCR (PDF, 1 page)**: 3-7 seconds
- **LLM Extraction**: 5-15 seconds
- **Total (single document)**: 10-25 seconds

### Optimization Strategies

1. **Parallel Processing**: Process multiple documents concurrently
2. **Caching**: Cache OCR results for duplicate documents
3. **Smaller Models**: Use quantized or smaller models for faster inference
4. **GPU Acceleration**: Use local models with GPU for faster OCR/LLM

## Security Considerations

**Current Implementation:**
- ⚠️ No authentication
- ⚠️ No request rate limiting
- ⚠️ Stores potentially sensitive medical data in memory

**Production Recommendations:**
1. Add API key authentication
2. Implement role-based access control (RBAC)
3. Encrypt data at rest and in transit (HTTPS)
4. Add request rate limiting
5. Sanitize file uploads (scan for malware)
6. Comply with HIPAA/GDPR regulations for medical data
7. Add audit logging for compliance
8. Use secure secret management (AWS Secrets Manager, HashiCorp Vault)

## Contributing

This is a take-home assessment project. For production use, consider:
- Adding comprehensive unit tests
- Implementing integration tests
- Adding CI/CD pipeline
- Code review process
- Documentation for deployment

## License

This project is created for assessment purposes.

## Contact

For questions or issues, please refer to the task specification document.

---

**Built with ❤️ for Curacel**
