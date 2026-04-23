import pytest
from main import main


def test_main_import():
    """Тест: main.py импортируется без ошибок."""
    from main import main
    assert main is not None
