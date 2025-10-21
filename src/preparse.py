"""
Regex pre-parser for medical claim invoices
Extracts structured data using pattern matching before LLM normalization
"""
import re
from typing import Dict, Any, List, Optional


def parse_numbers(s: str) -> Optional[float]:
    """
    Parse string to float, handling commas and currency symbols

    Args:
        s: Number string (e.g., "1,234.56" or "₦15,000")

    Returns:
        Float value or None if parsing fails
    """
    if not s:
        return None

    # Remove currency symbols and commas
    s2 = re.sub(r'[₦$£€,\s]', '', s).strip()

    try:
        return float(s2)
    except:
        return None


def preparse_invoice_text(text: str, source_filename: str) -> Dict[str, Any]:
    """
    Pre-parse invoice text using regex patterns
    Handles the specific formats in medical claim documents

    Args:
        text: OCR extracted text
        source_filename: Original filename

    Returns:
        Partially structured data dictionary
    """
    # Initialize structure
    T = {
        "document": {"source_filename": source_filename},
        "member": {},
        "patient": {},
        "diagnoses": [],
        "line_items": [],
        "totals": {},
        "meta": {}
    }

    # Common header fields - pattern, (object, key)
    pairs = [
        (r"INVOICE\s*NUMBER\s*:\s*(.+)", ("document", "invoice_number")),
        (r"INVOICE\s*DATE\s*:\s*([0-9:\-\s]+)", ("document", "invoice_date")),
        (r"SERVICE\s*PROVIDER\s*:\s*(.+)", ("document", "facility")),
        (r"Insurer\s*Name\s*:\s*(.+)", ("document", "insurer")),
        (r"Scheme\s*Name\s*:\s*(.+)", ("document", "scheme")),
        (r"Claim\s*Number\s*:\s*(.+)", ("document", "claim_number")),
        (r"Invoice\s*No\s*:\s*(.+)", ("document", "invoice_number")),
        (r"Reference\s*No\s*:\s*(.+)", ("document", "reference_no")),
        (r"(Card|Card/Referral)\s*No\s*:\s*(.+)", ("document", "card_or_referral_no")),
        (r"MEMBER\s*NAME\s*:\s*(.+)", ("member", "member_name")),
        (r"MEMBER\s*NUMBER\s*:\s*(.+)", ("member", "member_number")),
        (r"Patient\s*Name\s*:\s*(.+)", ("patient", "patient_name")),
        (r"AUTHORIZATION\s*BY\s*:\s*(.+)", ("meta", "authorization_status")),
        (r"REGISTRATION\s*NO\s*:\s*(.+)", ("meta", "registration_no")),
    ]

    for pat, (obj, key) in pairs:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            T[obj][key] = m.group(len(m.groups())).strip()

    # Parse diagnoses

    # Single diagnosis format (e.g., "DIAGNOSIS: Dermatitis")
    m = re.search(r"DIAGNOSIS\s*:\s*(.+)", text, re.IGNORECASE)
    if m:
        diag_text = m.group(1).strip()
        if diag_text:
            T["diagnoses"].append({"description": diag_text, "icd10": None})

    # Diagnosis table format with ICD-10 codes (e.g., "Hypertension I10")
    for line in text.splitlines():
        line = line.strip()
        # Match pattern: "Description CODE" where CODE is like I10, E11, J20
        m2 = re.match(r"([A-Za-z0-9 \-/\(\)]+)\s+([A-Z][0-9A-Z]{2,4})$", line)
        if m2:
            desc = m2.group(1).strip()
            icd = m2.group(2).strip()
            # Check if it looks like a medical condition
            if any(w in desc.lower() for w in [
                "hypertension", "diabetes", "bronchitis", "asthma", "malaria",
                "dermatitis", "fever", "infection", "pneumonia", "arthritis"
            ]):
                T["diagnoses"].append({"description": desc, "icd10": icd})

    # Parse line items

    # Format 1: "CODE DESCRIPTION QTY UNITPRICE TOTAL"
    # Example: "13119033 DOXYCYCLINE 100MG TABLETS 1 3000 3000.0"
    lineitem_pat = re.compile(
        r"^(\d{5,})\s+(.+?)\s+(\d+)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)$",
        re.IGNORECASE
    )

    for raw in text.splitlines():
        raw = raw.strip()
        mi = lineitem_pat.match(raw)
        if mi:
            code, desc, qty, unitp, total = mi.groups()
            T["line_items"].append({
                "code": code,
                "description": desc.strip(),
                "qty": int(qty),
                "unit_price": parse_numbers(unitp) or 0.0,
                "line_total": parse_numbers(total) or 0.0,
                "time": None,
                "reference": None
            })

    # Format 2: Treatments with timestamps
    # Example: "2025-06-17 - 09:12:30 MRI Scan 1 3952841 17,500.00 17,500.00"
    tr_pat = re.compile(
        r"^(\d{4}-\d{2}-\d{2})\s*-\s*(\d{2}:\d{2}:\d{2})\s+(.+?)\s+(\d+)\s+(\d+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})$"
    )

    for raw in text.splitlines():
        raw = raw.strip()
        mt = tr_pat.match(raw)
        if mt:
            d, t, desc, qty, ref, amount, balance = mt.groups()
            T["line_items"].append({
                "code": None,
                "description": desc.strip(),
                "qty": int(qty),
                "unit_price": None,
                "line_total": parse_numbers(amount) or 0.0,
                "time": f"{d} - {t}",
                "reference": ref
            })
            # Keep updating last seen balance
            T["totals"]["balance"] = parse_numbers(balance) or 0.0

    # Parse totals

    # Net Value
    net_val = re.search(r"Net\s*Value\s*:\s*([\d,₦]+(?:\.\d+)?)", text, re.IGNORECASE)
    if net_val:
        T["totals"]["net_amount"] = parse_numbers(net_val.group(1)) or 0.0
        T["totals"]["invoice_amount"] = T["totals"]["net_amount"]
        T["totals"]["raw_net_value"] = net_val.group(1).strip()

    # Invoice amount
    inv_amt = re.search(r"Inv(?:oice)?\s*amt\.\s*([\d,₦]+\.\d{2})", text, re.IGNORECASE)
    if inv_amt:
        T["totals"]["invoice_amount"] = parse_numbers(inv_amt.group(1)) or 0.0

    # Total Settlement
    tot_set = re.search(r"Total\s*Settlement\s*([\d,₦]+\.\d{2})", text, re.IGNORECASE)
    if tot_set:
        T["totals"]["total_settlement"] = parse_numbers(tot_set.group(1)) or 0.0

    # Net Amount (can appear separately from Net Value)
    net_amount2 = re.search(r"Net\s*Amount\s*([\d,₦]+\.\d{2})", text, re.IGNORECASE)
    if net_amount2:
        T["totals"]["net_amount"] = parse_numbers(net_amount2.group(1)) or T["totals"].get("net_amount")

    # Total amount (general)
    total_amount = re.search(r"Total\s*[Aa]mount\s*:\s*([\d,₦]+(?:\.\d+)?)", text, re.IGNORECASE)
    if total_amount:
        T["totals"]["total_amount"] = parse_numbers(total_amount.group(1)) or 0.0

    # Normalize missing keys
    T["document"].setdefault("invoice_date", None)
    T["totals"].setdefault("net_amount", None)
    T["totals"].setdefault("invoice_amount", None)
    T["totals"].setdefault("total_settlement", None)
    T["totals"].setdefault("balance", None)
    T["totals"].setdefault("currency", None)
    T["totals"].setdefault("raw_net_value", None)

    return T


