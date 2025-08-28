import os
import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

import uvicorn

def run_app():
    """Run the FastAPI application."""
    print("Starting FastAPI application...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    run_app()
