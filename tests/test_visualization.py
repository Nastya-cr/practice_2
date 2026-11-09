"""Тесты визуализации графа."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from visualization import to_ascii_tree, to_mermaid


class VisualizationTest(unittest.TestCase):
    """Проверяет Mermaid и ASCII-дерево."""

    @staticmethod
    def make_graph():
        """Создаёт тестовый граф."""
        return {
            "A": ["B", "C"],
            "B": ["A"],
            "C": [],
        }

    def test_mermaid(self):
        """Проверяет создание Mermaid-диаграммы."""
        result = to_mermaid(self.make_graph())

        self.assertIn("graph TD", result)
        self.assertIn('["A"]', result)
        self.assertIn("-->", result)

    def test_ascii_tree(self):
        """Проверяет создание ASCII-дерева."""
        result = to_ascii_tree(self.make_graph(), "A")

        self.assertIn("├── B", result)
        self.assertIn("└── C", result)
        self.assertIn("(цикл)", result)


if __name__ == "__main__":
    unittest.main()
