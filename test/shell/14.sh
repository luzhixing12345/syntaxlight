$ ./re2postfix "a(abc|c|bc)+ab+"

[a]: token_number = [0] token_number = [1]
[(]: token_number = [1] pipe_number = [0] -> p++
[a]: token_number = [0] token_number = [1]
[b]: token_number = [1] token_number = [2]
[c]: token_number = [2] token_number = [2]
[|]: token_number = [2] pipe_number = [1]
[c]: token_number = [0] token_number = [1]
[|]: token_number = [1] pipe_number = [2]
[b]: token_number = [0] token_number = [1]
[c]: token_number = [1] token_number = [2]
[)]: token_number = [2] pipe_number = [2]
[+]:
[a]: token_number = [2] token_number = [2]
[b]: token_number = [2] token_number = [2]
[+]:

postfix = aab.c.cbc.||+.a.b+.