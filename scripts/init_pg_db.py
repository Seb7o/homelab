#!/usr/bin/env python3
from __future__ import annotations

import argparse
import curses
import re
import shlex
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def fail(message: str, code: int = 1) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(code)


def info(message: str) -> None:
    print(f"[INFO] {message}")


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        fail(f"Env file not found: {path}")

    env: dict[str, str] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export "):].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if len(value) >= 2 and (
            (value[0] == value[-1] == '"') or
            (value[0] == value[-1] == "'")
        ):
            value = value[1:-1]

        env[key] = value

    return env


def load_config(path: Path) -> dict:
    if not path.exists():
        fail(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "ssh" not in data:
        fail("Missing 'ssh' section in config.yml")

    ssh_cfg = data["ssh"]
    if not ssh_cfg.get("host"):
        fail("config.yml: ssh.host is required")
    if not ssh_cfg.get("user"):
        fail("config.yml: ssh.user is required")

    return data


def validate_identifier(name: str, label: str) -> None:
    if not IDENTIFIER_RE.match(name):
        fail(
            f"{label} '{name}' is not a safe PostgreSQL identifier. "
            "Use only letters, digits, and underscores, and do not start with a digit."
        )


def build_role_sql(db_user: str, db_password: str) -> str:
    db_user_sql = db_user.replace("'", "''")
    db_password_sql = db_password.replace("'", "''")

    return f"""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{db_user_sql}'
    ) THEN
        EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '{db_user_sql}', '{db_password_sql}');
    ELSE
        EXECUTE format('ALTER ROLE %I LOGIN PASSWORD %L', '{db_user_sql}', '{db_password_sql}');
    END IF;
END
$$;
""".strip()


def init_curses(stdscr) -> None:
    curses.curs_set(0)
    try:
        curses.use_default_colors()
    except curses.error:
        pass


def run_menu(stdscr, title: str, options: list[str]) -> str:
    init_curses(stdscr)
    idx = 0
    scroll = 0

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(0, 0, title[: width - 1], curses.A_BOLD)
        stdscr.addstr(1, 0, "Use ↑ ↓ and Enter", curses.A_DIM)

        visible_height = max(1, height - 4)

        if idx < scroll:
            scroll = idx
        elif idx >= scroll + visible_height:
            scroll = idx - visible_height + 1

        visible_options = options[scroll: scroll + visible_height]

        for line_no, option in enumerate(visible_options, start=3):
            actual_index = scroll + (line_no - 3)
            prefix = "➜ " if actual_index == idx else "  "
            text = f"{prefix}{option}"
            if actual_index == idx:
                stdscr.addstr(line_no, 0, text[: width - 1], curses.A_REVERSE)
            else:
                stdscr.addstr(line_no, 0, text[: width - 1])

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            return options[idx]


def run_confirm(stdscr, lines: list[str]) -> bool:
    init_curses(stdscr)
    choices = ["Yes", "No"]
    idx = 0

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(0, 0, "Confirm", curses.A_BOLD)

        y = 2
        for line in lines:
            if y < height:
                stdscr.addstr(y, 0, line[: width - 1])
                y += 1

        y += 1
        if y < height:
            stdscr.addstr(y, 0, "Use ← → and Enter", curses.A_DIM)
            y += 2

        x = 0
        for i, choice in enumerate(choices):
            text = f"[ {choice} ]"
            if y < height:
                if i == idx:
                    stdscr.addstr(y, x, text, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, text)
            x += len(text) + 2

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_LEFT, ord("h")):
            idx = (idx - 1) % len(choices)
        elif key in (curses.KEY_RIGHT, ord("l")):
            idx = (idx + 1) % len(choices)
        elif key in (10, 13, curses.KEY_ENTER):
            return choices[idx] == "Yes"


def interactive_mapping(env_vars: dict[str, str]) -> tuple[str, str, str]:
    keys = sorted(env_vars.keys())
    if not keys:
        fail("No variables found in .env file")

    def wrapped(stdscr):
        db_name_var = run_menu(stdscr, "Select variable for db_name", keys)
        db_user_var = run_menu(stdscr, "Select variable for db_user", keys)
        db_password_var = run_menu(stdscr, "Select variable for db_password", keys)
        return db_name_var, db_user_var, db_password_var

    return curses.wrapper(wrapped)


