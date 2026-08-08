from typing import NamedTuple

from sqlalchemy import URL, make_url


class DBPreset(NamedTuple):
    label: str
    default_driver: str
    drivers: list[tuple[str, str]]
    default_username: str | None
    default_port: int | None
    is_sqlite: bool = False


PRESETS: dict[str, DBPreset] = {
    "1": DBPreset(
        label="PostgreSQL",
        default_driver="postgresql+asyncpg",
        drivers=[
            ("postgresql+asyncpg", "Async, recommended"),
            ("postgresql+psycopg", "psycopg v3"),
            ("postgresql+psycopg2", "psycopg v2"),
            ("postgresql+pg8000", "pure Python driver"),
            ("postgresql", "default driver"),
        ],
        default_username="postgres",
        default_port=5432,
    ),
    "2": DBPreset(
        label="SQLite",
        default_driver="sqlite+aiosqlite",
        drivers=[
            ("sqlite+aiosqlite", "Async, recommended"),
            ("sqlite", "Standard library"),
        ],
        default_username=None,
        default_port=None,
        is_sqlite=True,
    ),
    "3": DBPreset(
        label="MySQL / MariaDB",
        default_driver="mysql+pymysql",
        drivers=[
            ("mysql+pymysql", "PyMySQL, recommended"),
            ("mysql+asyncmy", "Async"),
            ("mysql+aiomysql", "Async"),
            ("mysql+mysqlconnector", "MySQL Connector"),
            ("mysql", "default driver"),
        ],
        default_username="root",
        default_port=3306,
    ),
    "4": DBPreset(
        label="Microsoft SQL Server",
        default_driver="mssql+pyodbc",
        drivers=[
            ("mssql+pyodbc", "pyodbc, recommended"),
            ("mssql+pymssql", "pymssql"),
            ("mssql", "default driver"),
        ],
        default_username="sa",
        default_port=1433,
    ),
    "5": DBPreset(
        label="Oracle",
        default_driver="oracle+oracledb",
        drivers=[
            ("oracle+oracledb", "oracledb, recommended"),
            ("oracle+cx_oracle", "cx_Oracle"),
            ("oracle", "default driver"),
        ],
        default_username="SYSTEM",
        default_port=1521,
    ),
}


def prompt(text: str, default: str | None = None) -> str:
    prompt_str = f"{text} [{default}]: " if default is not None else f"{text}: "
    val = input(prompt_str).strip()
    if not val and default is not None:
        return default
    return val


def select_db_preset() -> tuple[DBPreset | None, str]:
    print("=== SQLAlchemy URL Generator ===")
    print("\nSelect a database system:")
    for key, preset in PRESETS.items():
        print(f"  {key}) {preset.label}")
    print("  6) Other (Enter driver manually)")

    choice = prompt("\nYour choice", default="1")
    if choice in PRESETS:
        return PRESETS[choice], choice
    return None, choice


def select_driver(preset: DBPreset) -> str:
    print("\nSelect a driver:")
    for idx, (driver_name, desc) in enumerate(preset.drivers, start=1):
        default_mark = (
            " (default)" if driver_name == preset.default_driver else ""
        )
        print(f"  {idx}) {driver_name} - {desc}{default_mark}")
    print("  0) Enter custom driver")

    choice = prompt("Your choice", default="1")
    if choice == "1":
        return preset.default_driver
    if choice == "0":
        return prompt("Enter driver name (e.g. postgresql+asyncpg)")

    try:
        idx_val = int(choice) - 1
        if 0 <= idx_val < len(preset.drivers):
            return preset.drivers[idx_val][0]
    except ValueError:
        pass

    return choice if choice else preset.default_driver


def main() -> None:
    preset, choice_key = select_db_preset()

    if preset is None:
        if choice_key == "6":
            database_driver = prompt("Driver name (e.g. cockroachdb+asyncpg)")
        else:
            database_driver = choice_key

        is_sqlite = database_driver.startswith("sqlite")
        default_username: str | None = None if is_sqlite else "root"
        default_port: int | None = None
    else:
        database_driver = select_driver(preset)
        is_sqlite = preset.is_sqlite
        default_username = preset.default_username
        default_port = preset.default_port

    if is_sqlite:
        print("\nSQLite connection settings:")
        database = prompt("Database file path (or :memory:)", default="bookstore.db")
        username: str | None = None
        password: str | None = None
        host: str | None = None
        port: int | None = None
    else:
        print("\nConnection settings:")
        username_raw = prompt("Username", default=default_username)
        username = username_raw if username_raw else None

        password_raw = prompt("Password (leave empty if none)", default="")
        password = password_raw if password_raw else None

        host_raw = prompt("Host", default="localhost")
        host = host_raw if host_raw else None

        default_port_str = str(default_port) if default_port is not None else ""
        port_raw = prompt(
            "Port", default=default_port_str if default_port_str else None
        )
        port = int(port_raw) if port_raw.isdigit() else None

        database_raw = prompt("Database name", default="bookstore")
        database = database_raw if database_raw else None

    sqlalchemy_url = URL.create(
        drivername=database_driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    stringified_sqlalchemy_url = sqlalchemy_url.render_as_string(hide_password=False)

    # assert make_url round trip
    assert make_url(stringified_sqlalchemy_url) == sqlalchemy_url

    escaped_msg = (
        "The correctly escaped string that can be passed to SQLAlchemy make_url() and create_engine() is:\n\n"
        + f"     {stringified_sqlalchemy_url!r}\n"
    )
    print(escaped_msg)

    percent_replaced_url = stringified_sqlalchemy_url.replace("%", "%%")

    # assert percent-interpolated plus make_url round trip
    assert make_url(percent_replaced_url % {}) == sqlalchemy_url

    config_msg = (
        "The SQLAlchemy URL that can be placed in a ConfigParser file such as alembic.ini is:\n\n"
        + f"      sqlalchemy.url = {percent_replaced_url}\n"
    )
    print(config_msg)


if __name__ == "__main__":
    main()
