"""Тесты построения графа зависимостей."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from graph import build_dependency_graph


class FakeRepository:
    """Простой тестовый источник зависимостей."""

    def __init__(self, data):
        """Сохраняет тестовые данные."""
        self.data = data

    def get_dependencies(self, package_name, version):
        """Возвращает зависимости пакета."""
        return [
            {
                "name": name,
                "version": "",
            }
            for name in self.data.get(package_name, [])
        ]


class GraphTest(unittest.TestCase):
    """Проверяет DFS, глубину, фильтр и циклы."""

    def test_cycle(self):
        """Проверяет обработку циклического графа."""
        repository = FakeRepository(
            {
                "A": ["B"],
                "B": ["C"],
                "C": ["A"],
            }
        )

        graph = build_dependency_graph(
            "A",
            "",
            repository,
            5,
            "",
        )

        self.assertEqual(graph["C"], ["A"])

    def test_max_depth(self):
        """Проверяет максимальную глубину."""
        repository = FakeRepository(
            {
                "A": ["B"],
                "B": ["C"],
                "C": [],
            }
        )

        graph = build_dependency_graph(
            "A",
            "",
            repository,
            1,
            "",
        )

        self.assertEqual(
            graph,
            {
                "A": ["B"],
                "B": [],
            },
        )

    def test_filter(self):
        """Проверяет фильтрацию пакетов."""
        repository = FakeRepository(
            {
                "A": ["B", "C"],
                "B": [],
                "C": [],
            }
        )

        graph = build_dependency_graph(
            "A",
            "",
            repository,
            3,
            "C",
        )

        self.assertEqual(graph["A"], ["B"])


if __name__ == "__main__":
    unittest.main()