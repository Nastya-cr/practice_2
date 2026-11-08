"""Тесты получения зависимостей Cargo."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cargo import CargoError, get_direct_dependencies


INDEX_DATA = (
    '{"name":"demo","vers":"1.0.0","deps":['
    '{"name":"first","req":"^1.0",'
    '"kind":"normal","optional":false},'
    '{"name":"second","req":"^2.0",'
    '"kind":"dev","optional":true}]}'
)


class CargoTest(unittest.TestCase):
    """Проверяет обработку данных Cargo."""

    @patch("cargo._download_index", return_value=INDEX_DATA)
    def test_direct_dependencies(self, download):
        """Проверяет получение прямых зависимостей."""
        dependencies = get_direct_dependencies(
            "demo",
            "1.0.0",
            "https://example.com",
        )

        self.assertEqual(len(dependencies), 2)
        self.assertEqual(dependencies[0]["name"], "first")
        download.assert_called_once()

    @patch("cargo._download_index", return_value=INDEX_DATA)
    def test_missing_version(self, download):
        """Проверяет отсутствие нужной версии."""
        with self.assertRaises(CargoError):
            get_direct_dependencies(
                "demo",
                "2.0.0",
                "https://example.com",
            )

        download.assert_called_once()


if __name__ == "__main__":
    unittest.main()