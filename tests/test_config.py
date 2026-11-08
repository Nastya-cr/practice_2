"""Тесты загрузки и проверки конфигурации."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from config import load_config, validate_config


PROJECT = Path(__file__).parents[1]


class ConfigTest(unittest.TestCase):
    """Проверяет настройки программы."""

    def setUp(self):
        """Создаёт правильные настройки перед каждым тестом."""
        self.config = {
            "package_name": "serde",
            "repository": "https://index.crates.io/",
            "test_mode": False,
            "version": "1.0.0",
            "ascii_tree": True,
            "max_depth": 3,
            "filter_substring": "",
        }

    def test_load_config(self):
        """Проверяет чтение настоящего TOML-файла."""
        config = load_config(PROJECT / "config.toml")
        validate_config(config)
        self.assertIn("package_name", config)

    def test_valid_config(self):
        """Проверяет правильные настройки."""
        result = validate_config(self.config)
        self.assertIsNone(result)

    def test_invalid_values(self):
        """Проверяет неправильное значение каждого параметра."""
        invalid_values = {
            "package_name": "",
            "repository": "",
            "test_mode": "false",
            "version": "",
            "ascii_tree": "true",
            "max_depth": 0,
            "filter_substring": None,
        }

        for name in invalid_values:
            with self.subTest(name=name):
                config = self.config.copy()
                config[name] = invalid_values[name]

                with self.assertRaises(ValueError):
                    validate_config(config)

    def test_invalid_repository_url(self):
        """Проверяет неправильный URL репозитория."""
        self.config["repository"] = "not-a-url"

        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_missing_test_repository(self):
        """Проверяет отсутствие тестового репозитория."""
        self.config["test_mode"] = True
        self.config["repository"] = "missing.txt"

        with self.assertRaises(ValueError):
            validate_config(self.config)


if __name__ == "__main__":
    unittest.main()