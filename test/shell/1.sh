sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
    libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev \
    python3-dev python-is-python3 libboost-all-dev pkg-config libhdf5-dev libpng-dev

$ pgtbltest
ugetpid_test starting
ugetpid_test: OK
pgaccess_test starting
pgtbltest: pgaccess_test failed: incorrect access bits set, pid=3

(base) kamilu@LZX:~/xv6-labs-2022$ make grade
== Test pgtbltest ==
$ make qemu-gdb
(4.0s)
== Test   pgtbltest: ugetpid ==
  pgtbltest: ugetpid: OK
== Test   pgtbltest: pgaccess ==
  pgtbltest: pgaccess: OK
== Test pte printout ==
$ make qemu-gdb
pte printout: OK (0.5s)
== Test answers-pgtbl.txt == answers-pgtbl.txt: FAIL
    Cannot read answers-pgtbl.txt
== Test usertests ==
$ make qemu-gdb
(71.4s)
== Test   usertests: all tests ==
  usertests: all tests: OK
== Test time ==
time: FAIL
    Cannot read time.txt
Score: 40/46