def interactive_confirm(
    db_name_var: str,
    db_user_var: str,
    db_password_var: str,
    db_name: str,
    db_user: str,
    config_path: Path,
    env_path: Path,
    ssh_host: str,
    ssh_user: str,
) -> bool:
    lines = [
        f"Config file: {config_path}",
        f"Env file:    {env_path}",
        f"SSH target:  {ssh_user}@{ssh_host}",
        "",
        f"db_name     <- {db_name_var} = {db_name}",
        f"db_user     <- {db_user_var} = {db_user}",
        f"db_password <- {db_password_var} = ********",
        "",
        "Proceed with PostgreSQL bootstrap?",
    ]
    return curses.wrapper(lambda stdscr: run_confirm(stdscr, lines))


def run_remote_psql_command(
    sql: str,
    ssh_host: str,
    ssh_user: str,
    ssh_port: int,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    remote_target = f"{ssh_user}@{ssh_host}"

    psql_cmd = [
        "sudo",
        "-u", "postgres",
        "psql",
        "-v", "ON_ERROR_STOP=1",
        "-c", sql,
    ]

    remote_script = " ".join(shlex.quote(part) for part in psql_cmd)

    ssh_cmd = [
        "ssh",
        "-p", str(ssh_port),
        remote_target,
        remote_script,
    ]

    result = subprocess.run(
        ssh_cmd,
        text=True,
        capture_output=capture_output,
    )

    if result.returncode != 0:
        if capture_output:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or "unknown error"
            fail(f"Remote SSH/psql command failed: {details}")
        fail("Remote SSH/psql command failed")

    return result


def remote_database_exists(
    db_name: str,
    ssh_host: str,
    ssh_user: str,
    ssh_port: int,
) -> bool:
    db_name_sql = db_name.replace("'", "''")

    result = run_remote_psql_command(
        sql=f"SELECT 1 FROM pg_database WHERE datname = '{db_name_sql}';",
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
        capture_output=True,
    )

    return "1" in (result.stdout or "").split()


def create_database_if_needed(
    db_name: str,
    db_user: str,
    ssh_host: str,
    ssh_user: str,
    ssh_port: int,
) -> None:
    if remote_database_exists(
        db_name=db_name,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    ):
        info(f"Database already exists: {db_name}")
        return

    sql = f'CREATE DATABASE "{db_name}" OWNER "{db_user}";'
    run_remote_psql_command(
        sql=sql,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    )
    info(f"Database created: {db_name}")


def grant_database_privileges(
    db_name: str,
    db_user: str,
    ssh_host: str,
    ssh_user: str,
    ssh_port: int,
) -> None:
    sql = f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{db_user}";'
    run_remote_psql_command(
        sql=sql,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive PostgreSQL bootstrap via SSH + sudo -u postgres"
    )
    parser.add_argument(
        "env_file",
        help="Path to the .env file",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to config YAML file",
    )
    args = parser.parse_args()

    env_path = Path(args.env_file)
    config_path = Path(args.config)

    env_vars = parse_env_file(env_path)
    config = load_config(config_path)

    ssh_cfg = config["ssh"]
    ssh_host = ssh_cfg["host"]
    ssh_user = ssh_cfg["user"]
    ssh_port = int(ssh_cfg.get("port", 22))

    db_name_var, db_user_var, db_password_var = interactive_mapping(env_vars)

    db_name = env_vars[db_name_var]
    db_user = env_vars[db_user_var]
    db_password = env_vars[db_password_var]

    validate_identifier(db_name, "Database name")
    validate_identifier(db_user, "Database user")

    confirmed = interactive_confirm(
        db_name_var=db_name_var,
        db_user_var=db_user_var,
        db_password_var=db_password_var,
        db_name=db_name,
        db_user=db_user,
        config_path=config_path,
        env_path=env_path,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
    )

    if not confirmed:
        print("Aborted.")
        sys.exit(0)

    info(f"SSH target: {ssh_user}@{ssh_host}:{ssh_port}")
    info(f"Database: {db_name}")
    info(f"User: {db_user}")

    role_sql = build_role_sql(db_user=db_user, db_password=db_password)
    run_remote_psql_command(
        sql=role_sql,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    )

    create_database_if_needed(
        db_name=db_name,
        db_user=db_user,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    )

    grant_database_privileges(
        db_name=db_name,
        db_user=db_user,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    )

    info("Done.")


if __name__ == "__main__":
    main()