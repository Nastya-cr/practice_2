"""Получение прямых зависимостей пакетов Cargo."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ONE_LETTER = 1
TWO_LETTERS = 2
THREE_LETTERS = 3
HTTP_NOT_FOUND = 404
REQUEST_TIMEOUT = 10


class CargoError(Exception):
    """Ошибка получения данных из Cargo-репозитория."""


def _index_path(package_name):
    """Создаёт путь пакета внутри Cargo-индекса.

    Args:
        package_name: Название Rust-пакета.

    Returns:
        str: Путь к данным пакета.
    """
    name = package_name.lower()
    length = len(name)

    if length == ONE_LETTER:
        return f"1/{name}"
    if length == TWO_LETTERS:
        return f"2/{name}"
    if length == THREE_LETTERS:
        return f"3/{name[0]}/{name}"

    return f"{name[:2]}/{name[2:4]}/{name}"


def _build_url(repository, package_name):
    """Создаёт полный URL для получения данных пакета."""
    repository = repository.removeprefix("sparse+")
    repository = repository.rstrip("/")
    return f"{repository}/{_index_path(package_name)}"


def _download_index(url):
    """Загружает сведения о версиях пакета."""
    request = Request(
        url,
        headers={"User-Agent": "dependency-visualizer"},
    )

    try:
        with urlopen(
            request,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            return response.read().decode("utf-8")
    except HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise CargoError("пакет не найден") from error
        message = f"ошибка репозитория: HTTP {error.code}"
        raise CargoError(message) from error
    except (URLError, OSError, UnicodeError) as error:
        message = f"не удалось получить данные: {error}"
        raise CargoError(message) from error


def _parse_versions(text):
    """Преобразует строки Cargo-индекса в список версий."""
    versions = []

    for line in text.splitlines():
        if not line.strip():
            continue

        try:
            versions.append(json.loads(line))
        except json.JSONDecodeError as error:
            message = "репозиторий вернул неправильный JSON"
            raise CargoError(message) from error

    return versions


def _find_version(versions, required_version):
    """Находит сведения о нужной версии пакета."""
    for version in versions:
        if version.get("vers") == required_version:
            return version

    message = f"версия {required_version} не найдена"
    raise CargoError(message)


def get_direct_dependencies(
    package_name,
    version,
    repository,
):
    """Получает прямые зависимости указанной версии пакета.

    Args:
        package_name: Название Rust-пакета.
        version: Версия пакета.
        repository: Адрес Cargo-индекса.

    Returns:
        list: Прямые зависимости пакета.

    Raises:
        CargoError: Если получить данные невозможно.
    """
    url = _build_url(repository, package_name)
    text = _download_index(url)
    versions = _parse_versions(text)
    package = _find_version(versions, version)
    dependencies = []

    for dependency in package.get("deps", []):
        dependencies.append(
            {
                "name": (
                    dependency.get("package")
                    or dependency.get("name")
                ),
                "requirement": dependency.get("req", ""),
                "kind": dependency.get("kind") or "normal",
                "optional": dependency.get("optional", False),
            }
        )

    return sorted(
        dependencies,
        key=lambda item: (item["name"], item["kind"]),
    )