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
    isMale = true,
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
