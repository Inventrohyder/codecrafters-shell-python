import os
import sys
from typing import Callable

PATH = os.environ.get("PATH")
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


def cd(arguments: list[str]) -> None:
    if len(arguments) == 0:
        os.chdir(os.getenv("HOME"))
        return

    try:
        os.chdir(arguments[0])
    except FileNotFoundError:
        sys.stdout.write(f"cd: {arguments[0]}: No such file or directory\n")
        return


def echo(arguments: list[str]) -> None:
    sys.stdout.write(" ".join(arguments) + "\n")


def exit(arguments: list[str]) -> None:
    sys.exit(int(arguments[0]))


def pwd(_: list[str]) -> None:
    sys.stdout.write(f"{os.getcwd()}\n")


def type(arguments: list[str]) -> None:
    if arguments[0] in BUILT_IN_COMMANDS:
        sys.stdout.write(f"{arguments[0]} is a shell builtin\n")
        return

    cmd_exists, cmd_path = _check_command_exists(arguments[0])
    if cmd_exists:
        sys.stdout.write(f"{arguments[0]} is {cmd_path}\n")
        return

    sys.stdout.write(f"{arguments[0]}: not found\n")


def main():

    while True:
        sys.stdout.write("$ ")

        command = input()

        command_parts: list[str] = command.split(sep=" ")

        cmd: str = command_parts[0]
        arguments: list[str] = command_parts[1:]

        built_in_commands_to_programs_map: dict[str, Callable[[list[str]], None]] = {
            "echo": echo,
            "exit": exit,
            "pwd": pwd,
            "type": type,
            "cd": cd,
        }

        program_func: Callable[[list[str]], None] | None = (
            built_in_commands_to_programs_map.get(cmd, None)
        )

        if program_func is None:
            cmd_exists, _ = _check_command_exists(cmd)
            if cmd_exists:
                os.system(command)  # nosec: B605
            else:
                sys.stdout.write(f"{cmd}: command not found\n")
            continue

        program_func(arguments)


if __name__ == "__main__":
    main()
