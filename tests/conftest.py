"""Pytest configuration and fixtures."""

import sys

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_gtk():
    """Initialize GTK for tests (requires DISPLAY)."""
    # Skip GTK tests if no display available
    import os
    if not os.environ.get("DISPLAY") and sys.platform != "win32":
        pytest.skip("No DISPLAY available for GTK tests")


@pytest.fixture
def mock_gtk(monkeypatch):
    """Mock GTK imports for unit tests that don't need display."""
    # GTK imports are allowed to fail in test environment
    pass  # Use real GTK with mock display where available