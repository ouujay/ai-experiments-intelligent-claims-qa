"""
Test script for Intelligent Claims QA Service
Tests both /extract and /ask endpoints
"""
import requests
import json
import sys
from pathlib import Path


BASE_URL = "http://localhost:8001"


def test_health_check():
    """Test the root endpoint"""
    print("=" * 60)
    print("Testing health check endpoint...")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_extract(file_path: str):
    """Test the /extract endpoint"""
    print("\n" + "=" * 60)
    print(f"Testing /extract endpoint with: {file_path}")
    print("=" * 60)

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return None

    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            response = requests.post(f"{BASE_URL}/extract", files=files)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nDocument ID: {data['document_id']}")
            print(f"\nExtracted Data:")
            print(json.dumps(data['data'], indent=2))
            return data['document_id']
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def test_ask(document_id: str, question: str):
    """Test the /ask endpoint"""
    print("\n" + "=" * 60)
    print(f"Testing /ask endpoint...")
    print("=" * 60)
    print(f"Document ID: {document_id}")
    print(f"Question: {question}")

    try:
        payload = {
            "document_id": document_id,
            "question": question
        }

        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nAnswer: {data['answer']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_list_documents():
    """Test the /documents endpoint"""
    print("\n" + "=" * 60)
    print("Listing all documents...")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/documents")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nDocuments in storage:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main test flow"""
    print("\n" + "=" * 60)
    print("INTELLIGENT CLAIMS QA SERVICE - TEST SCRIPT")
    print("=" * 60)

    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running!")
        print("Please start the server with: python run.py")
        sys.exit(1)

    print("\n✅ Server is running!")

    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Try to use sample files if available
        project_root = Path(__file__).parent.parent
        sample_dir = project_root / "samples"

        print("\nUsage: python tests/test_service.py <path_to_claim_document>")
        print("\nNo file provided. Please provide a claim document to test.")

        if sample_dir.exists():
            sample_files = list(sample_dir.glob("*.pdf"))
            if sample_files:
                print(f"\nAvailable sample files in samples/ directory:")
                for f in sample_files:
                    print(f"  - {f.name}")
                print(f"\nExample: python tests/test_service.py samples/{sample_files[0].name}")
        else:
            print("Example: python tests/test_service.py path/to/claim_document.pdf")

        sys.exit(1)

    # Test extraction
    doc_id = test_extract(file_path)

    if not doc_id:
        print("\n❌ Extraction failed!")
        sys.exit(1)

    print("\n✅ Extraction successful!")

    # Test question answering
    questions = [
        "How many tablets of paracetamol were prescribed?",
        "What is the patient's name?",
        "What was the total amount?",
        "What medications were prescribed?"
    ]

    print("\n" + "=" * 60)
    print("Testing multiple questions...")
    print("=" * 60)

    for question in questions:
        test_ask(doc_id, question)

    # List all documents
    test_list_documents()

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
