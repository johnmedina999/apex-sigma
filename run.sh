#!/usr/bin/env bash

# Don't let CDPATH interfere with the cd command
unset CDPATH
cd "$(dirname "$0")"

# activate the python virtualenv
#source ".venv/bin/activate"

# activate local python version
export PATH=$(HOME)/bin/.pyenv/shims:$PATH
eval "$(pyenv init -)"
pyenv local 3.8.2

# Apperently the way pyenv installed python 3.8 makes ssl cry if left alone
# Make sure this is up to date by doing `apt-get update ca-certificates --upgrade`
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Execute the bot
exec python ./run.py