def merge_preparse_into_llm(pre: dict, llm: dict) -> dict:
    """
    Merge regex-parsed data into LLM output
    Fills in missing fields and ensures accuracy

    Args:
        pre: Pre-parsed data from regex
        llm: LLM normalized data

    Returns:
        Merged dictionary with best of both
    """
    def fill(path):
        """Fill missing values from pre-parse into llm result"""
        src = pre
        dst = llm

        # Navigate to the value in source
        for p in path[:-1]:
            src = src.get(p, {})
            dst = dst.get(p, {})

        key = path[-1]

        # If LLM didn't extract it but regex did, use regex value
        if not dst.get(key) and src.get(key) is not None:
            # Assign into llm structure
            target_parent = llm
            for p in path[:-1]:
                if p not in target_parent:
                    target_parent[p] = {}
                target_parent = target_parent[p]
            target_parent[key] = src.get(key)

    # Critical fields to check and fill
    critical = [
        ("document", "invoice_number"),
        ("document", "invoice_date"),
        ("document", "facility"),
        ("document", "insurer"),
        ("document", "scheme"),
        ("document", "claim_number"),
        ("document", "reference_no"),
        ("document", "card_or_referral_no"),
        ("member", "member_name"),
        ("member", "member_number"),
        ("patient", "patient_name"),
        ("totals", "invoice_amount"),
        ("totals", "net_amount"),
        ("totals", "total_settlement"),
        ("totals", "balance"),
    ]

    for c in critical:
        fill(c)

    # Merge diagnoses with deduplication
    if not llm.get("diagnoses"):
        llm["diagnoses"] = []

    seen_diag = {(d.get("description", ""), d.get("icd10")) for d in llm["diagnoses"]}
    for d in pre.get("diagnoses", []):
        tup = (d.get("description", ""), d.get("icd10"))
        if tup not in seen_diag:
            llm["diagnoses"].append(d)

    # Merge line items with deduplication
    if not llm.get("line_items"):
        llm["line_items"] = []

    seen_li = {
        (li.get("code"), li.get("description"), li.get("qty"), li.get("line_total"))
        for li in llm["line_items"]
    }
    for li in pre.get("line_items", []):
        tup = (li.get("code"), li.get("description"), li.get("qty"), li.get("line_total"))
        if tup not in seen_li:
            llm["line_items"].append(li)

    return llm
