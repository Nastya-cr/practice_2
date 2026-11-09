"""Запуск анализатора зависимостей Cargo."""

import sys
import tomllib

from cargo import CargoError, CargoRepository
from config import load_config, validate_config
from graph import (
    GraphError,
    TestRepository,
    build_dependency_graph,
    find_reverse_dependencies,
)
from visualization import (
    VisualizationError,
    save_png,
    to_ascii_tree,
    to_mermaid,
)


def _config_path(arguments):
    """Возвращает путь к конфигурации."""
    if arguments:
        return arguments[0]

    return "config.toml"


def _create_repository(config):
    """Создаёт настоящий или тестовый репозиторий."""
    if config["test_mode"]:
        repository = TestRepository.load(
            config["repository"],
        )
        return repository, ""

    repository = CargoRepository(
        config["repository"],
    )
    return repository, config["version"]


def _root_name(package_name, version):
    """Создаёт имя корневого узла."""
    if version:
        return f"{package_name}@{version}"

    return package_name


def _process(config):
    """Строит граф и создаёт результаты работы."""
    repository, version = _create_repository(config)
    graph = build_dependency_graph(
        config["package_name"],
        version,
        repository,
        config["max_depth"],
        config["filter_substring"],
    )
    reverse_dependencies = None

    if config["reverse_mode"]:
        reverse_dependencies = find_reverse_dependencies(
            graph,
            config["reverse_package"],
        )

    mermaid = to_mermaid(graph)
    ascii_tree = None

    if config["ascii_tree"]:
        root = _root_name(
            config["package_name"],
            version,
        )
        ascii_tree = to_ascii_tree(graph, root)

    return (
        graph,
        reverse_dependencies,
        mermaid,
        ascii_tree,
    )


def print_graph(graph):
    """Выводит граф зависимостей."""
    print("Граф зависимостей:")

    for package in sorted(graph):
        dependencies = graph[package]
        text = ", ".join(dependencies) if dependencies else "-"
        print(f"{package} -> {text}")


def print_reverse_dependencies(
    package_name,
    dependencies,
):
    """Выводит обратные зависимости."""
    print()
    print(f"Обратные зависимости {package_name}:")

    if not dependencies:
        print("Обратных зависимостей нет")
        return

    for dependency in dependencies:
        print(f"- {dependency}")


def print_visualizations(mermaid, ascii_tree):
    """Выводит Mermaid и ASCII-дерево."""
    print()
    print("Mermaid:")
    print(mermaid)

    if ascii_tree is not None:
        print()
        print("ASCII-дерево:")
        print(ascii_tree)


def _print_result(config, result):
    """Выводит все результаты работы."""
    graph, reverse, mermaid, ascii_tree = result
    print_graph(graph)

    if reverse is not None:
        print_reverse_dependencies(
            config["reverse_package"],
            reverse,
        )

    print_visualizations(mermaid, ascii_tree)


def main(argv=None):
    """Запускает анализатор зависимостей."""
    arguments = sys.argv[1:] if argv is None else argv
    path = _config_path(arguments)

    try:
        config = load_config(path)
        validate_config(config)
        result = _process(config)
    except (
        OSError,
        tomllib.TOMLDecodeError,
        ValueError,
        CargoError,
        GraphError,
        VisualizationError,
    ) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    _print_result(config, result)
    png_path = "graph.png"
    try:
        save_png(result[0], png_path)
    except (OSError, VisualizationError) as error:
        print(f"PNG не сохранён: {error}", file=sys.stderr)
    else:
        print(f"\nPNG сохранён: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
