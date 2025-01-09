import sys


def main():
    while True:
        sys.stdout.write("$ ")

        command = input()

        built_in_commands = {
            "echo",
            "exit",
            "type",
        }

        command_parts = command.split(sep=" ")

        if command_parts[0] not in built_in_commands:
            sys.stdout.write(f"{command}: command not found\n")
        elif command_parts[0] == "exit":
            sys.exit(int(command_parts[1]))
        elif command_parts[0] == "echo":
            sys.stdout.write(" ".join(command_parts[1:]) + "\n")
        elif command_parts[0] == "type":
            if command_parts[1] in built_in_commands:
                sys.stdout.write(f"{command_parts[1]} is a shell builtin\n")
            else:
                sys.stdout.write(f"{command_parts[1]}: not found\n")


if __name__ == "__main__":
    main()
