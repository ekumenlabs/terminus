#!/bin/sh

# Exit if any of the commands fails
set -e

git stash -q --keep-index
./run_pep8.sh
./run_tests.sh
git stash pop -q
