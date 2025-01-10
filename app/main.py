import os
import shlex
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
        os.chdir(os.path.expanduser(arguments[0]))
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


def _handle_redirection(command_parts: list[str]) -> tuple[list[str], str | None]:
    redirect_index = -1
    if ">" in command_parts:
        redirect_index = command_parts.index(">")
    elif "1>" in command_parts:
        redirect_index = command_parts.index("1>")

    if redirect_index == -1:
        return command_parts, None

    if redirect_index + 1 >= len(command_parts):
        sys.stdout.write("syntax error near unexpected token 'newline'\n")
        return command_parts, None

    output_file = command_parts[redirect_index + 1]

    return command_parts[:redirect_index], output_file


def main():
    while True:
        sys.stdout.write("$ ")

        command = input()

        # Split command preserving quotes
        command_parts: list[str] = shlex.split(command)

        if not command_parts:
            continue

        cmd: str = command_parts[0]

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
            if not cmd_exists:
                sys.stdout.write(f"{cmd}: command not found\n")
                continue
            os.system(command)  # nosec: B605
            continue

        command_parts, output_file = _handle_redirection(command_parts)

        if output_file is not None:
            try:
                # Save original stdout and redirect to file
                original_stdout = sys.stdout
                sys.stdout = open(output_file, "w")
            except IOError as e:
                sys.stdout.write(f"Failed to open {output_file}: {str(e)}\n")
                continue

        arguments: list[str] = command_parts[1:]
        program_func(arguments)

        # Restore original stdout if we redirected
        if output_file is not None:
            sys.stdout.close()
            sys.stdout = original_stdout


if __name__ == "__main__":
    main()
