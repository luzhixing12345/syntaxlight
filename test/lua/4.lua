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
