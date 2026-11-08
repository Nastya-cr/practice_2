"""Запуск анализатора зависимостей Cargo."""

import sys
import tomllib

from cargo import CargoError, CargoRepository
from config import load_config, validate_config
from graph import (
    GraphError,
    TestRepository,
    build_dependency_graph,
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


def print_graph(graph):
    """Выводит граф зависимостей."""
    for package in sorted(graph):
        dependencies = graph[package]

        if dependencies:
            text = ", ".join(dependencies)
        else:
            text = "-"

        print(f"{package} -> {text}")


def main(argv=None):
    """Загружает настройки и строит граф зависимостей."""
    arguments = sys.argv[1:] if argv is None else argv
    path = _config_path(arguments)

    try:
        config = load_config(path)
        validate_config(config)
        repository, version = _create_repository(config)
        graph = build_dependency_graph(
            config["package_name"],
            version,
            repository,
            config["max_depth"],
            config["filter_substring"],
        )
    except OSError as error:
        print(f"Ошибка чтения файла: {error}", file=sys.stderr)
        return 1
    except tomllib.TOMLDecodeError as error:
        print(f"Ошибка TOML: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Ошибка настройки: {error}", file=sys.stderr)
        return 1
    except (CargoError, GraphError) as error:
        print(f"Ошибка графа: {error}", file=sys.stderr)
        return 1

    print_graph(graph)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())