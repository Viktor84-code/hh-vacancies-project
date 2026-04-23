from src.utils.config import Config


def test_config_has_attributes():
    assert hasattr(Config, "DB_NAME")
    assert hasattr(Config, "DB_USER")
    assert hasattr(Config, "DB_PASSWORD")
    assert hasattr(Config, "DB_HOST")
    assert hasattr(Config, "DB_PORT")
