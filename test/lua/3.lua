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
