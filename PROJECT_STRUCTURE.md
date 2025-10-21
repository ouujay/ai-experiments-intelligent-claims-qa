# Project Structure

This document describes the organized structure of the Intelligent Claims QA Service project.

## Directory Layout

```
curacel-project/
│
├── 📁 src/                          # Source Code (Main Application)
│   ├── __init__.py                  # Package initializer
│   ├── app.py                       # FastAPI application & API endpoints
│   ├── ocr_utils.py                 # OCR processing (Tesseract + pdf2image)
│   ├── preparse.py                  # Regex-based pre-parser for claims data
│   └── claims_llm.py                # LLM integration (Together AI)
│
├── 📁 tests/                        # Test Scripts
│   └── test_service.py              # End-to-end API test script
│
├── 📁 docs/                         # Documentation
│   ├── README.md                    # Full detailed documentation
│   ├── QUICKSTART.md                # 5-minute quick start guide
│   └── flow.txt                     # Implementation plan & technical design
│
├── 📁 samples/                      # Sample Medical Claim Documents
│   ├── README.md                    # Guide to sample documents
│   ├── EXAMPLE_IMAGE_1.pdf          # Sample outpatient claim
│   └── EXAMPLE_IMAGE_2.pdf          # Sample hospital invoice
│
├── 📁 scripts/                      # Utility Scripts
│   └── test_all_samples.py          # Batch test all samples
│
├── 📁 venv/                         # Virtual Environment (not in git)
│
├── 📄 run.py                        # Main entry point to start the service
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Project overview & quick navigation
├── 📄 SETUP_CHECKLIST.md            # Setup verification checklist
├── 📄 PROJECT_STRUCTURE.md          # This file
│
├── 📄 .env                          # Environment variables (not in git)
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
│
├── 📄 llm.py                        # Reference LLM service (from old project)
└── 📄 AI_ML Engineer Take Home Task (Mid-Level) (1).pdf  # Task specification
```

## File Descriptions

### Core Application (`src/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `app.py` | FastAPI application with REST endpoints | `/extract`, `/ask`, `/documents` |
| `ocr_utils.py` | OCR text extraction from images/PDFs | `load_and_ocr()`, `ocr_image()`, `ocr_pdf()` |
| `preparse.py` | Regex-based pattern matching for deterministic extraction | `preparse_invoice_text()`, `merge_preparse_into_llm()` |
| `claims_llm.py` | Together AI LLM integration for data normalization | `llm_normalize()`, `answer_question()` |

### Testing (`tests/`)

| File | Purpose | Usage |
|------|---------|-------|
| `test_service.py` | End-to-end API testing | `python tests/test_service.py samples/EXAMPLE_IMAGE_1.pdf` |

### Documentation (`docs/`)

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Complete technical documentation | Developers, reviewers |
| `QUICKSTART.md` | Fast setup guide (5 min) | New users |
| `flow.txt` | Implementation plan & architecture | Technical reviewers |

### Samples (`samples/`)

| File | Type | Description |
|------|------|-------------|
| `EXAMPLE_IMAGE_1.pdf` | Outpatient claim | Line items, single diagnosis, member info |
| `EXAMPLE_IMAGE_2.pdf` | Hospital invoice | Multiple diagnoses, ICD-10 codes, timestamps |
| `README.md` | Guide | Documentation for sample files |

### Scripts (`scripts/`)

| File | Purpose | Usage |
|------|---------|-------|
| `test_all_samples.py` | Batch test all sample documents | `python scripts/test_all_samples.py` |

### Configuration Files

| File | Purpose | Notes |
|------|---------|-------|
| `run.py` | Main entry point | Runs FastAPI with uvicorn |
| `requirements.txt` | Python dependencies | Install with `pip install -r requirements.txt` |
| `.env` | Environment variables | Contains API keys (not in git) |
| `.env.example` | Environment template | Safe to commit |
| `.gitignore` | Git ignore rules | Excludes venv, .env, __pycache__ |

### Root Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Project overview | First thing to read |
| `SETUP_CHECKLIST.md` | Setup verification | During installation |
| `PROJECT_STRUCTURE.md` | This file | To understand organization |

## Module Dependencies

