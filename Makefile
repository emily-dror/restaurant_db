# Copyright (c) 2024, Emily Dror

## Project Paramaters
ID1 := 324934082
ID2 := 326757283

.PHONY: setup-venv
install-venv:
	python3 -m venv venv

.PHONY: zip
zip:
	cp src/Solution.py build/Solution.py
	cp docs/$(ID1)-$(ID2).py build/$(ID1)-$(ID2).py
	cd build && zip ../$ID1-$ID2.zip Solution.py $(ID1)-$(ID2).py

