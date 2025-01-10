import os
import shlex
import sys
from collections.abc import Sequence
from contextlib import redirect_stderr, redirect_stdout
from typing import Callable

PATH = os.environ.get("PATH") or ""
PATH_LIST = PATH.split(os.pathsep)

BUILT_IN_COMMANDS: set[str] = {
    "cd",
    "echo",
    "exit",
    "pwd",
    "type",
}


def _check_command_exists(command: str) -> tuple[bool, str | None]:
    for path in PATH_LIST:
        cmd_path = os.path.join(path, command)
        if os.path.exists(cmd_path):
            return True, cmd_path
    return False, None


def cd(arguments: Sequence[str]) -> None:
    if len(arguments) == 0:
        os.chdir(os.getenv("HOME") or "")
        return

    try:
        os.chdir(os.path.expanduser(arguments[0]))
    except FileNotFoundError:
        sys.stderr.write(f"cd: {arguments[0]}: No such file or directory\n")
        return


def echo(arguments: Sequence[str]) -> None:
    sys.stdout.write(" ".join(arguments) + "\n")


def exit(arguments: Sequence[str]) -> None:
    sys.exit(int(arguments[0]))


def pwd(_: Sequence[str]) -> None:
    sys.stdout.write(f"{os.getcwd()}\n")


def type(arguments: Sequence[str]) -> None:
    if arguments[0] in BUILT_IN_COMMANDS:
        sys.stdout.write(f"{arguments[0]} is a shell builtin\n")
        return

    cmd_exists, cmd_path = _check_command_exists(arguments[0])
    if cmd_exists:
        sys.stdout.write(f"{arguments[0]} is {cmd_path}\n")
        return

    sys.stderr.write(f"{arguments[0]}: not found\n")


def main() -> None:
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_parts: list[str] = shlex.split(command)

        if not command_parts:
            continue

        cmd: str = command_parts[0]
        build_in_commands_to_programs_map: dict[
            str, Callable[[Sequence[str]], None]
        ] = {
            "echo": echo,
            "exit": exit,
            "pwd": pwd,
            "type": type,
            "cd": cd,
        }
        program_func: Callable[[Sequence[str]], None] | None = (
            build_in_commands_to_programs_map.get(cmd, None)
        )

        # Handle non-built-in commands
        if program_func is None:
            cmd_exists, _ = _check_command_exists(cmd)
            if not cmd_exists:
                sys.stderr.write(f"{cmd}: command not found\n")
                continue
            os.system(command)  # nosec: B605
            continue

        # Handle built-in commands using the already retrieved program_func
        match command_parts:
            case [*run_cmd, ">>", file] | [*run_cmd, "1>>", file]:
                with open(file, "a") as f:
                    with redirect_stdout(f):
                        program_func(run_cmd[1:])
            case [*run_cmd, ">", file] | [*run_cmd, "1>", file]:
                with open(file, "w") as f:
                    with redirect_stdout(f):
                        program_func(run_cmd[1:])
            case [*run_cmd, "2>>"]:
                with open(file, "a") as f:
                    with redirect_stderr(f):
                        program_func(run_cmd[1:])
            case [*run_cmd, "2>", file] | [*run_cmd, "2>>", file]:
                with open(file, "w") as f:
                    with redirect_stderr(f):
                        program_func(run_cmd[1:])
            case _:
                program_func(command_parts[1:])


if __name__ == "__main__":
    main()
