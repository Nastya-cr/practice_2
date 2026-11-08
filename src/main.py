"""Запуск анализатора зависимостей Cargo."""

import sys
import tomllib

from cargo import CargoError, get_direct_dependencies
from config import load_config, validate_config


def print_dependencies(package_name, version, dependencies):
    """Выводит прямые зависимости пакета."""
    print(f"Прямые зависимости {package_name} {version}:")

    if not dependencies:
        print("Зависимости не найдены")
        return

    for dependency in dependencies:
        details = dependency["kind"]

        if dependency["optional"]:
            details += ", optional"

        name = dependency["name"]
        requirement = dependency["requirement"]
        print(f"- {name} {requirement} ({details})")


def main():
    """Загружает настройки и получает зависимости.

    Returns:
        int: Код 0 при успехе или 1 при ошибке.
    """
    try:
        config = load_config("config.toml")
        validate_config(config)
        dependencies = get_direct_dependencies(
            config["package_name"],
            config["version"],
            config["repository"],
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
    except CargoError as error:
        print(f"Ошибка Cargo: {error}", file=sys.stderr)
        return 1

    print_dependencies(
        config["package_name"],
        config["version"],
        dependencies,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())