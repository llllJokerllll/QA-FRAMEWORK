"""
Pytest configuration and fixtures

This file configures pytest to work with the backend module structure.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Ensure the backend module can be imported
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

print(f"Backend directory: {backend_dir}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 paths