#!/bin/bash

set -e

# additional entrypoint commands go here (exports, etc.)
zipline ingest -b quantopian-quandl

exec "$@"
