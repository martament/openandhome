#!/bin/bash
# openandhome-flasher unter Linux: System-Python 3 mit den mitgelieferten Paketen (pyserial, esptool)
HIER="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PYTHONPATH="$HIER/bin/pythonportable/Lib/site-packages" exec python3 "$HIER/bin/oh_flasher.py" "$@"
