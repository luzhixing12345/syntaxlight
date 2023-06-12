
.PHONY: test update cover


test:
	python test.py

update:
	python update.py

cover:
	coverage run coverage_test.py
	coverage html