"""
Settings and preferences management for Modern EBook Reader
"""

import json
from pathlib import Path
from typing import List

# Settings file location
SETTINGS_DIR = Path.home() / ".ebook_reader"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

def ensure_settings_dir():
    """Ensure settings directory exists."""
    SETTINGS_DIR.mkdir(exist_ok=True)

def load_settings() -> dict:
    """Load settings from file."""
    ensure_settings_dir()
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Return default settings
    return {
        "recent_books": [],
        "window_geometry": None,
        "zoom_level": 1.0,
        "theme": "light"
    }

def save_settings(settings: dict):
    """Save settings to file."""
    ensure_settings_dir()
    
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except IOError:
        pass  # Fail silently

def load_recent_books() -> List[str]:
    """Load recent books list."""
    settings = load_settings()
    return settings.get("recent_books", [])

def add_recent_book(file_path: str):
    """Add a book to the recent books list."""
    settings = load_settings()
    recent_books = settings.get("recent_books", [])
    
    # Remove if already exists
    if file_path in recent_books:
        recent_books.remove(file_path)
    
    # Add to beginning
    recent_books.insert(0, file_path)
    
    # Keep only last 20 books
    recent_books = recent_books[:20]
    
    settings["recent_books"] = recent_books
    save_settings(settings)

def clear_recent_books():
    """Clear all recent books."""
    settings = load_settings()
    settings["recent_books"] = []
    save_settings(settings)

def get_setting(key: str, default=None):
    """Get a specific setting value."""
    settings = load_settings()
    return settings.get(key, default)

def set_setting(key: str, value):
    """Set a specific setting value."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)