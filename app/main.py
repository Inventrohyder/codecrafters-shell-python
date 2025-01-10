import os
import shlex
import sys
from functools import partial
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
        sys.stderr.write(f"cd: {arguments[0]}: No such file or directory\n")
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

    sys.stderr.write(f"{arguments[0]}: not found\n")


def _parse_redirection_target(
    command_parts: list[str],
    redirect_markers: list[str],
) -> tuple[list[str], str | None]:
    redirect_index = -1
    for marker in redirect_markers:
        if marker in command_parts:
            redirect_index = command_parts.index(marker)
            break

    if redirect_index == -1:
        return command_parts, None

    if redirect_index + 1 >= len(command_parts):
        sys.stderr.write("syntax error near unexpected token 'newline'\n")
        return command_parts, None

    output_file = command_parts[redirect_index + 1]
    return command_parts[:redirect_index], output_file


parse_stdout_redirection = partial(
    _parse_redirection_target, redirect_markers=[">", "1>"]
)
parse_stderr_redirection = partial(_parse_redirection_target, redirect_markers=["2>"])


def parse_command_redirections(
    command_parts: list[str],
) -> tuple[list[str], str | None, str | None]:
    command_parts, std_output_file = parse_stdout_redirection(command_parts)
    command_parts, std_err_file = parse_stderr_redirection(command_parts)

    return command_parts, std_output_file, std_err_file


def _handle_program_call(
    program_func: Callable[[list[str]], None], command_parts: list[str]
) -> None:
    command_parts, std_output_file, std_err_file = parse_command_redirections(
        command_parts
    )

    if std_output_file is not None:
        try:
            original_stdout = sys.stdout
            sys.stdout = open(std_output_file, "w")
        except IOError as e:
            sys.stderr.write(f"Failed to open {std_output_file}: {str(e)}\n")
            return

    if std_err_file is not None:
        try:
            original_stderr = sys.stderr
            sys.stderr = open(std_err_file, "w")
        except IOError as e:
            sys.stderr.write(f"Failed to open {std_err_file}: {str(e)}\n")
            return

    arguments: list[str] = command_parts[1:]
    program_func(arguments)

    if std_output_file is not None:
        sys.stdout.close()
        sys.stdout = original_stdout

    if std_err_file is not None:
        sys.stderr.close()
        sys.stderr = original_stderr


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
                sys.stderr.write(f"{cmd}: command not found\n")
                continue
            os.system(command)  # nosec: B605
            continue

        _handle_program_call(program_func, command_parts)


if __name__ == "__main__":
    main()
