import sys
import tomllib

from config import load_config, validate_config


def main():
    """Загружает, проверяет и выводит настройки."""
    try:
        config = load_config("config.toml")
        validate_config(config)
    except OSError as error:
        print(f"Ошибка чтения файла: {error}", file=sys.stderr)
        return 1
    except tomllib.TOMLDecodeError as error:
        print(f"Ошибка TOML: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Ошибка настройки: {error}", file=sys.stderr)
        return 1

    for key in config:
        value = config[key]
        print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())