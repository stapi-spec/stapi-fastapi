#!/usr/bin/env bash

set -Eeuo pipefail
# set -x # print each command before executing

MYPYPATH=src mypy src/ tests/
