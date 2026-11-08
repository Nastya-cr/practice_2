"""Построение графа зависимостей через DFS."""

import json
from pathlib import Path


ROOT_DEPTH = 0
NEXT_DEPTH = 1


class GraphError(Exception):
    """Ошибка построения графа зависимостей."""


def _valid_test_name(name):
    """Проверяет имя пакета тестового репозитория."""
    return (
        isinstance(name, str)
        and name.isascii()
        and name.isalpha()
        and name.isupper()
    )


def _validate_test_data(data):
    """Проверяет тестовый граф."""
    if not isinstance(data, dict):
        raise GraphError("тестовый репозиторий должен быть объектом")

    for package, dependencies in data.items():
        if not _valid_test_name(package):
            raise GraphError("имена пакетов должны быть большими буквами")

        if not isinstance(dependencies, list):
            raise GraphError("зависимости должны быть списком")

        for dependency in dependencies:
            if not _valid_test_name(dependency):
                message = "имена зависимостей должны быть большими буквами"
                raise GraphError(message)


class TestRepository:
    """Предоставляет зависимости из тестового JSON-файла."""

    def __init__(self, data):
        """Сохраняет тестовый граф."""
        self.data = data

    @classmethod
    def load(cls, path):
        """Загружает тестовый репозиторий."""
        try:
            text = Path(path).read_text(encoding="utf-8")
            data = json.loads(text)
        except json.JSONDecodeError as error:
            message = "неправильный JSON тестового репозитория"
            raise GraphError(message) from error

        _validate_test_data(data)
        return cls(data)

    def get_dependencies(self, package_name, version):
        """Возвращает зависимости тестового пакета."""
        names = self.data.get(package_name, [])

        return [
            {
                "name": name,
                "version": "",
            }
            for name in names
        ]


def _node_name(package_name, version):
    """Создаёт имя узла графа."""
    if version:
        return f"{package_name}@{version}"

    return package_name


def build_dependency_graph(
    package_name,
    version,
    repository,
    max_depth,
    filter_substring,
):
    """Строит граф алгоритмом DFS без рекурсии."""
    graph = {}
    visited = set()
    filter_value = filter_substring.lower()
    stack = [
        (
            package_name,
            version,
            ROOT_DEPTH,
        )
    ]

    while stack:
        name, current_version, depth = stack.pop()
        node = _node_name(name, current_version)

        if node in visited:
            continue

        visited.add(node)
        graph.setdefault(node, [])

        if depth >= max_depth:
            continue

        dependencies = repository.get_dependencies(
            name,
            current_version,
        )

        for dependency in reversed(dependencies):
            child_name = dependency["name"]

            if (
                filter_value
                and filter_value in child_name.lower()
            ):
                continue

            child_version = dependency["version"]
            child = _node_name(
                child_name,
                child_version,
            )
            graph[node].append(child)
            graph.setdefault(child, [])

            if child not in visited:
                stack.append(
                    (
                        child_name,
                        child_version,
                        depth + NEXT_DEPTH,
                    )
                )

    return graph