(base) kamilu@LZX:~/libc$ ./kcc a.c -o a
file[0] = [a.c]
output file = [a]
(base) kamilu@LZX:~/libc$ ./kcc a.c -I include1 -Iinclude2 -I=include3 -o a
file[0] = [a.c]
include path[0] = [include1]
include path[1] = [include2]
include path[2] = [include3]
output file = [a]
(base) kamilu@LZX:~/libc$ ./kcc a.c -I include1 -Iinclude2 -I=include3 -labc -l=ccc -o a
file[0] = [a.c]
include path[0] = [include1]
include path[1] = [include2]
include path[2] = [include3]
library name[0] = [abc]
library name[1] = [ccc]
output file = [a]