import sys
from pathlib import Path

TEMPLATE = '''import rich_click as click

@click.command()
def {cmd}() -> None:
    """
    {desc}
    """
    click.echo("Running {cmd} command")
'''
# This template is used to create a new command file in the commands directory.

INIT_IMPORT = "\nfrom .{cmd} import {cmd}\ncli.add_command({cmd})\n"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/new_command.py <command_name> [description]")
        sys.exit(1)

    cmd = sys.argv[1]
    desc = sys.argv[2] if len(sys.argv) > 2 else f"{cmd.capitalize()} command"

    command_dir = Path("src/filemate/commands")
    command_dir.mkdir(parents=True, exist_ok=True)

    cmd_file = command_dir / f"{cmd}.py"
    if cmd_file.exists():
        print(f"Command '{cmd}' already exists.")
        sys.exit(1)

    # Write the new command file
    cmd_file.write_text(TEMPLATE.format(cmd=cmd, desc=desc))

    # Update __init__.py
    init_file = command_dir / "__init__.py"
    with open(init_file, "a") as f:
        f.write(INIT_IMPORT.format(cmd=cmd))

    print(f"✅ Created new command: {cmd}")


if __name__ == "__main__":
    main()
