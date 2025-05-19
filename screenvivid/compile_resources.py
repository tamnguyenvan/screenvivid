import subprocess

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error details: {e}")

def main():
    # Commands to run
    commands = [
        "pyside6-rcc -o rc_main.py resources/main.qrc",
        "pyside6-rcc -o rc_icons.py resources/icons.qrc",
        "pyside6-rcc -o rc_images.py resources/images.qrc"
    ]

    # Execute each command
    for command in commands:
        run_command(command)

if __name__ == "__main__":
    main()
