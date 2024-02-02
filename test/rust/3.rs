fn main() {
    println!("secret number = {{123}} {}", secret_number);
    println!("guess a number");
    format!("test"); // => "test"
    format!("hello {}", "world!"); // => "hello world!"
    format!("x = {:?}, y = {val}", 10, val = 30); // => "x = 10, y = 30"
    let (x, y) = (1, 2);
    format!("{x} + {y} = 3"); // => "1 + 2 = 3"
    println!("Name: {0}, Age: {1}", name, age);
    println!("Value: {:>5}", value);
    println!("Pi: {:.2}", pi);
    println!("Pi: {:<8.2e}", pi);
    println!("Value: {:5}", value);
    println!("Pi: {:<8.2}", pi); 
    println!("Value: {:<+5}", value);
}