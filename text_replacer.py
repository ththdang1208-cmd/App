#!/usr/bin/env python3
"""Simple global text replacement app.

Listens for keyboard input and replaces configured trigger words/phrases
with replacements after you finish typing them.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


DELIMITERS = {
    " ",
    "\n",
    "\t",
    ".",
    ",",
    "!",
    "?",
    ";",
    ":",
    ")",
    "]",
    "}",
}
BACKTRACK_LIMIT = 250


@dataclass
class Config:
    replacements: Dict[str, str]


class TextReplacer:
    def __init__(self, replacements: Dict[str, str]) -> None:
        from pynput.keyboard import Controller, Key, Listener

        if not replacements:
            raise ValueError("At least one replacement pair is required.")

        self.replacements = dict(sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True))
        self.buffer = ""
        self.keyboard = Controller()
        self.Key = Key
        self.Listener = Listener
        self._ignore_until = 0.0

    def _handle_delimiter(self, delimiter: str) -> None:
        for trigger, replacement in self.replacements.items():
            if self.buffer.endswith(trigger):
                self._replace_text(trigger, replacement, delimiter)
                self.buffer = ""
                return

        self.buffer = ""

    def _replace_text(self, trigger: str, replacement: str, delimiter: str) -> None:
        self._ignore_until = time.time() + 0.2

        for _ in range(len(trigger) + len(delimiter)):
            self.keyboard.press(self.Key.backspace)
            self.keyboard.release(self.Key.backspace)

        self.keyboard.type(replacement)
        if delimiter:
            self.keyboard.type(delimiter)

    def on_press(self, key: Any) -> None:
        if time.time() < self._ignore_until:
            return

        if key == self.Key.backspace:
            self.buffer = self.buffer[:-1]
            return

        if key in (self.Key.space, self.Key.enter, self.Key.tab):
            delimiter = {self.Key.space: " ", self.Key.enter: "\n", self.Key.tab: "\t"}[key]
            self._handle_delimiter(delimiter)
            return

        char = getattr(key, "char", None)
        if not char:
            return

        if char in DELIMITERS:
            self._handle_delimiter(char)
            return

        self.buffer = (self.buffer + char)[-BACKTRACK_LIMIT:]

    def run(self) -> None:
        print("Text replacer is running. Press Ctrl+C to stop.")
        print("Active rules:")
        for trigger, replacement in self.replacements.items():
            print(f"  {trigger!r} -> {replacement!r}")

        with self.Listener(on_press=self.on_press) as listener:
            listener.join()


def parse_mapping_items(items: list[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --map entry '{item}'. Expected format: trigger=replacement")

        trigger, replacement = item.split("=", 1)
        trigger = trigger.strip()
        if not trigger:
            raise ValueError("Trigger text cannot be empty.")
        mapping[trigger] = replacement

    return mapping


def load_config(path: Path) -> Config:
    data = json.loads(path.read_text(encoding="utf-8"))
    replacements = data.get("replacements", {})
    if not isinstance(replacements, dict):
        raise ValueError("'replacements' in config file must be an object.")

    clean = {str(k): str(v) for k, v in replacements.items() if str(k)}
    return Config(replacements=clean)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Global text replacement tool")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to a JSON file containing {\"replacements\": {\"trigger\": \"replacement\"}}",
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="TRIGGER=REPLACEMENT",
        help="Inline replacement rule. May be passed multiple times.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    replacements: Dict[str, str] = {}

    if args.config:
        config = load_config(args.config)
        replacements.update(config.replacements)

    if args.map:
        replacements.update(parse_mapping_items(args.map))

    if not replacements:
        parser.error("No replacement rules supplied. Use --config and/or --map.")

    app = TextReplacer(replacements)
    app.run()


if __name__ == "__main__":
    main()
