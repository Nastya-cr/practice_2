"""Загрузка и проверка настроек программы."""

import tomllib
from pathlib import Path


MIN_DEPTH = 1


def load_config(path):
    """Читает настройки из TOML-файла.

    Args:
        path: Путь к файлу с настройками.

    Returns:
        dict: Настройки программы.
    """
    with open(path, "rb") as file:
        return tomllib.load(file)


def _get_text(config, name, allow_empty=False):
    """Получает и проверяет текстовую настройку."""
    value = config.get(name)

    if not isinstance(value, str):
        raise ValueError(f"{name} должен быть текстом")

    if not allow_empty and not value.strip():
        raise ValueError(f"{name} не должен быть пустым")

    return value


def _get_bool(config, name):
    """Получает и проверяет логическую настройку."""
    value = config.get(name)

    if not isinstance(value, bool):
        raise ValueError(f"{name} должен быть true или false")

    return value


def _get_depth(config):
    """Получает и проверяет максимальную глубину."""
    value = config.get("max_depth")

    if type(value) is not int:
        raise ValueError("max_depth должен быть целым числом")

    if value < MIN_DEPTH:
        raise ValueError("max_depth должен быть положительным")

    return value


def _validate_repository(repository, test_mode):
    """Проверяет адрес или путь тестового репозитория."""
    if test_mode:
        if not Path(repository).is_file():
            raise ValueError("файл тестового репозитория не найден")
        return

    if not repository.startswith(("http://", "https://")):
        raise ValueError("repository должен содержать URL-адрес")


def validate_config(config):
    """Проверяет все настройки программы."""
    _get_text(config, "package_name")
    test_mode = _get_bool(config, "test_mode")
    repository = _get_text(config, "repository")
    _validate_repository(repository, test_mode)
    _get_text(config, "version")
    _get_bool(config, "ascii_tree")
    _get_depth(config)
    _get_text(config, "filter_substring", allow_empty=True)