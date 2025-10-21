"""
Batch test script - Tests all sample documents
Runs extraction on all files in the samples/ directory
"""
import requests
import json
from pathlib import Path
import sys


BASE_URL = "http://localhost:8001"
PROJECT_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = PROJECT_ROOT / "samples"


def test_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except:
        return False


def extract_document(file_path: Path):
    """Extract data from a document"""
    print(f"\n{'='*70}")
    print(f"Testing: {file_path.name}")
    print(f"{'='*70}")

    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(f"{BASE_URL}/extract", files=files)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Document ID: {data['document_id']}")
            print(f"\nExtracted Data Summary:")
            print(f"  - Patient: {data['data'].get('patient', {}).get('name', 'N/A')}")
            print(f"  - Diagnoses: {len(data['data'].get('diagnoses', []))}")
            print(f"  - Medications: {len(data['data'].get('medications', []))}")
            print(f"  - Procedures: {len(data['data'].get('procedures', []))}")
            print(f"  - Total Amount: {data['data'].get('total_amount', 'N/A')}")

            return data['document_id']
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def main():
    """Main batch test flow"""
    print("\n" + "="*70)
    print("BATCH TEST - All Sample Documents")
    print("="*70)

    # Check server
    if not test_health():
        print("\n❌ Server is not running!")
        print("Please start the server with: python run.py")
        sys.exit(1)

    print("✅ Server is running!")

    # Find all sample files
    if not SAMPLES_DIR.exists():
        print(f"\n❌ Samples directory not found: {SAMPLES_DIR}")
        sys.exit(1)

    sample_files = list(SAMPLES_DIR.glob("*.pdf")) + \
                   list(SAMPLES_DIR.glob("*.png")) + \
                   list(SAMPLES_DIR.glob("*.jpg"))

    # Filter out README
    sample_files = [f for f in sample_files if f.name != "README.md"]

    if not sample_files:
        print(f"\n❌ No sample files found in {SAMPLES_DIR}")
        sys.exit(1)

    print(f"\nFound {len(sample_files)} sample file(s) to test\n")

    # Test each file
    results = {}
    for file_path in sample_files:
        doc_id = extract_document(file_path)
        results[file_path.name] = {
            "success": doc_id is not None,
            "document_id": doc_id
        }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    successful = sum(1 for r in results.values() if r["success"])
    failed = len(results) - successful

    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")

    print("\nDetails:")
    for filename, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {filename}")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
