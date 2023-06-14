
i = -1

.PHONY: test update cover


test:
	@python test.py $(i)

cover:
	coverage run coverage_test.py
	coverage html