#!/bin/sh

chemin="$(cd "$(dirname "$0")";pwd)"
cd "${chemin}"


rm -rf __pycache__

rm -rf QWidgetsCustom/__pycache__

rm -rf Languages/*.qm
