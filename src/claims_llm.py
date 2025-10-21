"""
LLM service for medical claims extraction
Uses Together AI API to normalize and extract structured data from OCR text
"""
import httpx
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))


def build_system_prompt_with_examples() -> str:
    """
    Build system prompt with schema and few-shot examples for claims extraction
    """
    return """You are an expert medical claims data extraction assistant. Your job is to extract structured information from OCR text of medical invoices and claim sheets.

OUTPUT REQUIREMENTS:
- Output ONLY valid JSON matching the schema below
- If a field is unknown or not found, use null
- For arrays, use [] if no data found
- Be precise with numbers, dates, and codes

JSON SCHEMA:
{
  "patient": {
    "name": "string|null",
    "age": "integer|null"
  },
  "diagnoses": [
    {"description": "string", "icd10": "string|null"}
  ],
  "medications": [
    {"name": "string", "dosage": "string|null", "quantity": "string|null"}
  ],
  "procedures": ["string"],
  "admission": {
    "was_admitted": "boolean",
    "admission_date": "YYYY-MM-DD|null",
    "discharge_date": "YYYY-MM-DD|null"
  },
  "total_amount": "string|null",
  "document": {
    "source_filename": "string",
    "invoice_number": "string|null",
    "invoice_date": "YYYY-MM-DD HH:MM:SS|null",
    "facility": "string|null",
    "insurer": "string|null",
    "scheme": "string|null",
    "claim_number": "string|null",
    "reference_no": "string|null"
  },
  "member": {
    "member_name": "string|null",
    "member_number": "string|null"
  },
  "line_items": [
    {
      "code": "string|null",
      "description": "string",
      "qty": "integer",
      "unit_price": "float",
      "line_total": "float"
    }
  ],
  "totals": {
    "net_amount": "float|null",
    "invoice_amount": "float|null",
    "currency": "string|null"
  }
}

EXAMPLE 1:
OCR Input:
INVOICE NUMBER: 10002
MEMBER NAME: Emily Davis
MEMBER NUMBER: UU223344-06
INVOICE DATE: 2024-11-01 00:00:00
SERVICE PROVIDER: LIFELINK MEDICAL CENTER
DIAGNOSIS: Dermatitis
Patient Age: 34
13119033 DOXYCYCLINE 100MG TABLETS 1 3000 3000.0
Net Value: 49000.0

Expected Output:
{
  "patient": {"name": "Emily Davis", "age": 34},
  "diagnoses": [{"description": "Dermatitis", "icd10": null}],
  "medications": [{"name": "DOXYCYCLINE 100MG TABLETS", "dosage": "100mg", "quantity": "1"}],
  "procedures": [],
  "admission": {"was_admitted": false, "admission_date": null, "discharge_date": null},
  "total_amount": "49000.0",
  "document": {
    "source_filename": "claim.pdf",
    "invoice_number": "10002",
    "invoice_date": "2024-11-01 00:00:00",
    "facility": "LIFELINK MEDICAL CENTER",
    "insurer": null,
    "scheme": null,
    "claim_number": null,
    "reference_no": null
  },
  "member": {"member_name": "Emily Davis", "member_number": "UU223344-06"},
  "line_items": [
    {"code": "13119033", "description": "DOXYCYCLINE 100MG TABLETS", "qty": 1, "unit_price": 3000.0, "line_total": 3000.0}
  ],
  "totals": {"net_amount": 49000.0, "invoice_amount": 49000.0, "currency": null}
}

EXAMPLE 2:
OCR Input:
FINAL INVOICE
Insurer Name: HEALTHGUARD
Scheme Name: HEALTHGUARD ELITE
Claim Number: 98276340215
Invoice Date: 2025-06-17
Patient Name: Miriam Njeri
Patient Age: 45
Diagnosis: Hypertension I10
Diagnosis: Type 2 Diabetes Mellitus E11
Procedure: Blood Glucose Test
Medication: Metformin 500mg - 30 tablets
Inv amt. 22,800.00

Expected Output:
{
  "patient": {"name": "Miriam Njeri", "age": 45},
  "diagnoses": [
    {"description": "Hypertension", "icd10": "I10"},
    {"description": "Type 2 Diabetes Mellitus", "icd10": "E11"}
  ],
  "medications": [{"name": "Metformin", "dosage": "500mg", "quantity": "30 tablets"}],
  "procedures": ["Blood Glucose Test"],
  "admission": {"was_admitted": false, "admission_date": null, "discharge_date": null},
  "total_amount": "22800.00",
  "document": {
    "source_filename": "claim.pdf",
    "invoice_number": null,
    "invoice_date": "2025-06-17 00:00:00",
    "facility": null,
    "insurer": "HEALTHGUARD",
    "scheme": "HEALTHGUARD ELITE",
    "claim_number": "98276340215",
    "reference_no": null
  },
  "member": {"member_name": null, "member_number": null},
  "line_items": [],
  "totals": {"net_amount": 22800.0, "invoice_amount": 22800.0, "currency": null}
}

Now extract data from the following OCR text and output ONLY the JSON object:"""


