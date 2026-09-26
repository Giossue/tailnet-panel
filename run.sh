#!/usr/bin/env bash
# Lanzador de Tailnet Panel para Linux y macOS
cd "$(dirname "$0")" || exit 1
if [[ -x .venv/bin/python ]]; then
    exec .venv/bin/python -m app.main "$@"
fi
exec python3 -m app.main "$@"
