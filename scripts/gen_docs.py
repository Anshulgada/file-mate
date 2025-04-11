import os
import importlib
import pkgutil
from filemate import commands
from click import Context

# from filemate.cli import cli

DOCS_DIR = "docs/commands"
os.makedirs(DOCS_DIR, exist_ok=True)

for module_info in pkgutil.walk_packages(commands.__path__):
    mod = importlib.import_module(f"filemate.commands.{module_info.name}")
    if hasattr(mod, "cli"):
        cmd = mod.cli
        help_text = cmd.get_help(Context(cmd))
        with open(f"{DOCS_DIR}/{module_info.name}.md", "w", encoding="utf-8") as f:
            f.write(f"# `{module_info.name}` Command\n\n```\n{help_text}\n```")
