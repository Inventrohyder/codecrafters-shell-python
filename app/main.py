import os
import sys

PATH = os.environ.get("PATH")
PATH_LIST = PATH.split(os.pathsep)


def check_command_exists(command: str) -> tuple[bool, str | None]:
    for path in PATH_LIST:
        cmd_path = os.path.join(path, command)
        if os.path.exists(cmd_path):
            return True, cmd_path
    return False, None


def main():

    while True:
        sys.stdout.write("$ ")

        command = input()

        built_in_commands = {
            "echo",
            "exit",
            "pwd",
            "type",
        }

        command_parts = command.split(sep=" ")

        cmd = command_parts[0]
        arguments = command_parts[1:]

        if cmd == "exit":
            sys.exit(int(arguments[0]))
        elif cmd == "echo":
            sys.stdout.write(" ".join(arguments) + "\n")
        elif cmd == "type":
            if arguments[0] in built_in_commands:
                sys.stdout.write(f"{arguments[0]} is a shell builtin\n")
            else:
                cmd_exists, cmd_path = check_command_exists(arguments[0])
                if cmd_exists:
                    sys.stdout.write(f"{arguments[0]} is {cmd_path}\n")
                else:
                    sys.stdout.write(f"{arguments[0]}: not found\n")
        elif cmd == "pwd":
            sys.stdout.write(os.getcwd() + "\n")
        elif cmd not in built_in_commands:
            cmd_exists, cmd_path = check_command_exists(cmd)
            if cmd_exists:
                os.system(command)  # nosec: B605
            else:
                sys.stdout.write(f"{cmd}: command not found\n")


if __name__ == "__main__":
    main()
