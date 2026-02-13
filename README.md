# Python Text Replacer

This app listens to what you type and automatically replaces trigger words/phrases with text you choose.

## What it does

If you type a trigger and then finish it with a delimiter (space, enter, tab, or punctuation), it replaces the trigger immediately.

Example rules:
- `omw` -> `On my way!`
- `ty` -> `Thank you`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

### Option 1: Use inline rules

```bash
python text_replacer.py --map "omw=On my way!" --map "brb=Be right back"
```

### Option 2: Use a JSON config file

```bash
python text_replacer.py --config example_config.json
```

Config format:

```json
{
  "replacements": {
    "trigger": "replacement"
  }
}
```

## Notes

- This is a global keyboard listener (works across apps while running).
- On Linux you may need accessibility/input permissions depending on your desktop environment.
- Stop it with `Ctrl+C` in the terminal where it's running.
