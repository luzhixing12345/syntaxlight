
i = 0

.PHONY: test lexer cover


test:
	@python test.py $(i)

lexer:
	@python test.py $(i) lexer

cover:
	coverage run coverage_test.py
	coverage html