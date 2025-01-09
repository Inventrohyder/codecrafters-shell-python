import os
import sys


def main():

    PATH = os.environ.get("PATH")
    PATH_LIST = PATH.split(os.pathsep)

    while True:
        sys.stdout.write("$ ")

        command = input()

        built_in_commands = {
            "echo",
            "exit",
            "type",
        }

        command_parts = command.split(sep=" ")

        cmd = command_parts[0]
        arguments = command_parts[1:]

        if cmd not in built_in_commands:
            sys.stdout.write(f"{cmd}: command not found\n")
        elif cmd == "exit":
            sys.exit(int(arguments[0]))
        elif cmd == "echo":
            sys.stdout.write(" ".join(arguments) + "\n")
        elif cmd == "type":
            if arguments in built_in_commands:
                sys.stdout.write(f"{arguments} is a shell builtin\n")
            else:
                for path in PATH_LIST:
                    cmd_path = os.path.join(path, arguments)
                    if os.path.exists(cmd_path):
                        sys.stdout.write(f"{arguments} is {cmd_path}\n")
                        break
                else:
                    sys.stdout.write(f"{arguments}: not found\n")


if __name__ == "__main__":
    main()
