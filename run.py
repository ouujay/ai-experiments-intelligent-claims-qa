"""
Main entry point for the Intelligent Claims QA Service
Run this script to start the FastAPI application
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
