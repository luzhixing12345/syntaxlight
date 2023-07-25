
i = 0
t = lua
s = vscode

.PHONY: test lexer cover

test:
	@python test.py -i $(i) -t $(t) -s $(s)

lexer:
	@python test.py -i $(i) -t $(t) -s $(s) --lexer

cover:
	coverage run coverage_test.py
	coverage html