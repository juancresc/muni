#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=src python -m muni.cli "$@"

