
# lua
## [1.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/1.lua)

```lua
local k0aux <const> = 0
local k0 <const> = k0aux
local k1 <const> = 1
local k3 <const> = 3
local k6 <const> = k3 + (k3 << k0)
local kFF0 <const> = 0xFF0
local k3_78 <const> = 3.78
```
## [2.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/2.lua)

```lua
-- 1. 变量和数据类型
local numberVar = 42
local stringVar = "Hello, Lua!"
local booleanVar = true
local tableVar = {1, 2, 3}
local functionVar = function(x) return x * 2 end

-- 2. 条件语句
if numberVar > 50 then
    print("Number is greater than 50")
elseif numberVar == 50 then
    print("Number is equal to 50")
else
    print("Number is less than 50")
end

-- 3. 循环语句
for i = 1, 5 do
    print("Iteration", i)
end

local counter = 0
while counter < 5 do
    counter = counter + 1
    print("Counter:", counter)
end

-- 4. 函数定义
function sayHello(name)
    print("Hello,", name)
end

-- 5. 函数调用
sayHello("Alice")

-- 6. 表(Table)
local person = {
    name = "Bob",
    age = 30,
    isMale = true
}

print(person.name) -- Output: Bob

-- 7. 匿名函数
local add = function(a, b)
    return a + b
end

print(add(3, 4)) -- Output: 7

-- 8. 迭代器(Pairs和ipairs)
local fruits = {"apple", "banana", "orange"}

for index, fruit in ipairs(fruits) do
    print("Fruit", index, "is", fruit)
end

-- 9. 模块(Module)
local myModule = {}

function myModule.sayGoodbye(name)
    print("Goodbye,", name)
end

return myModule

```
## [3.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/3.lua)

```lua
-- 定义斐波那契数列函数
function fibonacci(n)
    local fib = {0, 1}
    for i = 3, n do
        fib[i] = fib[i - 1] + fib[i - 2]
    end
    return fib
end

-- 打印前n个斐波那契数
function print_fibonacci(n)
    local fib = fibonacci(n)
    print("前" .. n .. "个斐波那契数列:")
    for i = 1, n do
        io.write(fib[i] .. " ")
    end
    print()  -- 换行
end

-- 调用函数打印前10个斐波那契数
print_fibonacci(10)

```
## [4.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/4.lua)

```lua
function factorial(n)
    if n <= 0 then
        return 1
    else
        return n * factorial(n - 1)
    end
end

local result = factorial(5)
print("Factorial of 5:", result)

local a = 10

function modifyGlobal()
    a = 20
end

function accessGlobal()
    print("Global a:", a)
end

modifyGlobal()
accessGlobal()

local largeNumber = 2^100
print("Large number:", largeNumber)

local largeTable = {}
for i = 1, 10^6 do
    largeTable[i] = i
end

print("Large table length:", #largeTable)

local longString = ""
for i = 1, 10^5 do
    longString = longString .. tostring(i)
end

print("Length of longString:", #longString)

local nestedTable = {
    a = 1,
    b = {
        c = 2,
        d = {
            e = 3
        }
    }
}

print("Value of nestedTable.b.d.e:", nestedTable.b.d.e)

function multipleReturns()
    return 1, 2, 3
end

local a, b, c = multipleReturns()
print("Values:", a, b, c)

local mixedTable = {
    "first",
    "second",
    key1 = "value1",
    key2 = "value2",
    key3 = {
        key1 = function ()
            
        end,
        key2 = 1
    }
}

print("Value at index 2:", mixedTable[2])
print("Value of key 'key1':", mixedTable.key1)
print(mixedTable.key3.key1)
print(mixedTable.key3.key2)
print(mixedTable.key3:asd())

local value = 42

if value then
    print("Value is truthy")
else
    print("Value is falsy")
end

```
## [5.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/5.lua)

```lua

-- $Id: testes/all.lua $
-- See Copyright Notice at the end of this file


local version = "Lua 5.4"
if _VERSION ~= version then
  io.stderr:write("This test suite is for ", version,
                  ", not for ", _VERSION, "\nExiting tests")
  return
end


_G.ARG = arg   -- save arg for other tests


-- next variables control the execution of some tests
-- true means no test (so an undefined variable does not skip a test)
-- defaults are for Linux; test everything.
-- Make true to avoid long or memory consuming tests
_soft = rawget(_G, "_soft") or false
-- Make true to avoid non-portable tests
_port = rawget(_G, "_port") or false
-- Make true to avoid messages about tests not performed
_nomsg = rawget(_G, "_nomsg") or false


local usertests = rawget(_G, "_U")

if usertests then
  -- tests for sissies ;)  Avoid problems
  _soft = true
  _port = true
  _nomsg = true
end

-- tests should require debug when needed
debug = nil


if usertests then
  T = nil    -- no "internal" tests for user tests
else
  T = rawget(_G, "T")  -- avoid problems with 'strict' module
end


--[=[
  example of a long [comment],
  [[spanning several [lines]]]

]=]

print("\n\tStarting Tests")

do
  -- set random seed
  local random_x, random_y = math.randomseed()
  print(string.format("random seeds: %d, %d", random_x, random_y))
end

print("current path:\n****" .. package.path .. "****\n")


local initclock = os.clock()
local lastclock = initclock
local walltime = os.time()

local collectgarbage = collectgarbage

do   -- (

-- track messages for tests not performed
local msgs = {}
function Message (m)
  if not _nomsg then
    print(m)
    msgs[#msgs+1] = string.sub(m, 3, -3)
  end
end

assert(os.setlocale"C")

local T,print,format,write,assert,type,unpack,floor =
      T,print,string.format,io.write,assert,type,table.unpack,math.floor

-- use K for 1000 and M for 1000000 (not 2^10 -- 2^20)
local function F (m)
  local function round (m)
    m = m + 0.04999
    return format("%.1f", m)      -- keep one decimal digit
  end
  if m < 1000 then return m
  else
    m = m / 1000
    if m < 1000 then return round(m).."K"
    else
      return round(m/1000).."M"
    end
  end
end

local Cstacklevel

local showmem
if not T then
  local max = 0
  showmem = function ()
    local m = collectgarbage("count") * 1024
    max = (m > max) and m or max
    print(format("    ---- total memory: %s, max memory: %s ----\n",
          F(m), F(max)))
  end
  Cstacklevel = function () return 0 end   -- no info about stack level
else
  showmem = function ()
    T.checkmemory()
    local total, numblocks, maxmem = T.totalmem()
    local count = collectgarbage("count")
    print(format(
      "\n    ---- total memory: %s (%.0fK), max use: %s,  blocks: %d\n",
      F(total), count, F(maxmem), numblocks))
    print(format("\t(strings:  %d, tables: %d, functions: %d, "..
                 "\n\tudata: %d, threads: %d)",
                 T.totalmem"string", T.totalmem"table", T.totalmem"function",
                 T.totalmem"userdata", T.totalmem"thread"))
  end

  Cstacklevel = function ()
    local _, _, ncalls = T.stacklevel()
    return ncalls    -- number of C calls
  end
end


local Cstack = Cstacklevel()

--
-- redefine dofile to run files through dump/undump
--
local function report (n) print("\n***** FILE '"..n.."'*****") end
local olddofile = dofile
local dofile = function (n, strip)
  showmem()
  local c = os.clock()
  print(string.format("time: %g (+%g)", c - initclock, c - lastclock))
  lastclock = c
  report(n)
  local f = assert(loadfile(n))
  local b = string.dump(f, strip)
  f = assert(load(b))
  return f()
end

dofile('main.lua')

-- trace GC cycles
require"tracegc".start()

report"gc.lua"
local f = assert(loadfile('gc.lua'))
f()

dofile('db.lua')
assert(dofile('calls.lua') == deep and deep)
_G.deep = nil
olddofile('strings.lua')
olddofile('literals.lua')
dofile('tpack.lua')
assert(dofile('attrib.lua') == 27)
dofile('gengc.lua')
assert(dofile('locals.lua') == 5)
dofile('constructs.lua')
dofile('code.lua', true)
if not _G._soft then
  report('big.lua')
  local f = coroutine.wrap(assert(loadfile('big.lua')))
  assert(f() == 'b')
  assert(f() == 'a')
end
dofile('cstack.lua')
dofile('nextvar.lua')
dofile('pm.lua')
dofile('utf8.lua')
dofile('api.lua')
assert(dofile('events.lua') == 12)
dofile('vararg.lua')
dofile('closure.lua')
dofile('coroutine.lua')
dofile('goto.lua', true)
dofile('errors.lua')
dofile('math.lua')
dofile('sort.lua', true)
dofile('bitwise.lua')
assert(dofile('verybig.lua', true) == 10); collectgarbage()
dofile('files.lua')

if #msgs > 0 then
  local m = table.concat(msgs, "\n  ")
  warn("#tests not performed:\n  ", m, "\n")
end

print("(there should be two warnings now)")
warn("@on")
warn("#This is ", "an expected", " warning")
warn("@off")
warn("******** THIS WARNING SHOULD NOT APPEAR **********")
warn("******** THIS WARNING ALSO SHOULD NOT APPEAR **********")
warn("@on")
warn("#This is", " another one")

-- no test module should define 'debug'
assert(debug == nil)

local debug = require "debug"

print(string.format("%d-bit integers, %d-bit floats",
        string.packsize("j") * 8, string.packsize("n") * 8))

debug.sethook(function (a) assert(type(a) == 'string') end, "cr")

-- to survive outside block
_G.showmem = showmem


assert(Cstack == Cstacklevel(),
  "should be at the same C-stack level it was when started the tests")

end   --)

local _G, showmem, print, format, clock, time, difftime,
      assert, open, warn =
      _G, showmem, print, string.format, os.clock, os.time, os.difftime,
      assert, io.open, warn

-- file with time of last performed test
local fname = T and "time-debug.txt" or "time.txt"
local lasttime

if not usertests then
  -- open file with time of last performed test
  local f = io.open(fname)
  if f then
    lasttime = assert(tonumber(f:read'a'))
    f:close();
  else   -- no such file; assume it is recording time for first time
    lasttime = nil
  end
end

-- erase (almost) all globals
print('cleaning all!!!!')
for n in pairs(_G) do
  if not ({___Glob = 1, tostring = 1})[n] then
    _G[n] = undef
  end
end


collectgarbage()
collectgarbage()
collectgarbage()
collectgarbage()
collectgarbage()
collectgarbage();showmem()

local clocktime = clock() - initclock
walltime = difftime(time(), walltime)

print(format("\n\ntotal time: %.2fs (wall time: %gs)\n", clocktime, walltime))

if not usertests then
  lasttime = lasttime or clocktime    -- if no last time, ignore difference
  -- check whether current test time differs more than 5% from last time
  local diff = (clocktime - lasttime) / lasttime
  local tolerance = 0.05    -- 5%
  if (diff >= tolerance or diff <= -tolerance) then
    warn(format("#time difference from previous test: %+.1f%%",
                  diff * 100))
  end
  assert(open(fname, "w")):write(clocktime):close()
end

print("final OK !!!")



--[[
*****************************************************************************
* Copyright (C) 1994-2016 Lua.org, PUC-Rio.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*****************************************************************************
]]
```
## [6.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/6.lua)

