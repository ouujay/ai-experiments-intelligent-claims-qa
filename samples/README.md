# Sample Medical Claim Documents

This directory contains example medical claim documents for testing the Intelligent Claims QA Service.

## Available Samples

### EXAMPLE_IMAGE_1.pdf
**Type:** Outpatient medical claim
**Features:**
- Patient information (name, member number)
- Single diagnosis
- Line items with medication details (code, description, quantity, price)
- Net value total
- Authorization status

**Good for testing:**
- Basic extraction
- Medication parsing
- Line item extraction
- Total amount calculation

### EXAMPLE_IMAGE_2.pdf
**Type:** Hospital final invoice
**Features:**
- Insurer and scheme information
- Multiple diagnoses with ICD-10 codes
- Patient demographics
- Treatment details with timestamps
- Running balance
- Complex financial breakdown

**Good for testing:**
- ICD-10 code extraction
- Multiple diagnoses
- Insurer information parsing
- Complex document structure
- Timestamp handling

## Usage

### With Test Script

```bash
# Test with EXAMPLE_IMAGE_1
python tests/test_service.py samples/EXAMPLE_IMAGE_1.pdf

# Test with EXAMPLE_IMAGE_2
python tests/test_service.py samples/EXAMPLE_IMAGE_2.pdf
```

### With cURL

```bash
# Extract data from sample
curl -X POST "http://localhost:8000/extract" \
  -F "file=@samples/EXAMPLE_IMAGE_1.pdf"
```

### With Python

```python
import requests

with open("samples/EXAMPLE_IMAGE_1.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": f}
    )

print(response.json())
```

## Expected Output Structure

Both samples will extract data in this format:

```json
{
  "document_id": "...",
  "data": {
    "patient": {
      "name": "string",
      "age": 34
    },
    "diagnoses": [
      {"description": "...", "icd10": "..."}
    ],
    "medications": [
      {"name": "...", "dosage": "...", "quantity": "..."}
    ],
    "procedures": ["..."],
    "admission": {
      "was_admitted": false,
      "admission_date": null,
      "discharge_date": null
    },
    "total_amount": "...",
    "document": {...},
    "member": {...},
    "line_items": [...],
    "totals": {...}
  }
}
```

## Adding Your Own Samples

You can add your own medical claim documents to this directory:

1. **Supported formats:** PDF, PNG, JPG, JPEG, TIFF, BMP
2. **Best quality:** 300 DPI or higher for better OCR
3. **Privacy:** Ensure documents are anonymized or test data only

## Additional Test Data

More sample documents are available at:
https://drive.google.com/drive/folders/1Zl8spNwE7xe8jMaG3GUiIwvkE0z73-e4?usp=sharing

## Notes

- These samples are for testing and development purposes only
- They demonstrate the variety of formats the service can handle
- Use them to verify the extraction pipeline is working correctly
- They serve as examples for the expected document structure

---

**Need help?** See the main [README.md](../README.md) or [documentation](../docs/README.md)
