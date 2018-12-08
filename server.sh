#!/bin/bash
if [[ `python --version` == "Python 3."* ]]; then
	python server.py
else
	python3 server.py
fi
