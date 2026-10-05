# SPDX-License-Identifier: MIT
.PHONY: test image checkout parse fetch build
test:
	python3 -m unittest discover -s tests -v
image checkout parse fetch build:
	python3 scripts/bsp.py $@
