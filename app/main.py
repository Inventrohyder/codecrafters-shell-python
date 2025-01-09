import sys


def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