```
app.py
  ├── ocr_utils.py      (OCR processing)
  ├── preparse.py       (Regex extraction)
  └── claims_llm.py     (LLM normalization)
      └── (Together AI API)

test_service.py
  └── app.py (via HTTP API)

test_all_samples.py
  └── app.py (via HTTP API)
```

## Data Flow

```
User Upload (Image/PDF)
    ↓
[app.py] POST /extract
    ↓
[ocr_utils.py] OCR Extraction
    ↓
[preparse.py] Regex Pre-parsing
    ↓
[claims_llm.py] LLM Normalization
    ↓
[preparse.py] Merge Results
    ↓
Return: {document_id, data}
    ↓
User Question
    ↓
[app.py] POST /ask
    ↓
[claims_llm.py] Answer Question
    ↓
Return: {answer}
```

## Import Structure

### Before Reorganization
```python
# All files in root
from ocr_utils import load_and_ocr
from preparse import preparse_invoice_text
from claims_llm import llm_normalize
```

### After Reorganization
```python
# Files organized in src/
from src.ocr_utils import load_and_ocr
from src.preparse import preparse_invoice_text
from src.claims_llm import llm_normalize

# Or with relative imports (within src/)
from .ocr_utils import load_and_ocr
from .preparse import preparse_invoice_text
from .claims_llm import llm_normalize
```

## Key Design Decisions

### 1. Separation of Concerns
- **`src/`** - All source code isolated
- **`tests/`** - Testing separate from implementation
- **`docs/`** - Documentation in dedicated folder
- **`samples/`** - Test data organized separately

### 2. Clear Entry Points
- **`run.py`** - Single command to start the service
- **`tests/test_service.py`** - Single script to test functionality
- **`scripts/test_all_samples.py`** - Batch testing utility

### 3. Progressive Documentation
- **`README.md`** - Quick overview for GitHub visitors
- **`docs/QUICKSTART.md`** - For users who want to run it fast
- **`docs/README.md`** - For deep technical understanding
- **`SETUP_CHECKLIST.md`** - For installation verification

### 4. Sample Data Included
- Users can test immediately without downloading external files
- Examples demonstrate expected document formats
- Good for CI/CD and automated testing

## Adding New Features

### New Extraction Logic
1. Add to `src/preparse.py` (for regex patterns)
2. Update `src/claims_llm.py` (for LLM prompts)
3. Test with `tests/test_service.py`

### New Endpoint
1. Add route to `src/app.py`
2. Import required utilities from `src/`
3. Update API documentation

### New Tests
1. Add test script to `tests/`
2. Update `tests/test_service.py` or create new file
3. Document in `docs/README.md`

## Maintenance

### Adding Dependencies
```bash
pip install new-package
pip freeze > requirements.txt
```

### Running Tests
```bash
# Single file test
python tests/test_service.py samples/EXAMPLE_IMAGE_1.pdf

# Batch test
python scripts/test_all_samples.py
```

### Updating Documentation
1. Update `docs/README.md` for technical changes
2. Update `README.md` for user-facing changes
3. Update `docs/QUICKSTART.md` if setup changes

## Best Practices

### When Working on Code
1. ✅ Always activate virtual environment first
2. ✅ Keep related code in the same module
3. ✅ Use relative imports within `src/`
4. ✅ Test changes with sample data
5. ✅ Update documentation when adding features

### When Adding Files
1. ✅ Source code → `src/`
2. ✅ Tests → `tests/`
3. ✅ Documentation → `docs/`
4. ✅ Sample data → `samples/`
5. ✅ Utility scripts → `scripts/`

### When Committing to Git
1. ✅ Check `.gitignore` is working
2. ✅ Never commit `.env` (API keys)
3. ✅ Never commit `venv/`
4. ✅ Update `README.md` if needed

## Navigation Guide

**Want to...** | **Go to...**
---|---
Understand the project quickly | `README.md` (root)
Get it running in 5 minutes | `docs/QUICKSTART.md`
Read full documentation | `docs/README.md`
Understand architecture | `docs/flow.txt`
Verify installation | `SETUP_CHECKLIST.md`
See project organization | `PROJECT_STRUCTURE.md` (this file)
Understand source code | `src/` folder
Test the service | `tests/test_service.py`
Try sample documents | `samples/` folder
Add utilities | `scripts/` folder

---

**Questions?** See the main [README.md](README.md) or [full documentation](docs/README.md).
