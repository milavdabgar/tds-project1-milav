from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# API Configuration
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is not set")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Data Directory Configuration
DATA_DIR = os.getenv("DATA_DIR", "/data")
REAL_DATA_DIR = os.path.join(os.getcwd(), "data")

# API Endpoints
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "http://aiproxy.sanand.workers.dev/openai/v1")
OPENAI_CHAT_URL = f"{OPENAI_API_BASE_URL}/chat/completions"
OPENAI_EMBEDDINGS_URL = f"{OPENAI_API_BASE_URL}/embeddings"

# Create data directory if it doesn't exist
Path(REAL_DATA_DIR).mkdir(parents=True, exist_ok=True)

def get_real_path(virtual_path: str) -> str:
    """Convert a virtual path starting with /data to a real filesystem path."""
    if not virtual_path.startswith(DATA_DIR):
        raise ValueError(f"Path must start with {DATA_DIR}")
    
    relative_path = virtual_path[len(DATA_DIR):].lstrip('/')
    return os.path.join(REAL_DATA_DIR, relative_path)

def ensure_data_path(path: str) -> None:
    """Ensure that a path is within the data directory."""
    if not path.startswith(DATA_DIR):
        raise ValueError(f"Access denied. Can only access files under {DATA_DIR}")
