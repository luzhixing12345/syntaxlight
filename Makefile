
i = 0
t = rust
s = vscode

KNOWN_ERROR = 19

.PHONY: test lexer cover

test:
	@python test.py -i $(i) -t $(t) -s $(s)

lexer:
	@python test.py -i $(i) -t $(t) -s $(s) --lexer

cover:
	coverage run coverage_test.py
	coverage html

doc:
	python copy_test.py
	@echo should be $(KNOWN_ERROR) ERROR
	zood -g