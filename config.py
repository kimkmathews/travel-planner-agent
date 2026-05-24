# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration (using local Ollama)
LLM_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
LLM_BASE_URL = "http://localhost:11434"  # Default Ollama port

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "google_genai:gemma-4-31b")
# Paths
DATA_DIR = "data"
ITINERARIES_DIR = os.path.join(DATA_DIR, "itineraries")
TEMP_DIR = os.path.join(DATA_DIR, "temp")

# Vector DB settings
CHROMA_COLLECTION_NAME = "travel_data"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free sentence-transformers model

# Ensure directories exist
os.makedirs(ITINERARIES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)