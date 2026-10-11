"""Unit tests for the Settings configuration class."""
from src.config.settings import Settings


class TestSettings:
    """Test suite for application settings."""

    def setup_method(self) -> None:
        self.settings = Settings()

    def test_database_url_contains_postgresql(self):
        assert "postgresql://" in self.settings.database_url

    def test_mlflow_uri_starts_with_http(self):
        assert self.settings.mlflow_tracking_uri.startswith("http://")

    def test_api_host_defaults_to_localhost_not_zero(self):
        """Per Bandit B104 fix — should bind to 127.0.0.1, not 0.0.0.0."""
        assert self.settings.api_host == "127.0.0.1"

    def test_api_port_defaults_to_8000(self):
        assert self.settings.api_port == 8000

    def test_environment_defaults_to_development(self):
        assert self.settings.environment == "development"

    def test_database_url_is_string(self):
        assert isinstance(self.settings.database_url, str)

    def test_api_port_is_integer(self):
        assert isinstance(self.settings.api_port, int)
