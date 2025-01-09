import sys


def main():
    while True:
        sys.stdout.write("$ ")

        command = input()

        command_parts = command.split(sep=" ")
        if command_parts[0] == "exit":
            sys.exit(int(command_parts[1]))
        elif command_parts[0] == "echo":
            sys.stdout.write(" ".join(command_parts[1:]) + "\n")
        else:
            sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
