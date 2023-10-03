#!/usr/bin/env bash

if [ -d layer ]; then rm -rf layer; fi
if [ -d .venv ]; then rm -rf .venv; fi
python3.10 -m venv .venv
source .venv/bin/activate
pip install pip -U
pip install -r requirements.txt
mkdir -p layer/python
cp -r .venv/lib layer/python/
deactivate
rm -rf .venv
