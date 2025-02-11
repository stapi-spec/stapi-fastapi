#!/usr/bin/env bash

set -Eeuo pipefail
# set -x # print each command before executing

ruff check --fix # lint python files
ruff format # format python files
