"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src directory to Python path for test imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock py5 for headless test environments (GitHub Actions)
# py5 requires a graphical environment, but tests only need the logic
sys.modules["py5"] = MagicMock()