```lua
-- $Id: testes/api.lua $
-- See Copyright Notice in file all.lua

if T==nil then
    (Message or print)('\n >>> testC not active: skipping API tests <<<\n')
    return
  end
  
  local debug = require "debug"
  
  local pack = table.pack
  
  
  -- standard error message for memory errors
  local MEMERRMSG = "not enough memory"
  
  local function tcheck (t1, t2)
    assert(t1.n == (t2.n or #t2) + 1)
    for i = 2, t1.n do assert(t1[i] == t2[i - 1]) end
  end
  
  
  local function checkerr (msg, f, ...)
    local stat, err = pcall(f, ...)
    assert(not stat and string.find(err, msg))
  end
  
  
  print('testing C API')
  
  local a = T.testC("pushvalue R; return 1")
  assert(a == debug.getregistry())
  
  
  -- absindex
  assert(T.testC("settop 10; absindex -1; return 1") == 10)
  assert(T.testC("settop 5; absindex -5; return 1") == 1)
  assert(T.testC("settop 10; absindex 1; return 1") == 1)
  assert(T.testC("settop 10; absindex R; return 1") < -10)
  
  -- testing alignment
  a = T.d2s(12458954321123.0)
  assert(a == string.pack("d", 12458954321123.0))
  assert(T.s2d(a) == 12458954321123.0)
  
  local a,b,c = T.testC("pushnum 1; pushnum 2; pushnum 3; return 2")
  assert(a == 2 and b == 3 and not c)
  
  local f = T.makeCfunc("pushnum 1; pushnum 2; pushnum 3; return 2")
  a,b,c = f()
  assert(a == 2 and b == 3 and not c)
  
  -- test that all trues are equal
  a,b,c = T.testC("pushbool 1; pushbool 2; pushbool 0; return 3")
  assert(a == b and a == true and c == false)
  a,b,c = T.testC"pushbool 0; pushbool 10; pushnil;\
                        tobool -3; tobool -3; tobool -3; return 3"
  assert(a==false and b==true and c==false)
  
  
  a,b,c = T.testC("gettop; return 2", 10, 20, 30, 40)
  assert(a == 40 and b == 5 and not c)
  
  local t = pack(T.testC("settop 5; return *", 2, 3))
  tcheck(t, {n=4,2,3})
  
  t = pack(T.testC("settop 0; settop 15; return 10", 3, 1, 23))
  assert(t.n == 10 and t[1] == nil and t[10] == nil)
  
  t = pack(T.testC("remove -2; return *", 2, 3, 4))
  tcheck(t, {n=2,2,4})
  
  t = pack(T.testC("insert -1; return *", 2, 3))
  tcheck(t, {n=2,2,3})
  
  t = pack(T.testC("insert 3; return *", 2, 3, 4, 5))
  tcheck(t, {n=4,2,5,3,4})
  
  t = pack(T.testC("replace 2; return *", 2, 3, 4, 5))
  tcheck(t, {n=3,5,3,4})
  
  t = pack(T.testC("replace -2; return *", 2, 3, 4, 5))
  tcheck(t, {n=3,2,3,5})
  
  t = pack(T.testC("remove 3; return *", 2, 3, 4, 5))
  tcheck(t, {n=3,2,4,5})
  
  t = pack(T.testC("copy 3 4; return *", 2, 3, 4, 5))
  tcheck(t, {n=4,2,3,3,5})
  
  t = pack(T.testC("copy -3 -1; return *", 2, 3, 4, 5))
  tcheck(t, {n=4,2,3,4,3})
  
  do   -- testing 'rotate'
    local t = {10, 20, 30, 40, 50, 60}
    for i = -6, 6 do
      local s = string.format("rotate 2 %d; return 7", i)
      local t1 = pack(T.testC(s, 10, 20, 30, 40, 50, 60))
      tcheck(t1, t)
      table.insert(t, 1, table.remove(t))
    end
  
    t = pack(T.testC("rotate -2 1; return *", 10, 20, 30, 40))
    tcheck(t, {10, 20, 40, 30})
    t = pack(T.testC("rotate -2 -1; return *", 10, 20, 30, 40))
    tcheck(t, {10, 20, 40, 30})
  
    -- some corner cases
    t = pack(T.testC("rotate -1 0; return *", 10, 20, 30, 40))
    tcheck(t, {10, 20, 30, 40})
    t = pack(T.testC("rotate -1 1; return *", 10, 20, 30, 40))
    tcheck(t, {10, 20, 30, 40})
    t = pack(T.testC("rotate 5 -1; return *", 10, 20, 30, 40))
    tcheck(t, {10, 20, 30, 40})
  end
  
  
  -- testing warnings
  T.testC([[
    warningC "#This shold be a"
    warningC " single "
    warning "warning"
    warningC "#This should be "
    warning "another one"
  ]])
  
  
  -- testing message handlers
  do
    local f = T.makeCfunc[[
      getglobal error
      pushstring bola
      pcall 1 1 1   # call 'error' with given handler
      pushstatus
      return 2     # return error message and status
    ]]
  
    local msg, st = f(string.upper)   -- function handler
    assert(st == "ERRRUN" and msg == "BOLA")
    local msg, st = f(string.len)     -- function handler
    assert(st == "ERRRUN" and msg == 4)
  
  end
  
  t = pack(T.testC("insert 3; pushvalue 3; remove 3; pushvalue 2; remove 2; \
                    insert 2; pushvalue 1; remove 1; insert 1; \
        insert -2; pushvalue -2; remove -3; return *",
        2, 3, 4, 5, 10, 40, 90))
  tcheck(t, {n=7,2,3,4,5,10,40,90})
  
  t = pack(T.testC("concat 5; return *", "alo", 2, 3, "joao", 12))
  tcheck(t, {n=1,"alo23joao12"})
  
  -- testing MULTRET
  t = pack(T.testC("call 2,-1; return *",
       function (a,b) return 1,2,3,4,a,b end, "alo", "joao"))
  tcheck(t, {n=6,1,2,3,4,"alo", "joao"})
  
  do  -- test returning more results than fit in the caller stack
    local a = {}
    for i=1,1000 do a[i] = true end; a[999] = 10
    local b = T.testC([[pcall 1 -1 0; pop 1; tostring -1; return 1]],
                      table.unpack, a)
    assert(b == "10")
  end
  
  
  -- testing globals
  _G.AA = 14; _G.BB = "a31"
  local a = {T.testC[[
    getglobal AA;
    getglobal BB;
    getglobal BB;
    setglobal AA;
    return *
  ]]}
  assert(a[2] == 14 and a[3] == "a31" and a[4] == nil and _G.AA == "a31")
  
  _G.AA, _G.BB = nil
  
  -- testing arith
  assert(T.testC("pushnum 10; pushnum 20; arith /; return 1") == 0.5)
  assert(T.testC("pushnum 10; pushnum 20; arith -; return 1") == -10)
  assert(T.testC("pushnum 10; pushnum -20; arith *; return 1") == -200)
  assert(T.testC("pushnum 10; pushnum 3; arith ^; return 1") == 1000)
  assert(T.testC("pushnum 10; pushstring 20; arith /; return 1") == 0.5)
  assert(T.testC("pushstring 10; pushnum 20; arith -; return 1") == -10)
  assert(T.testC("pushstring 10; pushstring -20; arith *; return 1") == -200)
  assert(T.testC("pushstring 10; pushstring 3; arith ^; return 1") == 1000)
  assert(T.testC("arith /; return 1", 2, 0) == 10.0/0)
  a = T.testC("pushnum 10; pushint 3; arith \\; return 1")
  assert(a == 3.0 and math.type(a) == "float")
  a = T.testC("pushint 10; pushint 3; arith \\; return 1")
  assert(a == 3 and math.type(a) == "integer")
  a = assert(T.testC("pushint 10; pushint 3; arith +; return 1"))
  assert(a == 13 and math.type(a) == "integer")
  a = assert(T.testC("pushnum 10; pushint 3; arith +; return 1"))
  assert(a == 13 and math.type(a) == "float")
  a,b,c = T.testC([[pushnum 1;
                    pushstring 10; arith _;
                    pushstring 5; return 3]])
  assert(a == 1 and b == -10 and c == "5")
  local mt = {
        __add = function (a,b) return setmetatable({a[1] + b[1]}, mt) end,
        __mod = function (a,b) return setmetatable({a[1] % b[1]}, mt) end,
        __unm = function (a) return setmetatable({a[1]* 2}, mt) end}
  a,b,c = setmetatable({4}, mt),
          setmetatable({8}, mt),
          setmetatable({-3}, mt)
  local x,y,z = T.testC("arith +; return 2", 10, a, b)
  assert(x == 10 and y[1] == 12 and z == nil)
  assert(T.testC("arith %; return 1", a, c)[1] == 4%-3)
  assert(T.testC("arith _; arith +; arith %; return 1", b, a, c)[1] ==
                 8 % (4 + (-3)*2))
  
  -- errors in arithmetic
  checkerr("divide by zero", T.testC, "arith \\", 10, 0)
  checkerr("%%0", T.testC, "arith %", 10, 0)
  
  
  -- testing lessthan and lessequal
  assert(T.testC("compare LT 2 5, return 1", 3, 2, 2, 4, 2, 2))
  assert(T.testC("compare LE 2 5, return 1", 3, 2, 2, 4, 2, 2))
  assert(not T.testC("compare LT 3 4, return 1", 3, 2, 2, 4, 2, 2))
  assert(T.testC("compare LE 3 4, return 1", 3, 2, 2, 4, 2, 2))
  assert(T.testC("compare LT 5 2, return 1", 4, 2, 2, 3, 2, 2))
  assert(not T.testC("compare LT 2 -3, return 1", "4", "2", "2", "3", "2", "2"))
  assert(not T.testC("compare LT -3 2, return 1", "3", "2", "2", "4", "2", "2"))
  
  -- non-valid indices produce false
  assert(not T.testC("compare LT 1 4, return 1"))
  assert(not T.testC("compare LE 9 1, return 1"))
  assert(not T.testC("compare EQ 9 9, return 1"))
  
  local b = {__lt = function (a,b) return a[1] < b[1] end}
  local a1,a3,a4 = setmetatable({1}, b),
                   setmetatable({3}, b),
                   setmetatable({4}, b)
  assert(T.testC("compare LT 2 5, return 1", a3, 2, 2, a4, 2, 2))
  assert(T.testC("compare LE 2 5, return 1", a3, 2, 2, a4, 2, 2))
  assert(T.testC("compare LT 5 -6, return 1", a4, 2, 2, a3, 2, 2))
  a,b = T.testC("compare LT 5 -6, return 2", a1, 2, 2, a3, 2, 20)
  assert(a == 20 and b == false)
  a,b = T.testC("compare LE 5 -6, return 2", a1, 2, 2, a3, 2, 20)
  assert(a == 20 and b == false)
  a,b = T.testC("compare LE 5 -6, return 2", a1, 2, 2, a1, 2, 20)
  assert(a == 20 and b == true)
  
  
  do  -- testing lessthan and lessequal with metamethods
    local mt = {__lt = function (a,b) return a[1] < b[1] end,
                __le = function (a,b) return a[1] <= b[1] end,
                __eq = function (a,b) return a[1] == b[1] end}
    local function O (x)
      return setmetatable({x}, mt)
    end
  
    local a, b = T.testC("compare LT 2 3; pushint 10; return 2", O(1), O(2))
    assert(a == true and b == 10)
    local a, b = T.testC("compare LE 2 3; pushint 10; return 2", O(3), O(2))
    assert(a == false and b == 10)
    local a, b = T.testC("compare EQ 2 3; pushint 10; return 2", O(3), O(3))
    assert(a == true and b == 10)
  end
  
  -- testing length
  local t = setmetatable({x = 20}, {__len = function (t) return t.x end})
  a,b,c = T.testC([[
     len 2;
     Llen 2;
     objsize 2;
     return 3
  ]], t)
  assert(a == 20 and b == 20 and c == 0)
  
  t.x = "234"; t[1] = 20
  a,b,c = T.testC([[
     len 2;
     Llen 2;
     objsize 2;
     return 3
  ]], t)
  assert(a == "234" and b == 234 and c == 1)
  
  t.x = print; t[1] = 20
  a,c = T.testC([[
     len 2;
     objsize 2;
     return 2
  ]], t)
  assert(a == print and c == 1)
  
  
  -- testing __concat
  
  a = setmetatable({x="u"}, {__concat = function (a,b) return a.x..'.'..b.x end})
  x,y = T.testC([[
    pushnum 5
    pushvalue 2;
    pushvalue 2;
    concat 2;
    pushvalue -2;
    return 2;
  ]], a, a)
  assert(x == a..a and y == 5)
  
  -- concat with 0 elements
  assert(T.testC("concat 0; return 1") == "")
  
  -- concat with 1 element
  assert(T.testC("concat 1; return 1", "xuxu") == "xuxu")
  
  
  
  -- testing lua_is
  
  local function B (x) return x and 1 or 0 end
  
  local function count (x, n)
    n = n or 2
    local prog = [[
      isnumber %d;
      isstring %d;
      isfunction %d;
      iscfunction %d;
      istable %d;
      isuserdata %d;
      isnil %d;
      isnull %d;
      return 8
    ]]
    prog = string.format(prog, n, n, n, n, n, n, n, n)
    local a,b,c,d,e,f,g,h = T.testC(prog, x)
    return B(a)+B(b)+B(c)+B(d)+B(e)+B(f)+B(g)+(100*B(h))
  end
  
  assert(count(3) == 2)
  assert(count('alo') == 1)
  assert(count('32') == 2)
  assert(count({}) == 1)
  assert(count(print) == 2)
  assert(count(function () end) == 1)
  assert(count(nil) == 1)
  assert(count(io.stdin) == 1)
  assert(count(nil, 15) == 100)
  
  
  -- testing lua_to...
  
  local function to (s, x, n)
    n = n or 2
    return T.testC(string.format("%s %d; return 1", s, n), x)
  end
  
  local null = T.pushuserdata(0)
  local hfunc = string.gmatch("", "")    -- a "heavy C function" (with upvalues)
  assert(debug.getupvalue(hfunc, 1))
  assert(to("tostring", {}) == nil)
  assert(to("tostring", "alo") == "alo")
  assert(to("tostring", 12) == "12")
  assert(to("tostring", 12, 3) == nil)
  assert(to("objsize", {}) == 0)
  assert(to("objsize", {1,2,3}) == 3)
  assert(to("objsize", "alo\0\0a") == 6)
  assert(to("objsize", T.newuserdata(0)) == 0)
  assert(to("objsize", T.newuserdata(101)) == 101)
  assert(to("objsize", 124) == 0)
  assert(to("objsize", true) == 0)
  assert(to("tonumber", {}) == 0)
  assert(to("tonumber", "12") == 12)
  assert(to("tonumber", "s2") == 0)
  assert(to("tonumber", 1, 20) == 0)
  assert(to("topointer", 10) == null)
  assert(to("topointer", true) == null)
  assert(to("topointer", nil) == null)
  assert(to("topointer", "abc") ~= null)
  assert(to("topointer", string.rep("x", 10)) ==
         to("topointer", string.rep("x", 10)))    -- short strings
  do    -- long strings
    local s1 = string.rep("x", 300)
    local s2 = string.rep("x", 300)
    assert(to("topointer", s1) ~= to("topointer", s2))
  end
  assert(to("topointer", T.pushuserdata(20)) ~= null)
  assert(to("topointer", io.read) ~= null)           -- light C function
  assert(to("topointer", hfunc) ~= null)        -- "heavy" C function
  assert(to("topointer", function () end) ~= null)   -- Lua function
  assert(to("topointer", io.stdin) ~= null)   -- full userdata
  assert(to("func2num", 20) == 0)
  assert(to("func2num", T.pushuserdata(10)) == 0)
  assert(to("func2num", io.read) ~= 0)     -- light C function
  assert(to("func2num", hfunc) ~= 0)  -- "heavy" C function (with upvalue)
  a = to("tocfunction", math.deg)
  assert(a(3) == math.deg(3) and a == math.deg)
  
  
  print("testing panic function")
  do
    -- trivial error
    assert(T.checkpanic("pushstring hi; error") == "hi")
  
    -- using the stack inside panic
    assert(T.checkpanic("pushstring hi; error;",
      [[checkstack 5 XX
        pushstring ' alo'
        pushstring ' mundo'
        concat 3]]) == "hi alo mundo")
  
    -- "argerror" without frames
    assert(T.checkpanic("loadstring 4") ==
        "bad argument #4 (string expected, got no value)")
  
  
    -- memory error
    T.totalmem(T.totalmem()+10000)   -- set low memory limit (+10k)
    assert(T.checkpanic("newuserdata 20000") == MEMERRMSG)
    T.totalmem(0)          -- restore high limit
  
    -- stack error
    if not _soft then
      local msg = T.checkpanic[[
        pushstring "function f() f() end"
        loadstring -1; call 0 0
        getglobal f; call 0 0
      ]]
      assert(string.find(msg, "stack overflow"))
    end
  
    -- exit in panic still close to-be-closed variables
    assert(T.checkpanic([[
      pushstring "return {__close = function () Y = 'ho'; end}"
      newtable
      loadstring -2
      call 0 1
      setmetatable -2
      toclose -1
      pushstring "hi"
      error
    ]],
    [[
      getglobal Y
      concat 2         # concat original error with global Y
    ]]) == "hiho")
  
  
  end
  
  -- testing deep C stack
  if not _soft then
    print("testing stack overflow")
    collectgarbage("stop")
    checkerr("XXXX", T.testC, "checkstack 1000023 XXXX")   -- too deep
    -- too deep (with no message)
    checkerr("^stack overflow$", T.testC, "checkstack 1000023 ''")
    local s = string.rep("pushnil;checkstack 1 XX;", 1000000)
    checkerr("overflow", T.testC, s)
    collectgarbage("restart")
    print'+'
  end
  
  local lim = _soft and 500 or 12000
  local prog = {"checkstack " .. (lim * 2 + 100) .. "msg", "newtable"}
  for i = 1,lim do
    prog[#prog + 1] = "pushnum " .. i
    prog[#prog + 1] = "pushnum " .. i * 10
  end
  
  prog[#prog + 1] = "rawgeti R 2"   -- get global table in registry
  prog[#prog + 1] = "insert " .. -(2*lim + 2)
  
  for i = 1,lim do
    prog[#prog + 1] = "settable " .. -(2*(lim - i + 1) + 1)
  end
  
  prog[#prog + 1] = "return 2"
  
  prog = table.concat(prog, ";")
  local g, t = T.testC(prog)
  assert(g == _G)
  for i = 1,lim do assert(t[i] == i*10); t[i] = undef end
  assert(next(t) == nil)
  prog, g, t = nil
  
  -- testing errors
  
  a = T.testC([[
    loadstring 2; pcall 0 1 0;
    pushvalue 3; insert -2; pcall 1 1 0;
    pcall 0 0 0;
    return 1
  ]], "XX=150", function (a) assert(a==nil); return 3 end)
  
  assert(type(a) == 'string' and XX == 150)
  _G.XX = nil
  
  local function check3(p, ...)
    local arg = {...}
    assert(#arg == 3)
    assert(string.find(arg[3], p))
  end
  check3(":1:", T.testC("loadstring 2; return *", "x="))
  check3("%.", T.testC("loadfile 2; return *", "."))
  check3("xxxx", T.testC("loadfile 2; return *", "xxxx"))
  
  -- test errors in non protected threads
  local function checkerrnopro (code, msg)
    local th = coroutine.create(function () end)  -- create new thread
    local stt, err = pcall(T.testC, th, code)   -- run code there
    assert(not stt and string.find(err, msg))
  end
  
  if not _soft then
    collectgarbage("stop")   -- avoid __gc with full stack
    checkerrnopro("pushnum 3; call 0 0", "attempt to call")
    print"testing stack overflow in unprotected thread"
    function F () F() end
    checkerrnopro("getglobal 'F'; call 0 0;", "stack overflow")
    F = nil
    collectgarbage("restart")
  end
  print"+"
  
  
  -- testing table access
  
  do   -- getp/setp
    local a = {}
    local a1 = T.testC("rawsetp 2 1; return 1", a, 20)
    assert(a == a1)
    assert(a[T.pushuserdata(1)] == 20)
    local a1, res = T.testC("rawgetp -1 1; return 2", a)
    assert(a == a1 and res == 20)
  end
  
  
  do  -- using the table itself as index
    local a = {}
    a[a] = 10
    local prog = "gettable -1; return *"
    local res = {T.testC(prog, a)}
    assert(#res == 2 and res[1] == prog and res[2] == 10)
  
    local prog = "settable -2; return *"
    local res = {T.testC(prog, a, 20)}
    assert(a[a] == 20)
    assert(#res == 1 and res[1] == prog)
  
    -- raw
    a[a] = 10
    local prog = "rawget -1; return *"
    local res = {T.testC(prog, a)}
    assert(#res == 2 and res[1] == prog and res[2] == 10)
  
    local prog = "rawset -2; return *"
    local res = {T.testC(prog, a, 20)}
    assert(a[a] == 20)
    assert(#res == 1 and res[1] == prog)
  
    -- using the table as the value to set
    local prog = "rawset -1; return *"
    local res = {T.testC(prog, 30, a)}
    assert(a[30] == a)
    assert(#res == 1 and res[1] == prog)
  
    local prog = "settable -1; return *"
    local res = {T.testC(prog, 40, a)}
    assert(a[40] == a)
    assert(#res == 1 and res[1] == prog)
  
    local prog = "rawseti -1 100; return *"
    local res = {T.testC(prog, a)}
    assert(a[100] == a)
    assert(#res == 1 and res[1] == prog)
  
    local prog = "seti -1 200; return *"
    local res = {T.testC(prog, a)}
    assert(a[200] == a)
    assert(#res == 1 and res[1] == prog)
  end
  
  a = {x=0, y=12}
  x, y = T.testC("gettable 2; pushvalue 4; gettable 2; return 2",
                  a, 3, "y", 4, "x")
  assert(x == 0 and y == 12)
  T.testC("settable -5", a, 3, 4, "x", 15)
  assert(a.x == 15)
  a[a] = print
  x = T.testC("gettable 2; return 1", a)  -- table and key are the same object!
  assert(x == print)
  T.testC("settable 2", a, "x")    -- table and key are the same object!
  assert(a[a] == "x")
  
  b = setmetatable({p = a}, {})
  getmetatable(b).__index = function (t, i) return t.p[i] end
  local k, x = T.testC("gettable 3, return 2", 4, b, 20, 35, "x")
  assert(x == 15 and k == 35)
  k = T.testC("getfield 2 y, return 1", b)
  assert(k == 12)
  getmetatable(b).__index = function (t, i) return a[i] end
  getmetatable(b).__newindex = function (t, i,v ) a[i] = v end
  y = T.testC("insert 2; gettable -5; return 1", 2, 3, 4, "y", b)
  assert(y == 12)
  k = T.testC("settable -5, return 1", b, 3, 4, "x", 16)
  assert(a.x == 16 and k == 4)
  a[b] = 'xuxu'
  y = T.testC("gettable 2, return 1", b)
  assert(y == 'xuxu')
  T.testC("settable 2", b, 19)
  assert(a[b] == 19)
  
  --
  do   -- testing getfield/setfield with long keys
    local t = {_012345678901234567890123456789012345678901234567890123456789 = 32}
    local a = T.testC([[
      getfield 2 _012345678901234567890123456789012345678901234567890123456789
      return 1
    ]], t)
    assert(a == 32)
    local a = T.testC([[
      pushnum 33
      setglobal _012345678901234567890123456789012345678901234567890123456789
    ]])
    assert(_012345678901234567890123456789012345678901234567890123456789 == 33)
    _012345678901234567890123456789012345678901234567890123456789 = nil
  end
  
  -- testing next
  a = {}
  t = pack(T.testC("next; return *", a, nil))
  tcheck(t, {n=1,a})
  a = {a=3}
  t = pack(T.testC("next; return *", a, nil))
  tcheck(t, {n=3,a,'a',3})
  t = pack(T.testC("next; pop 1; next; return *", a, nil))
  tcheck(t, {n=1,a})
  
  
  
  -- testing upvalues
  
  do
    local A = T.testC[[ pushnum 10; pushnum 20; pushcclosure 2; return 1]]
    t, b, c = A([[pushvalue U0; pushvalue U1; pushvalue U2; return 3]])
    assert(b == 10 and c == 20 and type(t) == 'table')
    a, b = A([[tostring U3; tonumber U4; return 2]])
    assert(a == nil and b == 0)
    A([[pushnum 100; pushnum 200; replace U2; replace U1]])
    b, c = A([[pushvalue U1; pushvalue U2; return 2]])
    assert(b == 100 and c == 200)
    A([[replace U2; replace U1]], {x=1}, {x=2})
    b, c = A([[pushvalue U1; pushvalue U2; return 2]])
    assert(b.x == 1 and c.x == 2)
    T.checkmemory()
  end
  
  
  -- testing absent upvalues from C-function pointers
  assert(T.testC[[isnull U1; return 1]] == true)
  assert(T.testC[[isnull U100; return 1]] == true)
  assert(T.testC[[pushvalue U1; return 1]] == nil)
  
  local f = T.testC[[ pushnum 10; pushnum 20; pushcclosure 2; return 1]]
  assert(T.upvalue(f, 1) == 10 and
         T.upvalue(f, 2) == 20 and
         T.upvalue(f, 3) == nil)
  T.upvalue(f, 2, "xuxu")
  assert(T.upvalue(f, 2) == "xuxu")
  
  
  -- large closures
  do
    local A = "checkstack 300 msg;" ..
              string.rep("pushnum 10;", 255) ..
              "pushcclosure 255; return 1"
    A = T.testC(A)
    for i=1,255 do
      assert(A(("pushvalue U%d; return 1"):format(i)) == 10)
    end
    assert(A("isnull U256; return 1"))
    assert(not A("isnil U256; return 1"))
  end
  
  
  
  -- testing get/setuservalue
  -- bug in 5.1.2
  checkerr("got number", debug.setuservalue, 3, {})
  checkerr("got nil", debug.setuservalue, nil, {})
  checkerr("got light userdata", debug.setuservalue, T.pushuserdata(1), {})
  
  -- testing multiple user values
  local b = T.newuserdata(0, 10)
  for i = 1, 10 do
    local v, p = debug.getuservalue(b, i)
    assert(v == nil and p)
  end
  do   -- indices out of range
    local v, p = debug.getuservalue(b, -2)
    assert(v == nil and not p)
    local v, p = debug.getuservalue(b, 11)
    assert(v == nil and not p)
  end
  local t = {true, false, 4.56, print, {}, b, "XYZ"}
  for k, v in ipairs(t) do
    debug.setuservalue(b, v, k)
  end
  for k, v in ipairs(t) do
    local v1, p = debug.getuservalue(b, k)
    assert(v1 == v and p)
  end
  
  assert(not debug.getuservalue(4))
  
  debug.setuservalue(b, function () return 10 end, 10)
  collectgarbage()   -- function should not be collected
  assert(debug.getuservalue(b, 10)() == 10)
  
  debug.setuservalue(b, 134)
  collectgarbage()   -- number should not be a problem for collector
  assert(debug.getuservalue(b) == 134)
  
  
  -- test barrier for uservalues
  do
    local oldmode = collectgarbage("incremental")
    T.gcstate("atomic")
    assert(T.gccolor(b) == "black")
    debug.setuservalue(b, {x = 100})
    T.gcstate("pause")  -- complete collection
    assert(debug.getuservalue(b).x == 100)  -- uvalue should be there
    collectgarbage(oldmode)
  end
  
  -- long chain of userdata
  for i = 1, 1000 do
    local bb = T.newuserdata(0, 1)
    debug.setuservalue(bb, b)
    b = bb
  end
  collectgarbage()     -- nothing should not be collected
  for i = 1, 1000 do
    b = debug.getuservalue(b)
  end
  assert(debug.getuservalue(b).x == 100)
  b = nil
  
  
  -- testing locks (refs)
  
  -- reuse of references
  local i = T.ref{}
  T.unref(i)
  assert(T.ref{} == i)
  
  local Arr = {}
  local Lim = 100
  for i=1,Lim do   -- lock many objects
    Arr[i] = T.ref({})
  end
  
  assert(T.ref(nil) == -1 and T.getref(-1) == nil)
  T.unref(-1); T.unref(-1)
  
  for i=1,Lim do   -- unlock all them
    T.unref(Arr[i])
  end
  
  local function printlocks ()
    local f = T.makeCfunc("gettable R; return 1")
    local n = f("n")
    print("n", n)
    for i=0,n do
      print(i, f(i))
    end
  end
  
  
  for i=1,Lim do   -- lock many objects
    Arr[i] = T.ref({})
  end
  
  for i=1,Lim,2 do   -- unlock half of them
    T.unref(Arr[i])
  end
  
  assert(type(T.getref(Arr[2])) == 'table')
  
  
  assert(T.getref(-1) == nil)
  
  
  a = T.ref({})
  
  collectgarbage()
  
  assert(type(T.getref(a)) == 'table')
  
  
  -- colect in cl the `val' of all collected userdata
  local tt = {}
  local cl = {n=0}
  A = nil; B = nil
  local F
  F = function (x)
    local udval = T.udataval(x)
    table.insert(cl, udval)
    local d = T.newuserdata(100)   -- create garbage
    d = nil
    assert(debug.getmetatable(x).__gc == F)
    assert(load("table.insert({}, {})"))()   -- create more garbage
    assert(not collectgarbage())    -- GC during GC (no op)
    local dummy = {}    -- create more garbage during GC
    if A ~= nil then
      assert(type(A) == "userdata")
      assert(T.udataval(A) == B)
      debug.getmetatable(A)    -- just access it
    end
    A = x   -- ressurect userdata
    B = udval
    return 1,2,3
  end
  tt.__gc = F
  
  
  -- test whether udate collection frees memory in the right time
  do
    collectgarbage();
    collectgarbage();
    local x = collectgarbage("count");
    local a = T.newuserdata(5001)
    assert(T.testC("objsize 2; return 1", a) == 5001)
    assert(collectgarbage("count") >= x+4)
    a = nil
    collectgarbage();
    assert(collectgarbage("count") <= x+1)
    -- udata without finalizer
    x = collectgarbage("count")
    collectgarbage("stop")
    for i=1,1000 do T.newuserdata(0) end
    assert(collectgarbage("count") > x+10)
    collectgarbage()
    assert(collectgarbage("count") <= x+1)
    -- udata with finalizer
    collectgarbage()
    x = collectgarbage("count")
    collectgarbage("stop")
    a = {__gc = function () end}
    for i=1,1000 do debug.setmetatable(T.newuserdata(0), a) end
    assert(collectgarbage("count") >= x+10)
    collectgarbage()  -- this collection only calls TM, without freeing memory
    assert(collectgarbage("count") >= x+10)
    collectgarbage()  -- now frees memory
    assert(collectgarbage("count") <= x+1)
    collectgarbage("restart")
  end
  
  
  collectgarbage("stop")
  
  -- create 3 userdatas with tag `tt'
  a = T.newuserdata(0); debug.setmetatable(a, tt); local na = T.udataval(a)
  b = T.newuserdata(0); debug.setmetatable(b, tt); local nb = T.udataval(b)
  c = T.newuserdata(0); debug.setmetatable(c, tt); local nc = T.udataval(c)
  
  -- create userdata without meta table
  x = T.newuserdata(4)
  y = T.newuserdata(0)
  
  checkerr("FILE%* expected, got userdata", io.input, a)
  checkerr("FILE%* expected, got userdata", io.input, x)
  
  assert(debug.getmetatable(x) == nil and debug.getmetatable(y) == nil)
  
  local d = T.ref(a);
  local e = T.ref(b);
  local f = T.ref(c);
  t = {T.getref(d), T.getref(e), T.getref(f)}
  assert(t[1] == a and t[2] == b and t[3] == c)
  
  t=nil; a=nil; c=nil;
  T.unref(e); T.unref(f)
  
  collectgarbage()
  
  -- check that unref objects have been collected
  assert(#cl == 1 and cl[1] == nc)
  
  x = T.getref(d)
  assert(type(x) == 'userdata' and debug.getmetatable(x) == tt)
  x =nil
  tt.b = b  -- create cycle
  tt=nil    -- frees tt for GC
  A = nil
  b = nil
  T.unref(d);
  local n5 = T.newuserdata(0)
  debug.setmetatable(n5, {__gc=F})
  n5 = T.udataval(n5)
  collectgarbage()
  assert(#cl == 4)
  -- check order of collection
  assert(cl[2] == n5 and cl[3] == nb and cl[4] == na)
  
  collectgarbage"restart"
  
  
  a, na = {}, {}
  for i=30,1,-1 do
    a[i] = T.newuserdata(0)
    debug.setmetatable(a[i], {__gc=F})
    na[i] = T.udataval(a[i])
  end
  cl = {}
  a = nil; collectgarbage()
  assert(#cl == 30)
  for i=1,30 do assert(cl[i] == na[i]) end
  na = nil
  
  
  for i=2,Lim,2 do   -- unlock the other half
    T.unref(Arr[i])
  end
  
  x = T.newuserdata(41); debug.setmetatable(x, {__gc=F})
  assert(T.testC("objsize 2; return 1", x) == 41)
  cl = {}
  a = {[x] = 1}
  x = T.udataval(x)
  collectgarbage()
  -- old `x' cannot be collected (`a' still uses it)
  assert(#cl == 0)
  for n in pairs(a) do a[n] = undef end
  collectgarbage()
  assert(#cl == 1 and cl[1] == x)   -- old `x' must be collected
  
  -- testing lua_equal
  assert(T.testC("compare EQ 2 4; return 1", print, 1, print, 20))
  assert(T.testC("compare EQ 3 2; return 1", 'alo', "alo"))
  assert(T.testC("compare EQ 2 3; return 1", nil, nil))
  assert(not T.testC("compare EQ 2 3; return 1", {}, {}))
  assert(not T.testC("compare EQ 2 3; return 1"))
  assert(not T.testC("compare EQ 2 3; return 1", 3))
  
  -- testing lua_equal with fallbacks
  do
    local map = {}
    local t = {__eq = function (a,b) return map[a] == map[b] end}
    local function f(x)
      local u = T.newuserdata(0)
      debug.setmetatable(u, t)
      map[u] = x
      return u
    end
    assert(f(10) == f(10))
    assert(f(10) ~= f(11))
    assert(T.testC("compare EQ 2 3; return 1", f(10), f(10)))
    assert(not T.testC("compare EQ 2 3; return 1", f(10), f(20)))
    t.__eq = nil
    assert(f(10) ~= f(10))
  end
  
  print'+'
  
  
  
  -- testing changing hooks during hooks
  _G.TT = {}
  T.sethook([[
    # set a line hook after 3 count hooks
    sethook 4 0 '
      getglobal TT;
      pushvalue -3; append -2
      pushvalue -2; append -2
    ']], "c", 3)
  local a = 1   -- counting
  a = 1   -- counting
  a = 1   -- count hook (set line hook)
  a = 1   -- line hook
  a = 1   -- line hook
  debug.sethook()
  local t = _G.TT
  assert(t[1] == "line")
  local line = t[2]
  assert(t[3] == "line" and t[4] == line + 1)
  assert(t[5] == "line" and t[6] == line + 2)
  assert(t[7] == nil)
  _G.TT = nil
  
  
  -------------------------------------------------------------------------
  do   -- testing errors during GC
    warn("@off")
    collectgarbage("stop")
    local a = {}
    for i=1,20 do
      a[i] = T.newuserdata(i)   -- creates several udata
    end
    for i=1,20,2 do   -- mark half of them to raise errors during GC
      debug.setmetatable(a[i],
        {__gc = function (x) error("@expected error in gc") end})
    end
    for i=2,20,2 do   -- mark the other half to count and to create more garbage
      debug.setmetatable(a[i], {__gc = function (x) load("A=A+1")() end})
    end
    a = nil
    _G.A = 0
    collectgarbage()
    assert(A == 10)  -- number of normal collections
    collectgarbage("restart")
    warn("@on")
  end
  _G.A = nil
  -------------------------------------------------------------------------
  -- test for userdata vals
  do
    local a = {}; local lim = 30
    for i=0,lim do a[i] = T.pushuserdata(i) end
    for i=0,lim do assert(T.udataval(a[i]) == i) end
    for i=0,lim do assert(T.pushuserdata(i) == a[i]) end
    for i=0,lim do a[a[i]] = i end
    for i=0,lim do a[T.pushuserdata(i)] = i end
    assert(type(tostring(a[1])) == "string")
  end
  
  
  -------------------------------------------------------------------------
  -- testing multiple states
  T.closestate(T.newstate());
  L1 = T.newstate()
  assert(L1)
  
  assert(T.doremote(L1, "X='a'; return 'a'") == 'a')
  
  
  assert(#pack(T.doremote(L1, "function f () return 'alo', 3 end; f()")) == 0)
  
  a, b = T.doremote(L1, "return f()")
  assert(a == 'alo' and b == '3')
  
  T.doremote(L1, "_ERRORMESSAGE = nil")
  -- error: `sin' is not defined
  a, b, c = T.doremote(L1, "return sin(1)")
  assert(a == nil and c == 2)   -- 2 == run-time error
  
  -- error: syntax error
  a, b, c = T.doremote(L1, "return a+")
  assert(a == nil and c == 3 and type(b) == "string")   -- 3 == syntax error
  
  T.loadlib(L1)
  a, b, c = T.doremote(L1, [[
    string = require'string'
    a = require'_G'; assert(a == _G and require("_G") == a)
    io = require'io'; assert(type(io.read) == "function")
    assert(require("io") == io)
    a = require'table'; assert(type(a.insert) == "function")
    a = require'debug'; assert(type(a.getlocal) == "function")
    a = require'math'; assert(type(a.sin) == "function")
    return string.sub('okinama', 1, 2)
  ]])
  assert(a == "ok")
  
  T.closestate(L1);
  
  
  L1 = T.newstate()
  T.loadlib(L1)
  T.doremote(L1, "a = {}")
  T.testC(L1, [[getglobal "a"; pushstring "x"; pushint 1;
               settable -3]])
  assert(T.doremote(L1, "return a.x") == "1")
  
  T.closestate(L1)
  
  L1 = nil
  
  print('+')
  -------------------------------------------------------------------------
  -- testing to-be-closed variables
  -------------------------------------------------------------------------
  print"testing to-be-closed variables"
  
  do
    local openresource = {}
  
    local function newresource ()
      local x = setmetatable({10}, {__close = function(y)
        assert(openresource[#openresource] == y)
        openresource[#openresource] = nil
        y[1] = y[1] + 1
      end})
      openresource[#openresource + 1] = x
      return x
    end
  
    local a, b = T.testC([[
      call 0 1   # create resource
      pushnil
      toclose -2  # mark call result to be closed
      toclose -1  # mark nil to be closed (will be ignored)
      return 2
    ]], newresource)
    assert(a[1] == 11 and b == nil)
    assert(#openresource == 0)    -- was closed
  
    -- repeat the test, but calling function in a 'multret' context
    local a = {T.testC([[
      call 0 1   # create resource
      toclose 2 # mark it to be closed
      return 2
    ]], newresource)}
    assert(type(a[1]) == "string" and a[2][1] == 11)
    assert(#openresource == 0)    -- was closed
  
    -- closing by error
    local a, b = pcall(T.makeCfunc[[
      call 0 1   # create resource
      toclose -1 # mark it to be closed
      error       # resource is the error object
    ]], newresource)
    assert(a == false and b[1] == 11)
    assert(#openresource == 0)    -- was closed
  
    -- non-closable value
    local a, b = pcall(T.makeCfunc[[
      newtable   # create non-closable object
      toclose -1 # mark it to be closed (should raise an error)
      abort  # will not be executed
    ]])
    assert(a == false and
      string.find(b, "non%-closable value"))
  
    local function check (n)
      assert(#openresource == n)
    end
  
    -- closing resources with 'closeslot'
    _ENV.xxx = true
    local a = T.testC([[
      pushvalue 2  # stack: S, NR, CH, NR
      call 0 1   # create resource; stack: S, NR, CH, R
      toclose -1 # mark it to be closed
      pushvalue 2  #  stack: S, NR, CH, R, NR
      call 0 1   # create another resource; stack: S, NR, CH, R, R
      toclose -1 # mark it to be closed
      pushvalue 3  # stack: S, NR, CH, R, R, CH
      pushint 2   # there should be two open resources
      call 1 0  #  stack: S, NR, CH, R, R
      closeslot -1   # close second resource
      pushvalue 3  # stack: S, NR, CH, R, R, CH
      pushint 1   # there should be one open resource
      call 1 0  # stack: S, NR, CH, R, R
      closeslot 4
      setglobal "xxx"  # previous op. erased the slot
      pop 1       # pop other resource from the stack
      pushint *
      return 1    # return stack size
    ]], newresource, check)
    assert(a == 3 and _ENV.xxx == nil)   -- no extra items left in the stack
  
    -- closing resources with 'pop'
    local a = T.testC([[
      pushvalue 2  # stack: S, NR, CH, NR
      call 0 1   # create resource; stack: S, NR, CH, R
      toclose -1 # mark it to be closed
      pushvalue 2  #  stack: S, NR, CH, R, NR
      call 0 1   # create another resource; stack: S, NR, CH, R, R
      toclose -1 # mark it to be closed
      pushvalue 3  # stack: S, NR, CH, R, R, CH
      pushint 2   # there should be two open resources
      call 1 0  #  stack: S, NR, CH, R, R
      pop 1   # pop second resource
      pushvalue 3  # stack: S, NR, CH, R, CH
      pushint 1   # there should be one open resource
      call 1 0  # stack: S, NR, CH, R
      pop 1       # pop other resource from the stack
      pushvalue 3  # stack: S, NR, CH, CH
      pushint 0   # there should be no open resources
      call 1 0  # stack: S, NR, CH
      pushint *
      return 1    # return stack size
    ]], newresource, check)
    assert(a == 3)   -- no extra items left in the stack
  
    -- non-closable value
    local a, b = pcall(T.makeCfunc[[
      pushint 32
      toclose -1
    ]])
    assert(not a and string.find(b, "(C temporary)"))
  
  end
  
  
  --[[
  ** {==================================================================
  ** Testing memory limits
  ** ===================================================================
  --]]
  
  print("memory-allocation errors")
  
  checkerr("block too big", T.newuserdata, math.maxinteger)
  collectgarbage()
  local f = load"local a={}; for i=1,100000 do a[i]=i end"
  T.alloccount(10)
  checkerr(MEMERRMSG, f)
  T.alloccount()          -- remove limit
  
  
  -- test memory errors; increase limit for maximum memory by steps,
  -- o that we get memory errors in all allocations of a given
  -- task, until there is enough memory to complete the task without
  -- errors.
  local function testbytes (s, f)
    collectgarbage()
    local M = T.totalmem()
    local oldM = M
    local a,b = nil
    while true do
      collectgarbage(); collectgarbage()
      T.totalmem(M)
      a, b = T.testC("pcall 0 1 0; pushstatus; return 2", f)
      T.totalmem(0)  -- remove limit
      if a and b == "OK" then break end       -- stop when no more errors
      if b ~= "OK" and b ~= MEMERRMSG then    -- not a memory error?
        error(a, 0)   -- propagate it
      end
      M = M + 7   -- increase memory limit
    end
    print(string.format("minimum memory for %s: %d bytes", s, M - oldM))
    return a
  end
  
  -- test memory errors; increase limit for number of allocations one
  -- by one, so that we get memory errors in all allocations of a given
  -- task, until there is enough allocations to complete the task without
  -- errors.
  
  local function testalloc (s, f)
    collectgarbage()
    local M = 0
    local a,b = nil
    while true do
      collectgarbage(); collectgarbage()
      T.alloccount(M)
      a, b = T.testC("pcall 0 1 0; pushstatus; return 2", f)
      T.alloccount()  -- remove limit
      if a and b == "OK" then break end       -- stop when no more errors
      if b ~= "OK" and b ~= MEMERRMSG then    -- not a memory error?
        error(a, 0)   -- propagate it
      end
      M = M + 1   -- increase allocation limit
    end
    print(string.format("minimum allocations for %s: %d allocations", s, M))
    return a
  end
  
  
  local function testamem (s, f)
    testalloc(s, f)
    return testbytes(s, f)
  end
  
  
  -- doing nothing
  b = testamem("doing nothing", function () return 10 end)
  assert(b == 10)
  
  -- testing memory errors when creating a new state
  
  testamem("state creation", function ()
    local st = T.newstate()
    if st then T.closestate(st) end   -- close new state
    return st
  end)
  
  testamem("empty-table creation", function ()
    return {}
  end)
  
  testamem("string creation", function ()
    return "XXX" .. "YYY"
  end)
  
  testamem("coroutine creation", function()
             return coroutine.create(print)
  end)
  
  
  -- testing to-be-closed variables
  testamem("to-be-closed variables", function()
    local flag
    do
      local x <close> =
                setmetatable({}, {__close = function () flag = true end})
      flag = false
      local x = {}
    end
    return flag
  end)
  
  
  -- testing threads
  
  -- get main thread from registry (at index LUA_RIDX_MAINTHREAD == 1)
  local mt = T.testC("rawgeti R 1; return 1")
  assert(type(mt) == "thread" and coroutine.running() == mt)
  
  
  
  local function expand (n,s)
    if n==0 then return "" end
    local e = string.rep("=", n)
    return string.format("T.doonnewstack([%s[ %s;\n collectgarbage(); %s]%s])\n",
                                e, s, expand(n-1,s), e)
  end
  
  G=0; collectgarbage(); a =collectgarbage("count")
  load(expand(20,"G=G+1"))()
  assert(G==20); collectgarbage();  -- assert(gcinfo() <= a+1)
  G = nil
  
  testamem("running code on new thread", function ()
    return T.doonnewstack("local x=1") == 0  -- try to create thread
  end)
  
  
  -- testing memory x compiler
  
  testamem("loadstring", function ()
    return load("x=1")  -- try to do load a string
  end)
  
  
  local testprog = [[
  local function foo () return end
  local t = {"x"}
  AA = "aaa"
  for i = 1, #t do AA = AA .. t[i] end
  return true
  ]]
  
  -- testing memory x dofile
  _G.AA = nil
  local t =os.tmpname()
  local f = assert(io.open(t, "w"))
  f:write(testprog)
  f:close()
  testamem("dofile", function ()
    local a = loadfile(t)
    return a and a()
  end)
  assert(os.remove(t))
  assert(_G.AA == "aaax")
  
  
  -- other generic tests
  
  testamem("gsub", function ()
    local a, b = string.gsub("alo alo", "(a)", function (x) return x..'b' end)
    return (a == 'ablo ablo')
  end)
  
  testamem("dump/undump", function ()
    local a = load(testprog)
    local b = a and string.dump(a)
    a = b and load(b)
    return a and a()
  end)
  
  _G.AA = nil
  
  local t = os.tmpname()
  testamem("file creation", function ()
    local f = assert(io.open(t, 'w'))
    assert (not io.open"nomenaoexistente")
    io.close(f);
    return not loadfile'nomenaoexistente'
  end)
  assert(os.remove(t))
  
  testamem("table creation", function ()
    local a, lim = {}, 10
    for i=1,lim do a[i] = i; a[i..'a'] = {} end
    return (type(a[lim..'a']) == 'table' and a[lim] == lim)
  end)
  
  testamem("constructors", function ()
    local a = {10, 20, 30, 40, 50; a=1, b=2, c=3, d=4, e=5}
    return (type(a) == 'table' and a.e == 5)
  end)
  
  local a = 1
  local close = nil
  testamem("closure creation", function ()
    function close (b)
     return function (x) return b + x end
    end
    return (close(2)(4) == 6)
  end)
  
  testamem("using coroutines", function ()
    local a = coroutine.wrap(function ()
                coroutine.yield(string.rep("a", 10))
                return {}
              end)
    assert(string.len(a()) == 10)
    return a()
  end)
  
  do   -- auxiliary buffer
    local lim = 100
    local a = {}; for i = 1, lim do a[i] = "01234567890123456789" end
    testamem("auxiliary buffer", function ()
      return (#table.concat(a, ",") == 20*lim + lim - 1)
    end)
  end
  
  testamem("growing stack", function ()
    local function foo (n)
      if n == 0 then return 1 else return 1 + foo(n - 1) end
    end
    return foo(100)
  end)
  
  -- }==================================================================
  
  
  do   -- testing failing in 'lua_checkstack'
    local res = T.testC([[rawcheckstack 500000; return 1]])
    assert(res == false)
    local L = T.newstate()
    T.alloccount(0)   -- will be unable to reallocate the stack
    res = T.testC(L, [[rawcheckstack 5000; return 1]])
    T.alloccount()
    T.closestate(L)
    assert(res == false)
  end
  
  do   -- closing state with no extra memory
    local L = T.newstate()
    T.alloccount(0)
    T.closestate(L)
    T.alloccount()
  end
  
  do   -- garbage collection with no extra memory
    local L = T.newstate()
    T.loadlib(L)
    local res = (T.doremote(L, [[
      _ENV = require"_G"
      local T = require"T"
      local a = {}
      for i = 1, 1000 do a[i] = 'i' .. i end    -- grow string table
      local stsize, stuse = T.querystr()
      assert(stuse > 1000)
      local function foo (n)
        if n > 0 then foo(n - 1) end
      end
      foo(180)    -- grow stack
      local _, stksize = T.stacklevel()
      assert(stksize > 180)
      a = nil
      T.alloccount(0)
      collectgarbage()
      T.alloccount()
      -- stack and string table could not be reallocated,
      -- so they kept their sizes (without errors)
      assert(select(2, T.stacklevel()) == stksize)
      assert(T.querystr() == stsize)
      return 'ok'
    ]]))
    assert(res == 'ok')
    T.closestate(L)
  end
  
  print'+'
  
  -- testing some auxlib functions
  local function gsub (a, b, c)
    a, b = T.testC("gsub 2 3 4; gettop; return 2", a, b, c)
    assert(b == 5)
    return a
  end
  
  assert(gsub("alo.alo.uhuh.", ".", "//") == "alo//alo//uhuh//")
  assert(gsub("alo.alo.uhuh.", "alo", "//") == "//.//.uhuh.")
  assert(gsub("", "alo", "//") == "")
  assert(gsub("...", ".", "/.") == "/././.")
  assert(gsub("...", "...", "") == "")
  
  
  -- testing luaL_newmetatable
  local mt_xuxu, res, top = T.testC("newmetatable xuxu; gettop; return 3")
  assert(type(mt_xuxu) == "table" and res and top == 3)
  local d, res, top = T.testC("newmetatable xuxu; gettop; return 3")
  assert(mt_xuxu == d and not res and top == 3)
  d, res, top = T.testC("newmetatable xuxu1; gettop; return 3")
  assert(mt_xuxu ~= d and res and top == 3)
  
  x = T.newuserdata(0);
  y = T.newuserdata(0);
  T.testC("pushstring xuxu; gettable R; setmetatable 2", x)
  assert(getmetatable(x) == mt_xuxu)
  
  -- testing luaL_testudata
  -- correct metatable
  local res1, res2, top = T.testC([[testudata -1 xuxu
                        testudata 2 xuxu
                    gettop
                    return 3]], x)
  assert(res1 and res2 and top == 4)
  
  -- wrong metatable
  res1, res2, top = T.testC([[testudata -1 xuxu1
                  testudata 2 xuxu1
                  gettop
                  return 3]], x)
  assert(not res1 and not res2 and top == 4)
  
  -- non-existent type
  res1, res2, top = T.testC([[testudata -1 xuxu2
                  testudata 2 xuxu2
                  gettop
                  return 3]], x)
  assert(not res1 and not res2 and top == 4)
  
  -- userdata has no metatable
  res1, res2, top = T.testC([[testudata -1 xuxu
                  testudata 2 xuxu
                  gettop
                  return 3]], y)
  assert(not res1 and not res2 and top == 4)
  
  -- erase metatables
  do
    local r = debug.getregistry()
    assert(r.xuxu == mt_xuxu and r.xuxu1 == d)
    r.xuxu = nil; r.xuxu1 = nil
  end
  
  print'OK'
```
## [7.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/7.lua)

```lua
-- $Id: testes/attrib.lua $
-- See Copyright Notice in file all.lua

print "testing require"

assert(require"string" == string)
assert(require"math" == math)
assert(require"table" == table)
assert(require"io" == io)
assert(require"os" == os)
assert(require"coroutine" == coroutine)

assert(type(package.path) == "string")
assert(type(package.cpath) == "string")
assert(type(package.loaded) == "table")
assert(type(package.preload) == "table")

assert(type(package.config) == "string")
print("package config: "..string.gsub(package.config, "\n", "|"))

do
  -- create a path with 'max' templates,
  -- each with 1-10 repetitions of '?'
  local max = _soft and 100 or 2000
  local t = {}
  for i = 1,max do t[i] = string.rep("?", i%10 + 1) end
  t[#t + 1] = ";"    -- empty template
  local path = table.concat(t, ";")
  -- use that path in a search
  local s, err = package.searchpath("xuxu", path)
  -- search fails; check that message has an occurrence of
  -- '??????????' with ? replaced by xuxu and at least 'max' lines
  assert(not s and
         string.find(err, string.rep("xuxu", 10)) and
         #string.gsub(err, "[^\n]", "") >= max)
  -- path with one very long template
  local path = string.rep("?", max)
  local s, err = package.searchpath("xuxu", path)
  assert(not s and string.find(err, string.rep('xuxu', max)))
end

do
  local oldpath = package.path
  package.path = {}
  local s, err = pcall(require, "no-such-file")
  assert(not s and string.find(err, "package.path"))
  package.path = oldpath
end


do  print"testing 'require' message"
  local oldpath = package.path
  local oldcpath = package.cpath

  package.path = "?.lua;?/?"
  package.cpath = "?.so;?/init"

  local st, msg = pcall(require, 'XXX')

  local expected = [[module 'XXX' not found:
	no field package.preload['XXX']
	no file 'XXX.lua'
	no file 'XXX/XXX'
	no file 'XXX.so'
	no file 'XXX/init']]

  assert(msg == expected)

  package.path = oldpath
  package.cpath = oldcpath
end

print('+')


-- The next tests for 'require' assume some specific directories and
-- libraries.

if not _port then --[

local dirsep = string.match(package.config, "^([^\n]+)\n")

-- auxiliary directory with C modules and temporary files
local DIR = "libs" .. dirsep

-- prepend DIR to a name and correct directory separators
local function D (x)
  local x = string.gsub(x, "/", dirsep)
  return DIR .. x
end

-- prepend DIR and pospend proper C lib. extension to a name
local function DC (x)
  local ext = (dirsep == '\\') and ".dll" or ".so"
  return D(x .. ext)
end


local function createfiles (files, preextras, posextras)
  for n,c in pairs(files) do
    io.output(D(n))
    io.write(string.format(preextras, n))
    io.write(c)
    io.write(string.format(posextras, n))
    io.close(io.output())
  end
end

local function removefiles (files)
  for n in pairs(files) do
    os.remove(D(n))
  end
end

local files = {
  ["names.lua"] = "do return {...} end\n",
  ["err.lua"] = "B = 15; a = a + 1;",
  ["synerr.lua"] = "B =",
  ["A.lua"] = "",
  ["B.lua"] = "assert(...=='B');require 'A'",
  ["A.lc"] = "",
  ["A"] = "",
  ["L"] = "",
  ["XXxX"] = "",
  ["C.lua"] = "package.loaded[...] = 25; require'C'",
}

AA = nil
local extras = [[
NAME = '%s'
REQUIRED = ...
return AA]]

createfiles(files, "", extras)

-- testing explicit "dir" separator in 'searchpath'
assert(package.searchpath("C.lua", D"?", "", "") == D"C.lua")
assert(package.searchpath("C.lua", D"?", ".", ".") == D"C.lua")
assert(package.searchpath("--x-", D"?", "-", "X") == D"XXxX")
assert(package.searchpath("---xX", D"?", "---", "XX") == D"XXxX")
assert(package.searchpath(D"C.lua", "?", dirsep) == D"C.lua")
assert(package.searchpath(".\\C.lua", D"?", "\\") == D"./C.lua")

local oldpath = package.path

package.path = string.gsub("D/?.lua;D/?.lc;D/?;D/??x?;D/L", "D/", DIR)

local try = function (p, n, r, ext)
  NAME = nil
  local rr, x = require(p)
  assert(NAME == n)
  assert(REQUIRED == p)
  assert(rr == r)
  assert(ext == x)
end

local a = require"names"
assert(a[1] == "names" and a[2] == D"names.lua")

local st, msg = pcall(require, "err")
assert(not st and string.find(msg, "arithmetic") and B == 15)
st, msg = pcall(require, "synerr")
assert(not st and string.find(msg, "error loading module"))

assert(package.searchpath("C", package.path) == D"C.lua")
assert(require"C" == 25)
assert(require"C" == 25)
AA = nil
try('B', 'B.lua', true, "libs/B.lua")
assert(package.loaded.B)
assert(require"B" == true)
assert(package.loaded.A)
assert(require"C" == 25)
package.loaded.A = nil
try('B', nil, true, nil)   -- should not reload package
try('A', 'A.lua', true, "libs/A.lua")
package.loaded.A = nil
os.remove(D'A.lua')
AA = {}
try('A', 'A.lc', AA, "libs/A.lc")  -- now must find second option
assert(package.searchpath("A", package.path) == D"A.lc")
assert(require("A") == AA)
AA = false
try('K', 'L', false, "libs/L")     -- default option
try('K', 'L', false, "libs/L")     -- default option (should reload it)
assert(rawget(_G, "_REQUIREDNAME") == nil)

AA = "x"
try("X", "XXxX", AA, "libs/XXxX")


removefiles(files)
NAME, REQUIRED, AA, B = nil


-- testing require of sub-packages

local _G = _G

package.path = string.gsub("D/?.lua;D/?/init.lua", "D/", DIR)

files = {
  ["P1/init.lua"] = "AA = 10",
  ["P1/xuxu.lua"] = "AA = 20",
}

createfiles(files, "_ENV = {}\n", "\nreturn _ENV\n")
AA = 0

local m, ext = assert(require"P1")
assert(ext == "libs/P1/init.lua")
assert(AA == 0 and m.AA == 10)
assert(require"P1" == m)
assert(require"P1" == m)

assert(package.searchpath("P1.xuxu", package.path) == D"P1/xuxu.lua")
m.xuxu, ext = assert(require"P1.xuxu")
assert(AA == 0 and m.xuxu.AA == 20)
assert(ext == "libs/P1/xuxu.lua")
assert(require"P1.xuxu" == m.xuxu)
assert(require"P1.xuxu" == m.xuxu)
assert(require"P1" == m and m.AA == 10)


removefiles(files)
AA = nil

package.path = ""
assert(not pcall(require, "file_does_not_exist"))
package.path = "??\0?"
assert(not pcall(require, "file_does_not_exist1"))

package.path = oldpath

-- check 'require' error message
local fname = "file_does_not_exist2"
local m, err = pcall(require, fname)
for t in string.gmatch(package.path..";"..package.cpath, "[^;]+") do
  t = string.gsub(t, "?", fname)
  assert(string.find(err, t, 1, true))
end

do  -- testing 'package.searchers' not being a table
  local searchers = package.searchers
  package.searchers = 3
  local st, msg = pcall(require, 'a')
  assert(not st and string.find(msg, "must be a table"))
  package.searchers = searchers
end

local function import(...)
  local f = {...}
  return function (m)
    for i=1, #f do m[f[i]] = _G[f[i]] end
  end
end

-- cannot change environment of a C function
assert(not pcall(module, 'XUXU'))



-- testing require of C libraries


local p = ""   -- On Mac OS X, redefine this to "_"

-- check whether loadlib works in this system
local st, err, when = package.loadlib(DC"lib1", "*")
if not st then
  local f, err, when = package.loadlib("donotexist", p.."xuxu")
  assert(not f and type(err) == "string" and when == "absent")
  ;(Message or print)('\n >>> cannot load dynamic library <<<\n')
  print(err, when)
else
  -- tests for loadlib
  local f = assert(package.loadlib(DC"lib1", p.."onefunction"))
  local a, b = f(15, 25)
  assert(a == 25 and b == 15)

  f = assert(package.loadlib(DC"lib1", p.."anotherfunc"))
  assert(f(10, 20) == "10%20\n")

  -- check error messages
  local f, err, when = package.loadlib(DC"lib1", p.."xuxu")
  assert(not f and type(err) == "string" and when == "init")
  f, err, when = package.loadlib("donotexist", p.."xuxu")
  assert(not f and type(err) == "string" and when == "open")

  -- symbols from 'lib1' must be visible to other libraries
  f = assert(package.loadlib(DC"lib11", p.."luaopen_lib11"))
  assert(f() == "exported")

  -- test C modules with prefixes in names
  package.cpath = DC"?"
  local lib2, ext = require"lib2-v2"
  assert(string.find(ext, "libs/lib2-v2", 1, true))
  -- check correct access to global environment and correct
  -- parameters
  assert(_ENV.x == "lib2-v2" and _ENV.y == DC"lib2-v2")
  assert(lib2.id("x") == true)   -- a different "id" implementation

  -- test C submodules
  local fs, ext = require"lib1.sub"
  assert(_ENV.x == "lib1.sub" and _ENV.y == DC"lib1")
  assert(string.find(ext, "libs/lib1", 1, true))
  assert(fs.id(45) == 45)
  _ENV.x, _ENV.y = nil
end

_ENV = _G


-- testing preload

do
  local p = package
  package = {}
  p.preload.pl = function (...)
    local _ENV = {...}
    function xuxu (x) return x+20 end
    return _ENV
  end

  local pl, ext = require"pl"
  assert(require"pl" == pl)
  assert(pl.xuxu(10) == 30)
  assert(pl[1] == "pl" and pl[2] == ":preload:" and ext == ":preload:")

  package = p
  assert(type(package.path) == "string")
end

print('+')

end  --]

print("testing assignments, logical operators, and constructors")

local res, res2 = 27

local a, b = 1, 2+3
assert(a==1 and b==5)
a={}
local function f() return 10, 11, 12 end
a.x, b, a[1] = 1, 2, f()
assert(a.x==1 and b==2 and a[1]==10)
a[f()], b, a[f()+3] = f(), a, 'x'
assert(a[10] == 10 and b == a and a[13] == 'x')

do
  local f = function (n) local x = {}; for i=1,n do x[i]=i end;
                         return table.unpack(x) end;
  local a,b,c
  a,b = 0, f(1)
  assert(a == 0 and b == 1)
  a,b = 0, f(1)
  assert(a == 0 and b == 1)
  a,b,c = 0,5,f(4)
  assert(a==0 and b==5 and c==1)
  a,b,c = 0,5,f(0)
  assert(a==0 and b==5 and c==nil)
end

local a, b, c, d = 1 and nil, 1 or nil, (1 and (nil or 1)), 6
assert(not a and b and c and d==6)

d = 20
a, b, c, d = f()
assert(a==10 and b==11 and c==12 and d==nil)
a,b = f(), 1, 2, 3, f()
assert(a==10 and b==1)

assert(a<b == false and a>b == true)
assert((10 and 2) == 2)
assert((10 or 2) == 10)
assert((10 or assert(nil)) == 10)
assert(not (nil and assert(nil)))
assert((nil or "alo") == "alo")
assert((nil and 10) == nil)
assert((false and 10) == false)
assert((true or 10) == true)
assert((false or 10) == 10)
assert(false ~= nil)
assert(nil ~= false)
assert(not nil == true)
assert(not not nil == false)
assert(not not 1 == true)
assert(not not a == true)
assert(not not (6 or nil) == true)
assert(not not (nil and 56) == false)
assert(not not (nil and true) == false)
assert(not 10 == false)
assert(not {} == false)
assert(not 0.5 == false)
assert(not "x" == false)

assert({} ~= {})
print('+')

a = {}
a[true] = 20
a[false] = 10
assert(a[1<2] == 20 and a[1>2] == 10)

function f(a) return a end

local a = {}
for i=3000,-3000,-1 do a[i + 0.0] = i; end
a[10e30] = "alo"; a[true] = 10; a[false] = 20
assert(a[10e30] == 'alo' and a[not 1] == 20 and a[10<20] == 10)
for i=3000,-3000,-1 do assert(a[i] == i); end
a[print] = assert
a[f] = print
a[a] = a
assert(a[a][a][a][a][print] == assert)
a[print](a[a[f]] == a[print])
assert(not pcall(function () local a = {}; a[nil] = 10 end))
assert(not pcall(function () local a = {[nil] = 10} end))
assert(a[nil] == undef)
a = nil

local a, b, c
a = {10,9,8,7,6,5,4,3,2; [-3]='a', [f]=print, a='a', b='ab'}
a, a.x, a.y = a, a[-3]
assert(a[1]==10 and a[-3]==a.a and a[f]==print and a.x=='a' and not a.y)
a[1], f(a)[2], b, c = {['alo']=assert}, 10, a[1], a[f], 6, 10, 23, f(a), 2
a[1].alo(a[2]==10 and b==10 and c==print)

a.aVeryLongName012345678901234567890123456789012345678901234567890123456789 = 10
local function foo ()
  return a.aVeryLongName012345678901234567890123456789012345678901234567890123456789
end
assert(foo() == 10 and
a.aVeryLongName012345678901234567890123456789012345678901234567890123456789 ==
10)


do
  -- _ENV constant
  local function foo ()
    local _ENV <const> = 11
    X = "hi"
  end
  local st, msg = pcall(foo)
  assert(not st and string.find(msg, "number"))
end


-- test of large float/integer indices 

-- compute maximum integer where all bits fit in a float
local maxint = math.maxinteger

-- trim (if needed) to fit in a float
while maxint ~= (maxint + 0.0) or (maxint - 1) ~= (maxint - 1.0) do
  maxint = maxint // 2
end

local maxintF = maxint + 0.0   -- float version

assert(maxintF == maxint and math.type(maxintF) == "float" and
       maxintF >= 2.0^14)

-- floats and integers must index the same places
a[maxintF] = 10; a[maxintF - 1.0] = 11;
a[-maxintF] = 12; a[-maxintF + 1.0] = 13;

assert(a[maxint] == 10 and a[maxint - 1] == 11 and
       a[-maxint] == 12 and a[-maxint + 1] == 13)

a[maxint] = 20
a[-maxint] = 22

assert(a[maxintF] == 20 and a[maxintF - 1.0] == 11 and
       a[-maxintF] == 22 and a[-maxintF + 1.0] == 13)

a = nil


-- test conflicts in multiple assignment
do
  local a,i,j,b
  a = {'a', 'b'}; i=1; j=2; b=a
  i, a[i], a, j, a[j], a[i+j] = j, i, i, b, j, i
  assert(i == 2 and b[1] == 1 and a == 1 and j == b and b[2] == 2 and
         b[3] == 1)
  a = {}
  local function foo ()    -- assigining to upvalues
    b, a.x, a = a, 10, 20
  end
  foo()
  assert(a == 20 and b.x == 10)
end

-- repeat test with upvalues
do
  local a,i,j,b
  a = {'a', 'b'}; i=1; j=2; b=a
  local function foo ()
    i, a[i], a, j, a[j], a[i+j] = j, i, i, b, j, i
  end
  foo()
  assert(i == 2 and b[1] == 1 and a == 1 and j == b and b[2] == 2 and
         b[3] == 1)
  local t = {}
  (function (a) t[a], a = 10, 20  end)(1);
  assert(t[1] == 10)
end

-- bug in 5.2 beta
local function foo ()
  local a
  return function ()
    local b
    a, b = 3, 14    -- local and upvalue have same index
    return a, b
  end
end

local a, b = foo()()
assert(a == 3 and b == 14)

print('OK')

return res
```
## [8.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/8.lua)

```lua
-- $Id: testes/big.lua $
-- See Copyright Notice in file all.lua

if _soft then
    return 'a'
  end
  
  print "testing large tables"
  
  local debug = require"debug" 
  
  local lim = 2^18 + 1000
  local prog = { "local y = {0" }
  for i = 1, lim do prog[#prog + 1] = i  end
  prog[#prog + 1] = "}\n"
  prog[#prog + 1] = "X = y\n"
  prog[#prog + 1] = ("assert(X[%d] == %d)"):format(lim - 1, lim - 2)
  prog[#prog + 1] = "return 0"
  prog = table.concat(prog, ";")
  
  local env = {string = string, assert = assert}
  local f = assert(load(prog, nil, nil, env))
  
  f()
  assert(env.X[lim] == lim - 1 and env.X[lim + 1] == lim)
  for k in pairs(env) do env[k] = undef end
  
  -- yields during accesses larger than K (in RK)
  setmetatable(env, {
    __index = function (t, n) coroutine.yield('g'); return _G[n] end,
    __newindex = function (t, n, v) coroutine.yield('s'); _G[n] = v end,
  })
  
  X = nil
  local co = coroutine.wrap(f)
  assert(co() == 's')
  assert(co() == 'g')
  assert(co() == 'g')
  assert(co() == 0)
  
  assert(X[lim] == lim - 1 and X[lim + 1] == lim)
  
  -- errors in accesses larger than K (in RK)
  getmetatable(env).__index = function () end
  getmetatable(env).__newindex = function () end
  local e, m = pcall(f)
  assert(not e and m:find("global 'X'"))
  
  -- errors in metamethods 
  getmetatable(env).__newindex = function () error("hi") end
  local e, m = xpcall(f, debug.traceback)
  assert(not e and m:find("'newindex'"))
  
  f, X = nil
  
  coroutine.yield'b'
  
  if 2^32 == 0 then   -- (small integers) {   
  
  print "testing string length overflow"
  
  local repstrings = 192          -- number of strings to be concatenated
  local ssize = math.ceil(2.0^32 / repstrings) + 1   -- size of each string
  
  assert(repstrings * ssize > 2.0^32)  -- it should be larger than maximum size
  
  local longs = string.rep("\0", ssize)   -- create one long string
  
  -- create function to concatenate 'repstrings' copies of its argument
  local rep = assert(load(
    "local a = ...; return " .. string.rep("a", repstrings, "..")))
  
  local a, b = pcall(rep, longs)   -- call that function
  
  -- it should fail without creating string (result would be too large)
  assert(not a and string.find(b, "overflow"))
  
  end   -- }
  
  print'OK'
  
  return 'a'
```
## [9.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/9.lua)

```lua
-- $Id: testes/bitwise.lua $
-- See Copyright Notice in file all.lua

print("testing bitwise operations")

require "bwcoercion"

local numbits = string.packsize('j') * 8

assert(~0 == -1)

assert((1 << (numbits - 1)) == math.mininteger)

-- basic tests for bitwise operators;
-- use variables to avoid constant folding
local a, b, c, d
a = 0xFFFFFFFFFFFFFFFF
assert(a == -1 and a & -1 == a and a & 35 == 35)
a = 0xF0F0F0F0F0F0F0F0
assert(a | -1 == -1)
assert(a ~ a == 0 and a ~ 0 == a and a ~ ~a == -1)
assert(a >> 4 == ~a)
a = 0xF0; b = 0xCC; c = 0xAA; d = 0xFD
assert(a | b ~ c & d == 0xF4)

a = 0xF0.0; b = 0xCC.0; c = "0xAA.0"; d = "0xFD.0"
assert(a | b ~ c & d == 0xF4)

a = 0xF0000000; b = 0xCC000000;
c = 0xAA000000; d = 0xFD000000
assert(a | b ~ c & d == 0xF4000000)
assert(~~a == a and ~a == -1 ~ a and -d == ~d + 1)

a = a << 32
b = b << 32
c = c << 32
d = d << 32
assert(a | b ~ c & d == 0xF4000000 << 32)
assert(~~a == a and ~a == -1 ~ a and -d == ~d + 1)


do   -- constant folding
  local code = string.format("return -1 >> %d", math.maxinteger)
  assert(load(code)() == 0)
  local code = string.format("return -1 >> %d", math.mininteger)
  assert(load(code)() == 0)
  local code = string.format("return -1 << %d", math.maxinteger)
  assert(load(code)() == 0)
  local code = string.format("return -1 << %d", math.mininteger)
  assert(load(code)() == 0)
end

assert(-1 >> 1 == (1 << (numbits - 1)) - 1 and 1 << 31 == 0x80000000)
assert(-1 >> (numbits - 1) == 1)
assert(-1 >> numbits == 0 and
       -1 >> -numbits == 0 and
       -1 << numbits == 0 and
       -1 << -numbits == 0)

assert(1 >> math.mininteger == 0)
assert(1 >> math.maxinteger == 0)
assert(1 << math.mininteger == 0)
assert(1 << math.maxinteger == 0)

assert((2^30 - 1) << 2^30 == 0)
assert((2^30 - 1) >> 2^30 == 0)

assert(1 >> -3 == 1 << 3 and 1000 >> 5 == 1000 << -5)


-- coercion from strings to integers
assert("0xffffffffffffffff" | 0 == -1)
assert("0xfffffffffffffffe" & "-1" == -2)
assert(" \t-0xfffffffffffffffe\n\t" & "-1" == 2)
assert("   \n  -45  \t " >> "  -2  " == -45 * 4)
assert("1234.0" << "5.0" == 1234 * 32)
assert("0xffff.0" ~ "0xAAAA" == 0x5555)
assert(~"0x0.000p4" == -1)

assert(("7" .. 3) << 1 == 146)
assert(0xffffffff >> (1 .. "9") == 0x1fff)
assert(10 | (1 .. "9") == 27)

do
  local st, msg = pcall(function () return 4 & "a" end)
  assert(string.find(msg, "'band'"))

  local st, msg = pcall(function () return ~"a" end)
  assert(string.find(msg, "'bnot'"))
end


-- out of range number
assert(not pcall(function () return "0xffffffffffffffff.0" | 0 end))

-- embedded zeros
assert(not pcall(function () return "0xffffffffffffffff\0" | 0 end))

print'+'


package.preload.bit32 = function ()     --{

-- no built-in 'bit32' library: implement it using bitwise operators

local bit = {}

function bit.bnot (a)
  return ~a & 0xFFFFFFFF
end


--
-- in all vararg functions, avoid creating 'arg' table when there are
-- only 2 (or less) parameters, as 2 parameters is the common case
--

function bit.band (x, y, z, ...)
  if not z then
    return ((x or -1) & (y or -1)) & 0xFFFFFFFF
  else
    local arg = {...}
    local res = x & y & z
    for i = 1, #arg do res = res & arg[i] end
    return res & 0xFFFFFFFF
  end
end

function bit.bor (x, y, z, ...)
  if not z then
    return ((x or 0) | (y or 0)) & 0xFFFFFFFF
  else
    local arg = {...}
    local res = x | y | z
    for i = 1, #arg do res = res | arg[i] end
    return res & 0xFFFFFFFF
  end
end

function bit.bxor (x, y, z, ...)
  if not z then
    return ((x or 0) ~ (y or 0)) & 0xFFFFFFFF
  else
    local arg = {...}
    local res = x ~ y ~ z
    for i = 1, #arg do res = res ~ arg[i] end
    return res & 0xFFFFFFFF
  end
end

function bit.btest (...)
  return bit.band(...) ~= 0
end

function bit.lshift (a, b)
  return ((a & 0xFFFFFFFF) << b) & 0xFFFFFFFF
end

function bit.rshift (a, b)
  return ((a & 0xFFFFFFFF) >> b) & 0xFFFFFFFF
end

function bit.arshift (a, b)
  a = a & 0xFFFFFFFF
  if b <= 0 or (a & 0x80000000) == 0 then
    return (a >> b) & 0xFFFFFFFF
  else
    return ((a >> b) | ~(0xFFFFFFFF >> b)) & 0xFFFFFFFF
  end
end

function bit.lrotate (a ,b)
  b = b & 31
  a = a & 0xFFFFFFFF
  a = (a << b) | (a >> (32 - b))
  return a & 0xFFFFFFFF
end

function bit.rrotate (a, b)
  return bit.lrotate(a, -b)
end

local function checkfield (f, w)
  w = w or 1
  assert(f >= 0, "field cannot be negative")
  assert(w > 0, "width must be positive")
  assert(f + w <= 32, "trying to access non-existent bits")
  return f, ~(-1 << w)
end

function bit.extract (a, f, w)
  local f, mask = checkfield(f, w)
  return (a >> f) & mask
end

function bit.replace (a, v, f, w)
  local f, mask = checkfield(f, w)
  v = v & mask
  a = (a & ~(mask << f)) | (v << f)
  return a & 0xFFFFFFFF
end

return bit

end  --}


print("testing bitwise library")

local bit32 = require'bit32'

assert(bit32.band() == bit32.bnot(0))
assert(bit32.btest() == true)
assert(bit32.bor() == 0)
assert(bit32.bxor() == 0)

assert(bit32.band() == bit32.band(0xffffffff))
assert(bit32.band(1,2) == 0)


-- out-of-range numbers
assert(bit32.band(-1) == 0xffffffff)
assert(bit32.band((1 << 33) - 1) == 0xffffffff)
assert(bit32.band(-(1 << 33) - 1) == 0xffffffff)
assert(bit32.band((1 << 33) + 1) == 1)
assert(bit32.band(-(1 << 33) + 1) == 1)
assert(bit32.band(-(1 << 40)) == 0)
assert(bit32.band(1 << 40) == 0)
assert(bit32.band(-(1 << 40) - 2) == 0xfffffffe)
assert(bit32.band((1 << 40) - 4) == 0xfffffffc)

assert(bit32.lrotate(0, -1) == 0)
assert(bit32.lrotate(0, 7) == 0)
assert(bit32.lrotate(0x12345678, 0) == 0x12345678)
assert(bit32.lrotate(0x12345678, 32) == 0x12345678)
assert(bit32.lrotate(0x12345678, 4) == 0x23456781)
assert(bit32.rrotate(0x12345678, -4) == 0x23456781)
assert(bit32.lrotate(0x12345678, -8) == 0x78123456)
assert(bit32.rrotate(0x12345678, 8) == 0x78123456)
assert(bit32.lrotate(0xaaaaaaaa, 2) == 0xaaaaaaaa)
assert(bit32.lrotate(0xaaaaaaaa, -2) == 0xaaaaaaaa)
for i = -50, 50 do
  assert(bit32.lrotate(0x89abcdef, i) == bit32.lrotate(0x89abcdef, i%32))
end

assert(bit32.lshift(0x12345678, 4) == 0x23456780)
assert(bit32.lshift(0x12345678, 8) == 0x34567800)
assert(bit32.lshift(0x12345678, -4) == 0x01234567)
assert(bit32.lshift(0x12345678, -8) == 0x00123456)
assert(bit32.lshift(0x12345678, 32) == 0)
assert(bit32.lshift(0x12345678, -32) == 0)
assert(bit32.rshift(0x12345678, 4) == 0x01234567)
assert(bit32.rshift(0x12345678, 8) == 0x00123456)
assert(bit32.rshift(0x12345678, 32) == 0)
assert(bit32.rshift(0x12345678, -32) == 0)
assert(bit32.arshift(0x12345678, 0) == 0x12345678)
assert(bit32.arshift(0x12345678, 1) == 0x12345678 // 2)
assert(bit32.arshift(0x12345678, -1) == 0x12345678 * 2)
assert(bit32.arshift(-1, 1) == 0xffffffff)
assert(bit32.arshift(-1, 24) == 0xffffffff)
assert(bit32.arshift(-1, 32) == 0xffffffff)
assert(bit32.arshift(-1, -1) == bit32.band(-1 * 2, 0xffffffff))

assert(0x12345678 << 4 == 0x123456780)
assert(0x12345678 << 8 == 0x1234567800)
assert(0x12345678 << -4 == 0x01234567)
assert(0x12345678 << -8 == 0x00123456)
assert(0x12345678 << 32 == 0x1234567800000000)
assert(0x12345678 << -32 == 0)
assert(0x12345678 >> 4 == 0x01234567)
assert(0x12345678 >> 8 == 0x00123456)
assert(0x12345678 >> 32 == 0)
assert(0x12345678 >> -32 == 0x1234567800000000)

print("+")
-- some special cases
local c = {0, 1, 2, 3, 10, 0x80000000, 0xaaaaaaaa, 0x55555555,
           0xffffffff, 0x7fffffff}

for _, b in pairs(c) do
  assert(bit32.band(b) == b)
  assert(bit32.band(b, b) == b)
  assert(bit32.band(b, b, b, b) == b)
  assert(bit32.btest(b, b) == (b ~= 0))
  assert(bit32.band(b, b, b) == b)
  assert(bit32.band(b, b, b, ~b) == 0)
  assert(bit32.btest(b, b, b) == (b ~= 0))
  assert(bit32.band(b, bit32.bnot(b)) == 0)
  assert(bit32.bor(b, bit32.bnot(b)) == bit32.bnot(0))
  assert(bit32.bor(b) == b)
  assert(bit32.bor(b, b) == b)
  assert(bit32.bor(b, b, b) == b)
  assert(bit32.bor(b, b, 0, ~b) == 0xffffffff)
  assert(bit32.bxor(b) == b)
  assert(bit32.bxor(b, b) == 0)
  assert(bit32.bxor(b, b, b) == b)
  assert(bit32.bxor(b, b, b, b) == 0)
  assert(bit32.bxor(b, 0) == b)
  assert(bit32.bnot(b) ~= b)
  assert(bit32.bnot(bit32.bnot(b)) == b)
  assert(bit32.bnot(b) == (1 << 32) - 1 - b)
  assert(bit32.lrotate(b, 32) == b)
  assert(bit32.rrotate(b, 32) == b)
  assert(bit32.lshift(bit32.lshift(b, -4), 4) == bit32.band(b, bit32.bnot(0xf)))
  assert(bit32.rshift(bit32.rshift(b, 4), -4) == bit32.band(b, bit32.bnot(0xf)))
end

-- for this test, use at most 24 bits (mantissa of a single float)
c = {0, 1, 2, 3, 10, 0x800000, 0xaaaaaa, 0x555555, 0xffffff, 0x7fffff}
for _, b in pairs(c) do
  for i = -40, 40 do
    local x = bit32.lshift(b, i)
    local y = math.floor(math.fmod(b * 2.0^i, 2.0^32))
    assert(math.fmod(x - y, 2.0^32) == 0)
  end
end

assert(not pcall(bit32.band, {}))
assert(not pcall(bit32.bnot, "a"))
assert(not pcall(bit32.lshift, 45))
assert(not pcall(bit32.lshift, 45, print))
assert(not pcall(bit32.rshift, 45, print))

print("+")


-- testing extract/replace

assert(bit32.extract(0x12345678, 0, 4) == 8)
assert(bit32.extract(0x12345678, 4, 4) == 7)
assert(bit32.extract(0xa0001111, 28, 4) == 0xa)
assert(bit32.extract(0xa0001111, 31, 1) == 1)
assert(bit32.extract(0x50000111, 31, 1) == 0)
assert(bit32.extract(0xf2345679, 0, 32) == 0xf2345679)

assert(not pcall(bit32.extract, 0, -1))
assert(not pcall(bit32.extract, 0, 32))
assert(not pcall(bit32.extract, 0, 0, 33))
assert(not pcall(bit32.extract, 0, 31, 2))

assert(bit32.replace(0x12345678, 5, 28, 4) == 0x52345678)
assert(bit32.replace(0x12345678, 0x87654321, 0, 32) == 0x87654321)
assert(bit32.replace(0, 1, 2) == 2^2)
assert(bit32.replace(0, -1, 4) == 2^4)
assert(bit32.replace(-1, 0, 31) == (1 << 31) - 1)
assert(bit32.replace(-1, 0, 1, 2) == (1 << 32) - 7)


-- testing conversion of floats

assert(bit32.bor(3.0) == 3)
assert(bit32.bor(-4.0) == 0xfffffffc)

-- large floats and large-enough integers?
if 2.0^50 < 2.0^50 + 1.0 and 2.0^50 < (-1 >> 1) then
  assert(bit32.bor(2.0^32 - 5.0) == 0xfffffffb)
  assert(bit32.bor(-2.0^32 - 6.0) == 0xfffffffa)
  assert(bit32.bor(2.0^48 - 5.0) == 0xfffffffb)
  assert(bit32.bor(-2.0^48 - 6.0) == 0xfffffffa)
end

print'OK'
```
## [10.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/10.lua)

```lua
-- BUG: built in function 无法识别

local tonumber, tointeger = tonumber, math.tointeger
local type, getmetatable, rawget, error = type, getmetatable, rawget, error
local strsub = string.sub

local print = print

_ENV = nil

-- Try to convert a value to an integer, without assuming any coercion.
local function toint (x)
  x = tonumber(x)   -- handle numerical strings
  if not x then
    return false    -- not coercible to a number
  end
  return tointeger(x)
end


-- If operation fails, maybe second operand has a metamethod that should
-- have been called if not for this string metamethod, so try to
-- call it.
local function trymt (x, y, mtname)
  if type(y) ~= "string" then    -- avoid recalling original metamethod
    local mt = getmetatable(y)
    local mm = mt and rawget(mt, mtname)
    if mm then
      return mm(x, y)
    end
  end
  -- if any test fails, there is no other metamethod to be called
  error("attempt to '" .. strsub(mtname, 3) ..
        "' a " .. type(x) .. " with a " .. type(y), 4)
end


local function checkargs (x, y, mtname)
  local xi = toint(x)
  local yi = toint(y)
  if xi and yi then
    return xi, yi
  else
    return trymt(x, y, mtname), nil
  end
end


local smt = getmetatable("")

smt.__band = function (x, y)
  local x, y = checkargs(x, y, "__band")
  return y and x & y or x
end

smt.__bor = function (x, y)
  local x, y = checkargs(x, y, "__bor")
  return y and x | y or x
end

smt.__bxor = function (x, y)
  local x, y = checkargs(x, y, "__bxor")
  return y and x ~ y or x
end

smt.__shl = function (x, y)
  local x, y = checkargs(x, y, "__shl")
  return y and x << y or x
end

smt.__shr = function (x, y)
  local x, y = checkargs(x, y, "__shr")
  return y and x >> y or x
end

smt.__bnot = function (x)
  local x, y = checkargs(x, x, "__bnot")
  return y and ~x or x
end
```
## [11.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/11.lua)

```lua
-- $Id: testes/calls.lua $
-- See Copyright Notice in file all.lua

print("testing functions and calls")

local debug = require "debug"

-- get the opportunity to test 'type' too ;)

assert(type(1<2) == 'boolean')
assert(type(true) == 'boolean' and type(false) == 'boolean')
assert(type(nil) == 'nil'
   and type(-3) == 'number'
   and type'x' == 'string'
   and type{} == 'table'
   and type(type) == 'function')

assert(type(assert) == type(print))
local function f (x) return a:x (x) end
assert(type(f) == 'function')
assert(not pcall(type))


-- testing local-function recursion
fact = false
do
  local res = 1
  local function fact (n)
    if n==0 then return res
    else return n*fact(n-1)
    end
  end
  assert(fact(5) == 120)
end
assert(fact == false)
fact = nil

-- testing declarations
local a = {i = 10}
local self = 20
function a:x (x) return x+self.i end
function a.y (x) return x+self end

assert(a:x(1)+10 == a.y(1))

a.t = {i=-100}
a["t"].x = function (self, a,b) return self.i+a+b end

assert(a.t:x(2,3) == -95)

do
  local a = {x=0}
  function a:add (x) self.x, a.y = self.x+x, 20; return self end
  assert(a:add(10):add(20):add(30).x == 60 and a.y == 20)
end

local a = {b={c={}}}

function a.b.c.f1 (x) return x+1 end
function a.b.c:f2 (x,y) self[x] = y end
assert(a.b.c.f1(4) == 5)
a.b.c:f2('k', 12); assert(a.b.c.k == 12)

print('+')

t = nil   -- 'declare' t
function f(a,b,c) local d = 'a'; t={a,b,c,d} end

f(      -- this line change must be valid
  1,2)
assert(t[1] == 1 and t[2] == 2 and t[3] == nil and t[4] == 'a')
f(1,2,   -- this one too
      3,4)
assert(t[1] == 1 and t[2] == 2 and t[3] == 3 and t[4] == 'a')

t = nil   -- delete 't'

function fat(x)
  if x <= 1 then return 1
  else return x*load("return fat(" .. x-1 .. ")", "")()
  end
end

assert(load "load 'assert(fat(6)==720)' () ")()
a = load('return fat(5), 3')
local a,b = a()
assert(a == 120 and b == 3)
fat = nil
print('+')

local function err_on_n (n)
  if n==0 then error(); exit(1);
  else err_on_n (n-1); exit(1);
  end
end

do
  local function dummy (n)
    if n > 0 then
      assert(not pcall(err_on_n, n))
      dummy(n-1)
    end
  end

  dummy(10)
end

_G.deep = nil   -- "declaration"  (used by 'all.lua')

function deep (n)
  if n>0 then deep(n-1) end
end
deep(10)
deep(180)


print"testing tail calls"

function deep (n) if n>0 then return deep(n-1) else return 101 end end
assert(deep(30000) == 101)
a = {}
function a:deep (n) if n>0 then return self:deep(n-1) else return 101 end end
assert(a:deep(30000) == 101)

do   -- tail calls x varargs
  local function foo (x, ...) local a = {...}; return x, a[1], a[2] end

  local function foo1 (x) return foo(10, x, x + 1) end

  local a, b, c = foo1(-2)
  assert(a == 10 and b == -2 and c == -1)

  -- tail calls x metamethods
  local t = setmetatable({}, {__call = foo})
  local function foo2 (x) return t(10, x) end
  a, b, c = foo2(100)
  assert(a == t and b == 10 and c == 100)

  a, b = (function () return foo() end)()
  assert(a == nil and b == nil)

  local X, Y, A
  local function foo (x, y, ...) X = x; Y = y; A = {...} end
  local function foo1 (...) return foo(...) end

  local a, b, c = foo1()
  assert(X == nil and Y == nil and #A == 0)

  a, b, c = foo1(10)
  assert(X == 10 and Y == nil and #A == 0)

  a, b, c = foo1(10, 20)
  assert(X == 10 and Y == 20 and #A == 0)

  a, b, c = foo1(10, 20, 30)
  assert(X == 10 and Y == 20 and #A == 1 and A[1] == 30)
end


do   -- C-stack overflow while handling C-stack overflow
  local function loop ()
    assert(pcall(loop))
  end

  local err, msg = xpcall(loop, loop)
  assert(not err and string.find(msg, "error"))
end



do   -- tail calls x chain of __call
  local n = 10000   -- depth

  local function foo ()
    if n == 0 then return 1023
    else n = n - 1; return foo()
    end
  end

  -- build a chain of __call metamethods ending in function 'foo'
  for i = 1, 100 do
    foo = setmetatable({}, {__call = foo})
  end

  -- call the first one as a tail call in a new coroutine
  -- (to ensure stack is not preallocated)
  assert(coroutine.wrap(function() return foo() end)() == 1023)
end

print('+')


do  -- testing chains of '__call'
  local N = 20
  local u = table.pack
  for i = 1, N do
    u = setmetatable({i}, {__call = u})
  end

  local Res = u("a", "b", "c")

  assert(Res.n == N + 3)
  for i = 1, N do
    assert(Res[i][1] == i)
  end
  assert(Res[N + 1] == "a" and Res[N + 2] == "b" and Res[N + 3] == "c")
end


a = nil
(function (x) a=x end)(23)
assert(a == 23 and (function (x) return x*2 end)(20) == 40)


-- testing closures

-- fixed-point operator
local Z = function (le)
      local function a (f)
        return le(function (x) return f(f)(x) end)
      end
      return a(a)
    end


-- non-recursive factorial

local F = function (f)
      return function (n)
               if n == 0 then return 1
               else return n*f(n-1) end
             end
    end

local fat = Z(F)

assert(fat(0) == 1 and fat(4) == 24 and Z(F)(5)==5*Z(F)(4))

local function g (z)
  local function f (a,b,c,d)
    return function (x,y) return a+b+c+d+a+x+y+z end
  end
  return f(z,z+1,z+2,z+3)
end

local f = g(10)
assert(f(9, 16) == 10+11+12+13+10+9+16+10)

print('+')

-- testing multiple returns

local function unlpack (t, i)
  i = i or 1
  if (i <= #t) then
    return t[i], unlpack(t, i+1)
  end
end

local function equaltab (t1, t2)
  assert(#t1 == #t2)
  for i = 1, #t1 do
    assert(t1[i] == t2[i])
  end
end

local pack = function (...) return (table.pack(...)) end

local function f() return 1,2,30,4 end
local function ret2 (a,b) return a,b end

local a,b,c,d = unlpack{1,2,3}
assert(a==1 and b==2 and c==3 and d==nil)
a = {1,2,3,4,false,10,'alo',false,assert}
equaltab(pack(unlpack(a)), a)
equaltab(pack(unlpack(a), -1), {1,-1})
a,b,c,d = ret2(f()), ret2(f())
assert(a==1 and b==1 and c==2 and d==nil)
a,b,c,d = unlpack(pack(ret2(f()), ret2(f())))
assert(a==1 and b==1 and c==2 and d==nil)
a,b,c,d = unlpack(pack(ret2(f()), (ret2(f()))))
assert(a==1 and b==1 and c==nil and d==nil)

a = ret2{ unlpack{1,2,3}, unlpack{3,2,1}, unlpack{"a", "b"}}
assert(a[1] == 1 and a[2] == 3 and a[3] == "a" and a[4] == "b")


-- testing calls with 'incorrect' arguments
rawget({}, "x", 1)
rawset({}, "x", 1, 2)
assert(math.sin(1,2) == math.sin(1))
table.sort({10,9,8,4,19,23,0,0}, function (a,b) return a<b end, "extra arg")


-- test for generic load
local x = "-- a comment\0\0\0\n  x = 10 + \n23; \
     local a = function () x = 'hi' end; \
     return '\0'"
local function read1 (x)
  local i = 0
  return function ()
    collectgarbage()
    i=i+1
    return string.sub(x, i, i)
  end
end

local function cannotload (msg, a,b)
  assert(not a and string.find(b, msg))
end

a = assert(load(read1(x), "modname", "t", _G))
assert(a() == "\0" and _G.x == 33)
assert(debug.getinfo(a).source == "modname")
-- cannot read text in binary mode
cannotload("attempt to load a text chunk", load(read1(x), "modname", "b", {}))
cannotload("attempt to load a text chunk", load(x, "modname", "b"))

a = assert(load(function () return nil end))
a()  -- empty chunk

assert(not load(function () return true end))


-- small bug
local t = {nil, "return ", "3"}
f, msg = load(function () return table.remove(t, 1) end)
assert(f() == nil)   -- should read the empty chunk

-- another small bug (in 5.2.1)
f = load(string.dump(function () return 1 end), nil, "b", {})
assert(type(f) == "function" and f() == 1)


do   -- another bug (in 5.4.0)
  -- loading a binary long string interrupted by GC cycles
  local f = string.dump(function ()
    return '01234567890123456789012345678901234567890123456789'
  end)
  f = load(read1(f))
  assert(f() == '01234567890123456789012345678901234567890123456789')
end


do   -- another bug (since 5.2)
  -- corrupted binary dump: list of upvalue names is larger than number
  -- of upvalues, overflowing the array of upvalues.
  local code =
   "\x1b\x4c\x75\x61\x54\x00\x19\x93\x0d\x0a\x1a\x0a\x04\x08\x08\x78\x56\z
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x28\x77\x40\x00\x86\x40\z
    \x74\x65\x6d\x70\x81\x81\x01\x00\x02\x82\x48\x00\x02\x00\xc7\x00\x01\z
    \x00\x80\x80\x80\x82\x00\x00\x80\x81\x82\x78\x80\x82\x81\x86\x40\x74\z
    \x65\x6d\x70"

  assert(load(code))   -- segfaults in previous versions
end


x = string.dump(load("x = 1; return x"))
a = assert(load(read1(x), nil, "b"))
assert(a() == 1 and _G.x == 1)
cannotload("attempt to load a binary chunk", load(read1(x), nil, "t"))
cannotload("attempt to load a binary chunk", load(x, nil, "t"))
_G.x = nil

assert(not pcall(string.dump, print))  -- no dump of C functions

cannotload("unexpected symbol", load(read1("*a = 123")))
cannotload("unexpected symbol", load("*a = 123"))
cannotload("hhi", load(function () error("hhi") end))

-- any value is valid for _ENV
assert(load("return _ENV", nil, nil, 123)() == 123)


-- load when _ENV is not first upvalue
local x; XX = 123
local function h ()
  local y=x   -- use 'x', so that it becomes 1st upvalue
  return XX   -- global name
end
local d = string.dump(h)
x = load(d, "", "b")
assert(debug.getupvalue(x, 2) == '_ENV')
debug.setupvalue(x, 2, _G)
assert(x() == 123)

assert(assert(load("return XX + ...", nil, nil, {XX = 13}))(4) == 17)
XX = nil

-- test generic load with nested functions
x = [[
  return function (x)
    return function (y)
     return function (z)
       return x+y+z
     end
   end
  end
]]
a = assert(load(read1(x), "read", "t"))
assert(a()(2)(3)(10) == 15)

-- repeat the test loading a binary chunk
x = string.dump(a)
a = assert(load(read1(x), "read", "b"))
assert(a()(2)(3)(10) == 15)


-- test for dump/undump with upvalues
local a, b = 20, 30
x = load(string.dump(function (x)
  if x == "set" then a = 10+b; b = b+1 else
  return a
  end
end), "", "b", nil)
assert(x() == nil)
assert(debug.setupvalue(x, 1, "hi") == "a")
assert(x() == "hi")
assert(debug.setupvalue(x, 2, 13) == "b")
assert(not debug.setupvalue(x, 3, 10))   -- only 2 upvalues
x("set")
assert(x() == 23)
x("set")
assert(x() == 24)

-- test for dump/undump with many upvalues
do
  local nup = 200    -- maximum number of local variables
  local prog = {"local a1"}
  for i = 2, nup do prog[#prog + 1] = ", a" .. i end
  prog[#prog + 1] = " = 1"
  for i = 2, nup do prog[#prog + 1] = ", " .. i end
  local sum = 1
  prog[#prog + 1] = "; return function () return a1"
  for i = 2, nup do prog[#prog + 1] = " + a" .. i; sum = sum + i end
  prog[#prog + 1] = " end"
  prog = table.concat(prog)
  local f = assert(load(prog))()
  assert(f() == sum)

  f = load(string.dump(f))   -- main chunk now has many upvalues
  local a = 10
  local h = function () return a end
  for i = 1, nup do
    debug.upvaluejoin(f, i, h, 1)
  end
  assert(f() == 10 * nup)
end

-- test for long method names
do
  local t = {x = 1}
  function t:_012345678901234567890123456789012345678901234567890123456789 ()
    return self.x
  end
  assert(t:_012345678901234567890123456789012345678901234567890123456789() == 1)
end


-- test for bug in parameter adjustment
assert((function () return nil end)(4) == nil)
assert((function () local a; return a end)(4) == nil)
assert((function (a) return a end)() == nil)


print("testing binary chunks")
do
  local header = string.pack("c4BBc6BBB",
    "\27Lua",                                  -- signature
    0x54,                                      -- version 5.4 (0x54)
    0,                                         -- format
    "\x19\x93\r\n\x1a\n",                      -- data
    4,                                         -- size of instruction
    string.packsize("j"),                      -- sizeof(lua integer)
    string.packsize("n")                       -- sizeof(lua number)
  )
  local c = string.dump(function ()
    local a = 1; local b = 3;
    local f = function () return a + b + _ENV.c; end    -- upvalues
    local s1 = "a constant"
    local s2 = "another constant"
    return a + b * 3
  end)

  assert(assert(load(c))() == 10)

  -- check header
  assert(string.sub(c, 1, #header) == header)
  -- check LUAC_INT and LUAC_NUM
  local ci, cn = string.unpack("jn", c, #header + 1)
  assert(ci == 0x5678 and cn == 370.5)

  -- corrupted header
  for i = 1, #header do
    local s = string.sub(c, 1, i - 1) ..
              string.char(string.byte(string.sub(c, i, i)) + 1) ..
              string.sub(c, i + 1, -1)
    assert(#s == #c)
    assert(not load(s))
  end

  -- loading truncated binary chunks
  for i = 1, #c - 1 do
    local st, msg = load(string.sub(c, 1, i))
    assert(not st and string.find(msg, "truncated"))
  end
end

print('OK')
return deep
```
## [12.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/12.lua)

```lua
-- $Id: testes/closure.lua $
-- See Copyright Notice in file all.lua

print "testing closures"

local A,B = 0,{g=10}
local function f(x)
  local a = {}
  for i=1,1000 do
    local y = 0
    do
      a[i] = function () B.g = B.g+1; y = y+x; return y+A end
    end
  end
  local dummy = function () return a[A] end
  collectgarbage()
  A = 1; assert(dummy() == a[1]); A = 0;
  assert(a[1]() == x)
  assert(a[3]() == x)
  collectgarbage()
  assert(B.g == 12)
  return a
end

local a = f(10)
-- force a GC in this level
local x = {[1] = {}}   -- to detect a GC
setmetatable(x, {__mode = 'kv'})
while x[1] do   -- repeat until GC
  local a = A..A..A..A  -- create garbage
  A = A+1
end
assert(a[1]() == 20+A)
assert(a[1]() == 30+A)
assert(a[2]() == 10+A)
collectgarbage()
assert(a[2]() == 20+A)
assert(a[2]() == 30+A)
assert(a[3]() == 20+A)
assert(a[8]() == 10+A)
assert(getmetatable(x).__mode == 'kv')
assert(B.g == 19)


-- testing equality
a = {}

for i = 1, 5 do  a[i] = function (x) return i + a + _ENV end  end
assert(a[3] ~= a[4] and a[4] ~= a[5])

do
  local a = function (x)  return math.sin(_ENV[x])  end
  local function f()
    return a
  end
  assert(f() == f())
end


-- testing closures with 'for' control variable
a = {}
for i=1,10 do
  a[i] = {set = function(x) i=x end, get = function () return i end}
  if i == 3 then break end
end
assert(a[4] == undef)
a[1].set(10)
assert(a[2].get() == 2)
a[2].set('a')
assert(a[3].get() == 3)
assert(a[2].get() == 'a')

a = {}
local t = {"a", "b"}
for i = 1, #t do
  local k = t[i]
  a[i] = {set = function(x, y) i=x; k=y end,
          get = function () return i, k end}
  if i == 2 then break end
end
a[1].set(10, 20)
local r,s = a[2].get()
assert(r == 2 and s == 'b')
r,s = a[1].get()
assert(r == 10 and s == 20)
a[2].set('a', 'b')
r,s = a[2].get()
assert(r == "a" and s == "b")


-- testing closures with 'for' control variable x break
local f
for i=1,3 do
  f = function () return i end
  break
end
assert(f() == 1)

for k = 1, #t do
  local v = t[k]
  f = function () return k, v end
  break
end
assert(({f()})[1] == 1)
assert(({f()})[2] == "a")


-- testing closure x break x return x errors

local b
function f(x)
  local first = 1
  while 1 do
    if x == 3 and not first then return end
    local a = 'xuxu'
    b = function (op, y)
          if op == 'set' then
            a = x+y
          else
            return a
          end
        end
    if x == 1 then do break end
    elseif x == 2 then return
    else if x ~= 3 then error() end
    end
    first = nil
  end
end

for i=1,3 do
  f(i)
  assert(b('get') == 'xuxu')
  b('set', 10); assert(b('get') == 10+i)
  b = nil
end

pcall(f, 4);
assert(b('get') == 'xuxu')
b('set', 10); assert(b('get') == 14)


local y, w
-- testing multi-level closure
function f(x)
  return function (y)
    return function (z) return w+x+y+z end
  end
end

y = f(10)
w = 1.345
assert(y(20)(30) == 60+w)


-- testing closures x break
do
  local X, Y
  local a = math.sin(0)

  while a do
    local b = 10
    X = function () return b end   -- closure with upvalue
    if a then break end
  end
  
  do
    local b = 20
    Y = function () return b end   -- closure with upvalue
  end

  -- upvalues must be different
  assert(X() == 10 and Y() == 20)
end

  
-- testing closures x repeat-until

local a = {}
local i = 1
repeat
  local x = i
  a[i] = function () i = x+1; return x end
until i > 10 or a[i]() ~= x
assert(i == 11 and a[1]() == 1 and a[3]() == 3 and i == 4)


-- testing closures created in 'then' and 'else' parts of 'if's
a = {}
for i = 1, 10 do
  if i % 3 == 0 then
    local y = 0
    a[i] = function (x) local t = y; y = x; return t end
  elseif i % 3 == 1 then
    goto L1
    error'not here'
  ::L1::
    local y = 1
    a[i] = function (x) local t = y; y = x; return t end
  elseif i % 3 == 2 then
    local t
    goto l4
    ::l4a:: a[i] = t; goto l4b
    error("should never be here!")
    ::l4::
    local y = 2
    t = function (x) local t = y; y = x; return t end
    goto l4a
    error("should never be here!")
    ::l4b::
  end
end

for i = 1, 10 do
  assert(a[i](i * 10) == i % 3 and a[i]() == i * 10)
end

print'+'


-- test for correctly closing upvalues in tail calls of vararg functions
local function t ()
  local function c(a,b) assert(a=="test" and b=="OK") end
  local function v(f, ...) c("test", f() ~= 1 and "FAILED" or "OK") end
  local x = 1
  return v(function() return x end)
end
t()


-- test for debug manipulation of upvalues
local debug = require'debug'

local foo1, foo2, foo3
do
  local a , b, c = 3, 5, 7
  foo1 = function () return a+b end;
  foo2 = function () return b+a end;
  do
    local a = 10
    foo3 = function () return a+b end;
  end
end

assert(debug.upvalueid(foo1, 1))
assert(debug.upvalueid(foo1, 2))
assert(not debug.upvalueid(foo1, 3))
assert(debug.upvalueid(foo1, 1) == debug.upvalueid(foo2, 2))
assert(debug.upvalueid(foo1, 2) == debug.upvalueid(foo2, 1))
assert(debug.upvalueid(foo3, 1))
assert(debug.upvalueid(foo1, 1) ~= debug.upvalueid(foo3, 1))
assert(debug.upvalueid(foo1, 2) == debug.upvalueid(foo3, 2))

assert(debug.upvalueid(string.gmatch("x", "x"), 1) ~= nil)

assert(foo1() == 3 + 5 and foo2() == 5 + 3)
debug.upvaluejoin(foo1, 2, foo2, 2)
assert(foo1() == 3 + 3 and foo2() == 5 + 3)
assert(foo3() == 10 + 5)
debug.upvaluejoin(foo3, 2, foo2, 1)
assert(foo3() == 10 + 5)
debug.upvaluejoin(foo3, 2, foo2, 2)
assert(foo3() == 10 + 3)

assert(not pcall(debug.upvaluejoin, foo1, 3, foo2, 1))
assert(not pcall(debug.upvaluejoin, foo1, 1, foo2, 3))
assert(not pcall(debug.upvaluejoin, foo1, 0, foo2, 1))
assert(not pcall(debug.upvaluejoin, print, 1, foo2, 1))
assert(not pcall(debug.upvaluejoin, {}, 1, foo2, 1))
assert(not pcall(debug.upvaluejoin, foo1, 1, print, 1))

print'OK'
```
## [13.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/13.lua)

```lua
-- $Id: testes/code.lua $
-- See Copyright Notice in file all.lua

if T==nil then
    (Message or print)('\n >>> testC not active: skipping opcode tests <<<\n')
    return
  end
  print "testing code generation and optimizations"
  
  -- to test constant propagation
  local k0aux <const> = 0
  local k0 <const> = k0aux
  local k1 <const> = 1
  local k3 <const> = 3
  local k6 <const> = k3 + (k3 << k0)
  local kFF0 <const> = 0xFF0
  local k3_78 <const> = 3.78
  local x, k3_78_4 <const> = 10, k3_78 / 4
  assert(x == 10)
  
  local kx <const> = "x"
  
  local kTrue <const> = true
  local kFalse <const> = false
  
  local kNil <const> = nil
  
  -- this code gave an error for the code checker
  do
    local function f (a)
    for k,v,w in a do end
    end
  end
  
  
  -- testing reuse in constant table
  local function checkKlist (func, list)
    local k = T.listk(func)
    assert(#k == #list)
    for i = 1, #k do
      assert(k[i] == list[i] and math.type(k[i]) == math.type(list[i]))
    end
  end
  
  local function foo ()
    local a
    a = k3;
    a = 0; a = 0.0; a = -7 + 7
    a = k3_78/4; a = k3_78_4
    a = -k3_78/4; a = k3_78/4; a = -3.78/4
    a = -3.79/4; a = 0.0; a = -0;
    a = k3; a = 3.0; a = 3; a = 3.0
  end
  
  checkKlist(foo, {3.78/4, -3.78/4, -3.79/4})
  
  
  foo = function (f, a)
          f(100 * 1000)
          f(100.0 * 1000)
          f(-100 * 1000)
          f(-100 * 1000.0)
          f(100000)
          f(100000.0)
          f(-100000)
          f(-100000.0)
        end
  
  checkKlist(foo, {100000, 100000.0, -100000, -100000.0})
  
  
  -- floats x integers
  foo = function (t, a)
    t[a] = 1; t[a] = 1.0
    t[a] = 1; t[a] = 1.0
    t[a] = 2; t[a] = 2.0
    t[a] = 0; t[a] = 0.0
    t[a] = 1; t[a] = 1.0
    t[a] = 2; t[a] = 2.0
    t[a] = 0; t[a] = 0.0
  end
  
  checkKlist(foo, {1, 1.0, 2, 2.0, 0, 0.0})
  
  
  -- testing opcodes
  
  -- check that 'f' opcodes match '...'
  local function check (f, ...)
    local arg = {...}
    local c = T.listcode(f)
    for i=1, #arg do
      local opcode = string.match(c[i], "%u%w+")
      -- print(arg[i], opcode)
      assert(arg[i] == opcode)
    end
    assert(c[#arg+2] == undef)
  end
  
  
  -- check that 'f' opcodes match '...' and that 'f(p) == r'.
  local function checkR (f, p, r, ...)
    local r1 = f(p)
    assert(r == r1 and math.type(r) == math.type(r1))
    check(f, ...)
  end
  
  
  -- check that 'a' and 'b' has the same opcodes
  local function checkequal (a, b)
    a = T.listcode(a)
    b = T.listcode(b)
    assert(#a == #b)
    for i = 1, #a do
      a[i] = string.gsub(a[i], '%b()', '')   -- remove line number
      b[i] = string.gsub(b[i], '%b()', '')   -- remove line number
      assert(a[i] == b[i])
    end
  end
  
  
  -- some basic instructions
  check(function ()   -- function does not create upvalues
    (function () end){f()}
  end, 'CLOSURE', 'NEWTABLE', 'EXTRAARG', 'GETTABUP', 'CALL',
       'SETLIST', 'CALL', 'RETURN0')
  
  check(function (x)   -- function creates upvalues
    (function () return x end){f()}
  end, 'CLOSURE', 'NEWTABLE', 'EXTRAARG', 'GETTABUP', 'CALL',
       'SETLIST', 'CALL', 'RETURN')
  
  
  -- sequence of LOADNILs
  check(function ()
    local kNil <const> = nil
    local a,b,c
    local d; local e;
    local f,g,h;
    d = nil; d=nil; b=nil; a=kNil; c=nil;
  end, 'LOADNIL', 'RETURN0')
  
  check(function ()
    local a,b,c,d = 1,1,1,1
    d=nil;c=nil;b=nil;a=nil
  end, 'LOADI', 'LOADI', 'LOADI', 'LOADI', 'LOADNIL', 'RETURN0')
  
  do
    local a,b,c,d = 1,1,1,1
    d=nil;c=nil;b=nil;a=nil
    assert(a == nil and b == nil and c == nil and d == nil)
  end
  
  
  -- single return
  check (function (a,b,c) return a end, 'RETURN1')
  
  
  -- infinite loops
  check(function () while kTrue do local a = -1 end end,
  'LOADI', 'JMP', 'RETURN0')
  
  check(function () while 1 do local a = -1 end end,
  'LOADI', 'JMP', 'RETURN0')
  
  check(function () repeat local x = 1 until true end,
  'LOADI', 'RETURN0')
  
  
  -- concat optimization
  check(function (a,b,c,d) return a..b..c..d end,
    'MOVE', 'MOVE', 'MOVE', 'MOVE', 'CONCAT', 'RETURN1')
  
  -- not
  check(function () return not not nil end, 'LOADFALSE', 'RETURN1')
  check(function () return not not kFalse end, 'LOADFALSE', 'RETURN1')
  check(function () return not not true end, 'LOADTRUE', 'RETURN1')
  check(function () return not not k3 end, 'LOADTRUE', 'RETURN1')
  
  -- direct access to locals
  check(function ()
    local a,b,c,d
    a = b*a
    c.x, a[b] = -((a + d/b - a[b]) ^ a.x), b
  end,
    'LOADNIL',
    'MUL', 'MMBIN',
    'DIV', 'MMBIN', 'ADD', 'MMBIN', 'GETTABLE', 'SUB', 'MMBIN',
    'GETFIELD', 'POW', 'MMBIN', 'UNM', 'SETTABLE', 'SETFIELD', 'RETURN0')
  
  
  -- direct access to constants
  check(function ()
    local a,b
    local c = kNil
    a[kx] = 3.2
    a.x = b
    a[b] = 'x'
  end,
    'LOADNIL', 'SETFIELD', 'SETFIELD', 'SETTABLE', 'RETURN0')
  
  -- "get/set table" with numeric indices
  check(function (a)
    local k255 <const> = 255
    a[1] = a[100]
    a[k255] = a[256]
    a[256] = 5
  end,
    'GETI', 'SETI',
    'LOADI', 'GETTABLE', 'SETI',
    'LOADI', 'SETTABLE',  'RETURN0')
  
  check(function ()
    local a,b
    a = a - a
    b = a/a
    b = 5-4
  end,
    'LOADNIL', 'SUB', 'MMBIN', 'DIV', 'MMBIN', 'LOADI', 'RETURN0')
  
  check(function ()
    local a,b
    a[kTrue] = false
  end,
    'LOADNIL', 'LOADTRUE', 'SETTABLE', 'RETURN0')
  
  
  -- equalities
  checkR(function (a) if a == 1 then return 2 end end, 1, 2,
    'EQI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if -4.0 == a then return 2 end end, -4, 2,
    'EQI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if a == "hi" then return 2 end end, 10, nil,
    'EQK', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if a == 10000 then return 2 end end, 1, nil,
    'EQK', 'JMP', 'LOADI', 'RETURN1')   -- number too large
  
  checkR(function (a) if -10000 == a then return 2 end end, -10000, 2,
    'EQK', 'JMP', 'LOADI', 'RETURN1')   -- number too large
  
  -- comparisons
  
  checkR(function (a) if -10 <= a then return 2 end end, -10, 2,
    'GEI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if 128.0 > a then return 2 end end, 129, nil,
    'LTI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if -127.0 < a then return 2 end end, -127, nil,
    'GTI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if 10 < a then return 2 end end, 11, 2,
    'GTI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if 129 < a then return 2 end end, 130, 2,
    'LOADI', 'LT', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if a >= 23.0 then return 2 end end, 25, 2,
    'GEI', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if a >= 23.1 then return 2 end end, 0, nil,
    'LOADK', 'LE', 'JMP', 'LOADI', 'RETURN1')
  
  checkR(function (a) if a > 2300.0 then return 2 end end, 0, nil,
    'LOADF', 'LT', 'JMP', 'LOADI', 'RETURN1')
  
  
  -- constant folding
  local function checkK (func, val)
    check(func, 'LOADK', 'RETURN1')
    checkKlist(func, {val})
    assert(func() == val)
  end
  
  local function checkI (func, val)
    check(func, 'LOADI', 'RETURN1')
    checkKlist(func, {})
    assert(func() == val)
  end
  
  local function checkF (func, val)
    check(func, 'LOADF', 'RETURN1')
    checkKlist(func, {})
    assert(func() == val)
  end
  
  checkF(function () return 0.0 end, 0.0)
  checkI(function () return k0 end, 0)
  checkI(function () return -k0//1 end, 0)
  checkK(function () return 3^-1 end, 1/3)
  checkK(function () return (1 + 1)^(50 + 50) end, 2^100)
  checkK(function () return (-2)^(31 - 2) end, -0x20000000 + 0.0)
  checkF(function () return (-k3^0 + 5) // 3.0 end, 1.0)
  checkI(function () return -k3 % 5 end, 2)
  checkF(function () return -((2.0^8 + -(-1)) % 8)/2 * 4 - 3 end, -5.0)
  checkF(function () return -((2^8 + -(-1)) % 8)//2 * 4 - 3 end, -7.0)
  checkI(function () return 0xF0.0 | 0xCC.0 ~ 0xAA & 0xFD end, 0xF4)
  checkI(function () return ~(~kFF0 | kFF0) end, 0)
  checkI(function () return ~~-1024.0 end, -1024)
  checkI(function () return ((100 << k6) << -4) >> 2 end, 100)
  
  -- borders around MAXARG_sBx ((((1 << 17) - 1) >> 1) == 65535)
  local a = 17; local sbx = ((1 << a) - 1) >> 1   -- avoid folding
  local border <const> = 65535
  checkI(function () return border end, sbx)
  checkI(function () return -border end, -sbx)
  checkI(function () return border + 1 end, sbx + 1)
  checkK(function () return border + 2 end, sbx + 2)
  checkK(function () return -(border + 1) end, -(sbx + 1))
  
  local border <const> = 65535.0
  checkF(function () return border end, sbx + 0.0)
  checkF(function () return -border end, -sbx + 0.0)
  checkF(function () return border + 1 end, (sbx + 1.0))
  checkK(function () return border + 2 end, (sbx + 2.0))
  checkK(function () return -(border + 1) end, -(sbx + 1.0))
  
  
  -- immediate operands
  checkR(function (x) return x + k1 end, 10, 11, 'ADDI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x - 127 end, 10, -117, 'ADDI', 'MMBINI', 'RETURN1')
  checkR(function (x) return 128 + x end, 0.0, 128.0,
           'ADDI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x * -127 end, -1.0, 127.0,
           'MULK', 'MMBINK', 'RETURN1')
  checkR(function (x) return 20 * x end, 2, 40, 'MULK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x ^ -2 end, 2, 0.25, 'POWK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x / 40 end, 40, 1.0, 'DIVK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x // 1 end, 10.0, 10.0,
           'IDIVK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x % (100 - 10) end, 91, 1,
           'MODK', 'MMBINK', 'RETURN1')
  checkR(function (x) return k1 << x end, 3, 8, 'SHLI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x << 127 end, 10, 0, 'SHRI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x << -127 end, 10, 0, 'SHRI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x >> 128 end, 8, 0, 'SHRI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x >> -127 end, 8, 0, 'SHRI', 'MMBINI', 'RETURN1')
  checkR(function (x) return x & 1 end, 9, 1, 'BANDK', 'MMBINK', 'RETURN1')
  checkR(function (x) return 10 | x end, 1, 11, 'BORK', 'MMBINK', 'RETURN1')
  checkR(function (x) return -10 ~ x end, -1, 9, 'BXORK', 'MMBINK', 'RETURN1')
  
  -- K operands in arithmetic operations
  checkR(function (x) return x + 0.0 end, 1, 1.0, 'ADDK', 'MMBINK', 'RETURN1')
  --  check(function (x) return 128 + x end, 'ADDK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x * -10000 end, 2, -20000,
           'MULK', 'MMBINK', 'RETURN1')
  --  check(function (x) return 20 * x end, 'MULK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x ^ 0.5 end, 4, 2.0, 'POWK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x / 2.0 end, 4, 2.0, 'DIVK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x // 10000 end, 10000, 1,
           'IDIVK', 'MMBINK', 'RETURN1')
  checkR(function (x) return x % (100.0 - 10) end, 91, 1.0,
           'MODK', 'MMBINK', 'RETURN1')
  
  -- no foldings (and immediate operands)
  check(function () return -0.0 end, 'LOADF', 'UNM', 'RETURN1')
  check(function () return k3/0 end, 'LOADI', 'DIVK', 'MMBINK', 'RETURN1')
  check(function () return 0%0 end, 'LOADI', 'MODK', 'MMBINK', 'RETURN1')
  check(function () return -4//0 end, 'LOADI', 'IDIVK', 'MMBINK', 'RETURN1')
  check(function (x) return x >> 2.0 end, 'LOADF', 'SHR', 'MMBIN', 'RETURN1')
  check(function (x) return x << 128 end, 'LOADI', 'SHL', 'MMBIN', 'RETURN1')
  check(function (x) return x & 2.0 end, 'LOADF', 'BAND', 'MMBIN', 'RETURN1')
  
  -- basic 'for' loops
  check(function () for i = -10, 10.5 do end end,
  'LOADI', 'LOADK', 'LOADI', 'FORPREP', 'FORLOOP', 'RETURN0')
  check(function () for i = 0xfffffff, 10.0, 1 do end end,
  'LOADK', 'LOADF', 'LOADI', 'FORPREP', 'FORLOOP', 'RETURN0')
  
  -- bug in constant folding for 5.1
  check(function () return -nil end, 'LOADNIL', 'UNM', 'RETURN1')
  
  
  check(function ()
    local a,b,c
    b[c], a = c, b
    b[a], a = c, b
    a, b = c, a
    a = a
  end,
    'LOADNIL',
    'MOVE', 'MOVE', 'SETTABLE',
    'MOVE', 'MOVE', 'MOVE', 'SETTABLE',
    'MOVE', 'MOVE', 'MOVE',
    -- no code for a = a
    'RETURN0')
  
  
  -- x == nil , x ~= nil
  -- checkequal(function (b) if (a==nil) then a=1 end; if a~=nil then a=1 end end,
  --            function () if (a==9) then a=1 end; if a~=9 then a=1 end end)
  
  -- check(function () if a==nil then a='a' end end,
  -- 'GETTABUP', 'EQ', 'JMP', 'SETTABUP', 'RETURN')
  
  do   -- tests for table access in upvalues
    local t
    check(function () t[kx] = t.y end, 'GETTABUP', 'SETTABUP')
    check(function (a) t[a()] = t[a()] end,
    'MOVE', 'CALL', 'GETUPVAL', 'MOVE', 'CALL',
    'GETUPVAL', 'GETTABLE', 'SETTABLE')
  end
  
  -- de morgan
  checkequal(function () local a; if not (a or b) then b=a end end,
             function () local a; if (not a and not b) then b=a end end)
  
  checkequal(function (l) local a; return 0 <= a and a <= l end,
             function (l) local a; return not (not(a >= 0) or not(a <= l)) end)
  
  
  -- if-break optimizations
  check(function (a, b)
          while a do
            if b then break else a = a + 1 end
          end
        end,
  'TEST', 'JMP', 'TEST', 'JMP', 'ADDI', 'MMBINI', 'JMP', 'RETURN0')
  
  checkequal(function () return 6 or true or nil end,
             function () return k6 or kTrue or kNil end)
  
  checkequal(function () return 6 and true or nil end,
             function () return k6 and kTrue or kNil end)
  
  
  do   -- string constants
    local k0 <const> = "00000000000000000000000000000000000000000000000000"
    local function f1 ()
      local k <const> = k0
      return function ()
               return function () return k end
             end
    end
  
    local f2 = f1()
    local f3 = f2()
    assert(f3() == k0)
    checkK(f3, k0)
    -- string is not needed by other functions
    assert(T.listk(f1)[1] == nil)
    assert(T.listk(f2)[1] == nil)
  end
  
  print 'OK'
```
## [14.lua](https://github.com/luzhixing12345/syntaxlight/tree/main/test/lua/14.lua)

```lua
-- $Id: testes/goto.lua $
-- See Copyright Notice in file all.lua

collectgarbage()

local function errmsg (code, m)
  local st, msg = load(code)
  assert(not st and string.find(msg, m))
end

-- cannot see label inside block
errmsg([[ goto l1; do ::l1:: end ]], "label 'l1'")
errmsg([[ do ::l1:: end goto l1; ]], "label 'l1'")

-- repeated label
errmsg([[ ::l1:: ::l1:: ]], "label 'l1'")
errmsg([[ ::l1:: do ::l1:: end]], "label 'l1'")


-- undefined label
errmsg([[ goto l1; local aa ::l1:: ::l2:: print(3) ]], "local 'aa'")

-- jumping over variable definition
errmsg([[
do local bb, cc; goto l1; end
local aa
::l1:: print(3)
]], "local 'aa'")

-- jumping into a block
errmsg([[ do ::l1:: end goto l1 ]], "label 'l1'")
errmsg([[ goto l1 do ::l1:: end ]], "label 'l1'")

-- cannot continue a repeat-until with variables
errmsg([[
  repeat
    if x then goto cont end
    local xuxu = 10
    ::cont::
  until xuxu < x
]], "local 'xuxu'")

-- simple gotos
local x
do
  local y = 12
  goto l1
  ::l2:: x = x + 1; goto l3
  ::l1:: x = y; goto l2
end
::l3:: ::l3_1:: assert(x == 13)


-- long labels
do
  local prog = [[
  do
    local a = 1
    goto l%sa; a = a + 1
   ::l%sa:: a = a + 10
    goto l%sb; a = a + 2
   ::l%sb:: a = a + 20
    return a
  end
  ]]
  local label = string.rep("0123456789", 40)
  prog = string.format(prog, label, label, label, label)
  assert(assert(load(prog))() == 31)
end


-- ok to jump over local dec. to end of block
do
  goto l1
  local a = 23
  x = a
  ::l1::;
end

while true do
  goto l4
  goto l1  -- ok to jump over local dec. to end of block
  goto l1  -- multiple uses of same label
  local x = 45
  ::l1:: ;;;
end
::l4:: assert(x == 13)

if print then
  goto l1   -- ok to jump over local dec. to end of block
  error("should not be here")
  goto l2   -- ok to jump over local dec. to end of block
  local x
  ::l1:: ; ::l2:: ;;
else end

-- to repeat a label in a different function is OK
local function foo ()
  local a = {}
  goto l3
  ::l1:: a[#a + 1] = 1; goto l2;
  ::l2:: a[#a + 1] = 2; goto l5;
  ::l3::
  ::l3a:: a[#a + 1] = 3; goto l1;
  ::l4:: a[#a + 1] = 4; goto l6;
  ::l5:: a[#a + 1] = 5; goto l4;
  ::l6:: assert(a[1] == 3 and a[2] == 1 and a[3] == 2 and
              a[4] == 5 and a[5] == 4)
  if not a[6] then a[6] = true; goto l3a end   -- do it twice
end

::l6:: foo()


do   -- bug in 5.2 -> 5.3.2
  local x
  ::L1::
  local y             -- cannot join this SETNIL with previous one
  assert(y == nil)
  y = true
  if x == nil then
    x = 1
    goto L1
  else
    x = x + 1
  end
  assert(x == 2 and y == true)
end

-- bug in 5.3
do
  local first = true
  local a = false
  if true then
    goto LBL
    ::loop::
    a = true
    ::LBL::
    if first then
      first = false
      goto loop
    end
  end
  assert(a)
end

do   -- compiling infinite loops
  goto escape   -- do not run the infinite loops
  ::a:: goto a
  ::b:: goto c
  ::c:: goto b
end
::escape::
--------------------------------------------------------------------------------
-- testing closing of upvalues

local debug = require 'debug'

local function foo ()
  local t = {}
  do
  local i = 1
  local a, b, c, d
  t[1] = function () return a, b, c, d end
  ::l1::
  local b
  do
    local c
    t[#t + 1] = function () return a, b, c, d end    -- t[2], t[4], t[6]
    if i > 2 then goto l2 end
    do
      local d
      t[#t + 1] = function () return a, b, c, d end   -- t[3], t[5]
      i = i + 1
      local a
      goto l1
    end
  end
  end
  ::l2:: return t
end

local a = foo()
assert(#a == 6)

-- all functions share same 'a'
for i = 2, 6 do
  assert(debug.upvalueid(a[1], 1) == debug.upvalueid(a[i], 1))
end

-- 'b' and 'c' are shared among some of them
for i = 2, 6 do
  -- only a[1] uses external 'b'/'b'
  assert(debug.upvalueid(a[1], 2) ~= debug.upvalueid(a[i], 2))
  assert(debug.upvalueid(a[1], 3) ~= debug.upvalueid(a[i], 3))
end

for i = 3, 5, 2 do
  -- inner functions share 'b'/'c' with previous ones
  assert(debug.upvalueid(a[i], 2) == debug.upvalueid(a[i - 1], 2))
  assert(debug.upvalueid(a[i], 3) == debug.upvalueid(a[i - 1], 3))
  -- but not with next ones
  assert(debug.upvalueid(a[i], 2) ~= debug.upvalueid(a[i + 1], 2))
  assert(debug.upvalueid(a[i], 3) ~= debug.upvalueid(a[i + 1], 3))
end

-- only external 'd' is shared
for i = 2, 6, 2 do
  assert(debug.upvalueid(a[1], 4) == debug.upvalueid(a[i], 4))
end

-- internal 'd's are all different
for i = 3, 5, 2 do
  for j = 1, 6 do
    assert((debug.upvalueid(a[i], 4) == debug.upvalueid(a[j], 4))
      == (i == j))
  end
end

--------------------------------------------------------------------------------
-- testing if x goto optimizations

local function testG (a)
  if a == 1 then
    goto l1
    error("should never be here!")
  elseif a == 2 then goto l2
  elseif a == 3 then goto l3
  elseif a == 4 then
    goto l1  -- go to inside the block
    error("should never be here!")
    ::l1:: a = a + 1   -- must go to 'if' end
  else
    goto l4
    ::l4a:: a = a * 2; goto l4b
    error("should never be here!")
    ::l4:: goto l4a
    error("should never be here!")
    ::l4b::
  end
  do return a end
  ::l2:: do return "2" end
  ::l3:: do return "3" end
  ::l1:: return "1"
end

assert(testG(1) == "1")
assert(testG(2) == "2")
assert(testG(3) == "3")
assert(testG(4) == 5)
assert(testG(5) == 10)

do
  -- if x back goto out of scope of upvalue
  local X
  goto L1

  ::L2:: goto L3

  ::L1:: do
    local a <close> = setmetatable({}, {__close = function () X = true end})
    assert(X == nil)
    if a then goto L2 end   -- jumping back out of scope of 'a'
  end

  ::L3:: assert(X == true)   -- checks that 'a' was correctly closed
end
--------------------------------------------------------------------------------


print'OK'
```