async def llm_normalize(ocr_text: str, source_filename: str) -> dict:
    """
    Use LLM to normalize OCR text into structured JSON

    Args:
        ocr_text: Raw OCR extracted text
        source_filename: Original filename

    Returns:
        Structured dictionary matching schema
    """
    if not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY not found in environment variables")

    # Build messages
    messages = [
        {"role": "system", "content": build_system_prompt_with_examples()},
        {"role": "user", "content": f"source_filename: {source_filename}\n\nOCR TEXT:\n{ocr_text}"}
    ]

    # Prepare API request
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.0,
        "stop": ["<|eot_id|>", "<|eom_id|>"]
    }

    try:
        # Make API request
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                TOGETHER_API_URL,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            # Parse response
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"].strip()

            # Clean up response (remove markdown code blocks if present)
            generated_text = re.sub(r"^```json\s*|\s*```$", "", generated_text, flags=re.IGNORECASE | re.DOTALL).strip()

            # Parse JSON
            data = json.loads(generated_text)

            # Sanity fixes
            if "document" in data:
                data["document"]["source_filename"] = source_filename

                # Normalize date format
                if data["document"].get("invoice_date"):
                    date_str = data["document"]["invoice_date"]
                    if len(date_str) == 10:  # Just date, no time
                        data["document"]["invoice_date"] = date_str + " 00:00:00"

            # Ensure patient exists
            if "patient" not in data:
                data["patient"] = {"name": None, "age": None}

            # Ensure admission exists
            if "admission" not in data:
                data["admission"] = {
                    "was_admitted": False,
                    "admission_date": None,
                    "discharge_date": None
                }

            # Ensure arrays exist
            if "diagnoses" not in data:
                data["diagnoses"] = []
            if "medications" not in data:
                data["medications"] = []
            if "procedures" not in data:
                data["procedures"] = []

            return data

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
        raise Exception(f"Together AI API error ({e.response.status_code}): {error_detail}")

    except httpx.TimeoutException:
        raise Exception("Together AI API request timed out")

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM JSON response: {str(e)}\nResponse: {generated_text}")

    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")


async def answer_question(question: str, claim_data: dict, raw_text: str) -> str:
    """
    Answer a question about extracted claim data using LLM

    Args:
        question: User's question
        claim_data: Structured claim data
        raw_text: Original OCR text for context

    Returns:
        Answer string
    """
    if not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY not found in environment variables")

    # Build context from structured data
    context = f"""CLAIM DATA:
{json.dumps(claim_data, indent=2)}

ORIGINAL TEXT:
{raw_text[:2000]}"""  # Limit context size

    system_prompt = """You are a helpful assistant answering questions about medical claim documents.
Use the provided structured data and original text to answer questions accurately and concisely.
If the information is not available, say so clearly."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context}\n\nQuestion: {question}\n\nProvide a clear, concise answer:"}
    ]

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300,
        "top_p": 0.9,
        "stop": ["<|eot_id|>", "<|eom_id|>"]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                TOGETHER_API_URL,
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()

            return answer

    except Exception as e:
        raise Exception(f"Error answering question: {str(e)}")
