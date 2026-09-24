#!/bin/zsh
set -e
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print 'Install the project following README.md, then run again.'
  exit 1
fi
if [[ ! -x build/sample_mcd ]]; then
  .venv/bin/python scripts/build_mcd.py
fi
print 'Mars Wind Lab : http://127.0.0.1:8765'
print 'Open this address in your browser. Press Ctrl+C to stop.'
exec .venv/bin/python -m uvicorn marswind.server:app --app-dir src --host 127.0.0.1 --port 8765
