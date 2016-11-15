#!/bin/bash

set -e

# additional entrypoint commands go here (exports, etc.)

# editable install of development source
pip install -e .

exec "$@"
