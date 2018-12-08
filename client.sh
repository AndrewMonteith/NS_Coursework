#!/bin/bash
if [[ `python --version` == "Python 3."* ]]; then
	python client.py
else
	python3 client.py
fi
