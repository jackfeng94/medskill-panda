#!/bin/sh
# Run a Medskill Panda hook script with whichever Python 3 is installed.
# Claude Code runs hooks through sh on macOS and Linux and through Git Bash on Windows.
# If no Python is found the hook does nothing: it must never stop the user's work by itself.
dir=$(cd "$(dirname "$0")" && pwd)
# Keep the installed plugin clean: no __pycache__ folders next to the hook scripts.
export PYTHONDONTWRITEBYTECODE=1
for py in python3 python py; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
    exec "$py" "$dir/$1"
  fi
done
exit 0
