"""Выбор версии по требованиям Cargo."""

import operator
import re


ZERO = 0
ONE = 1
MAJOR = 0
MINOR = 1
PATCH = 2
ONE_PART = 1
TWO_PARTS = 2

VERSION_PATTERN = re.compile(
    r"^(\d+|\*)(?:\.(\d+|\*))?(?:\.(\d+|\*))?$"
)

COMPARISONS = (
    (">=", operator.ge),
    ("<=", operator.le),
    (">", operator.gt),
    ("<", operator.lt),
    ("=", operator.eq),
)


def _base_version(text):
    """Преобразует версию в три числа."""
    match = VERSION_PATTERN.fullmatch(text.strip())

    if not match:
        return None, ZERO

    values = []
    count = ZERO

    for part in match.groups():
        if part is None or part == "*":
            values.append(ZERO)
        else:
            values.append(int(part))
            count += ONE

    return tuple(values), count


def _parse_version(version):
    """Преобразует настоящую версию пакета в числа."""
    core = version.split("+", ONE)[ZERO]
    core = core.split("-", ONE)[ZERO]

    if "*" in core:
        return None

    parsed, count = _base_version(core)

    if count == ZERO:
        return None

    return parsed


def _match_comparison(version, clause):
    """Проверяет операторы сравнения версий."""
    for symbol, operation in COMPARISONS:
        if clause.startswith(symbol):
            text = clause[len(symbol):].strip()
            base, count = _base_version(text)

            if count == ZERO:
                return False

            return operation(version, base)

    return None


def _match_caret(version, text):
    """Проверяет требование с оператором каретки."""
    base, count = _base_version(text)

    if count == ZERO:
        return False

    if base[MAJOR] > ZERO:
        upper = (base[MAJOR] + ONE, ZERO, ZERO)
    elif count == ONE_PART:
        upper = (ONE, ZERO, ZERO)
    elif base[MINOR] > ZERO:
        upper = (ZERO, base[MINOR] + ONE, ZERO)
    elif count == TWO_PARTS:
        upper = (ZERO, ONE, ZERO)
    else:
        upper = (ZERO, ZERO, base[PATCH] + ONE)

    return base <= version < upper


def _match_tilde(version, text):
    """Проверяет требование с оператором тильды."""
    base, count = _base_version(text)

    if count == ZERO:
        return False

    if count == ONE_PART:
        upper = (base[MAJOR] + ONE, ZERO, ZERO)
    else:
        upper = (
            base[MAJOR],
            base[MINOR] + ONE,
            ZERO,
        )

    return base <= version < upper


def _match_wildcard(version, text):
    """Проверяет требование со звёздочкой."""
    base, count = _base_version(text)

    if count == ZERO:
        return True

    return version[:count] == base[:count]


def _match_clause(version, clause):
    """Проверяет одну часть требования Cargo."""
    clause = clause.strip().replace("x", "*")
    clause = clause.replace("X", "*")

    if not clause or clause == "*":
        return True

    comparison = _match_comparison(version, clause)

    if comparison is not None:
        return comparison

    if "*" in clause:
        return _match_wildcard(version, clause)

    if clause.startswith("^"):
        return _match_caret(version, clause[ONE:])

    if clause.startswith("~"):
        return _match_tilde(version, clause[ONE:])

    return _match_caret(version, clause)


def _matches_requirement(version, requirement):
    """Проверяет полное требование версии."""
    clauses = requirement.split(",")

    return all(
        _match_clause(version, clause)
        for clause in clauses
    )


def select_version(versions, requirement):
    """Выбирает новейшую подходящую версию."""
    matches = []

    for item in versions:
        raw_version = item.get("vers", "")
        parsed = _parse_version(raw_version)

        if parsed is None or item.get("yanked"):
            continue

        if "-" in raw_version and "-" not in requirement:
            continue

        if _matches_requirement(parsed, requirement):
            matches.append((parsed, raw_version))

    if not matches:
        return None

    return max(matches)[ONE]