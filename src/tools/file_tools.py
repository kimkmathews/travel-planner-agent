import os
from langchain_core.tools import tool

@tool
def save_text_file(filepath: str, content: str) -> str:
    """Saves text content to a physical file on disk."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully saved to {filepath}"
    except Exception as e:
        return f"Failed to save file: {e}"

@tool
def read_text_file(filepath: str) -> str:
    """Reads text content from a physical file on disk."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file: {e}"

@tool
def list_directory_files(directory: str) -> str:
    """Lists files in a physical directory on disk."""
    try:
        if not os.path.exists(directory):
            return f"Directory {directory} does not exist."
        files = os.listdir(directory)
        return f"Files in {directory}: {', '.join(files)}"
    except Exception as e:
        return f"Failed to list directory: {e}"