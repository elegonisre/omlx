#!/usr/bin/env python3
"""omlx - A command-line tool for managing and launching applications.

Fork of jundot/omlx with additional features and improvements.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

__version__ = "0.1.0"
__author__ = "omlx contributors"

CONFIG_DIR = Path.home() / ".config" / "omlx"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from the config file."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """Save configuration to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def cmd_list(args) -> int:
    """List all registered applications."""
    config = load_config()
    apps = config.get("apps", {})
    if not apps:
        print("No applications registered.")
        return 0
    # Sort alphabetically so the list is easier to scan
    for name, info in sorted(apps.items()):
        path = info.get("path", "unknown")
        # Show a checkmark if the path still exists, warning sign if not
        exists_marker = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists_marker} {name:<20} {path}")
    return 0


def cmd_add(args) -> int:
    """Register a new application."""
    config = load_config()
    apps = config.setdefault("apps", {})
    if args.name in apps:
        print(f"Error: '{args.name}' is already registered.", file=sys.stderr)
        return 1
    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.", file=sys.stderr)
        return 1
    apps[args.name] = {"path": path}
    save_config(config)
    print(f"Registered '{args.name}' -> {path}")
    return 0


def cmd_remove(args) -> int:
    """Remove a registered application."""
    config = load_config()
    apps = config.get("apps", {})
    if args.name not in apps:
        print(f"Error: '{args.name}' is not registered.", file=sys.stderr)
        return 1
    del apps[args.name]
    save_config(config)
    print(f"Removed '{args.name}'.")
    return 0


def cmd_open(args) -> int:
    """Launch a registered application."""
    config = load_config()
    apps = config.get("apps", {})
    if args.name not in apps:
        print(f"Error: '{args.name}' is not registered.", file=sys.stderr)
        return 1
    path = apps[args.name]["path"]
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "linux":
            subprocess.Popen(["xdg-open", path])
        else:
            os.startfile(path)
        print(f"Opened '{args.name}'.")
    except Exception as e:
        print(f"Error: Failed to open '{args.name}': {e}", file=sys.stderr)
        return 1
    return 0
