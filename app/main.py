import sys


def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        # if command is exit, call the exit builtin
        command_parts = command.split()
        if command_parts[0] == "exit":
            sys.exit(command_parts[1])

        sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
