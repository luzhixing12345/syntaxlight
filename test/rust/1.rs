use rand::Rng;
use std::cmp::Ordering;
use std::io;
use std::alloc::{*, self};

fn main() {
    println!("Hello, world!");

    let secret_number = rand::thread_rng().gen_range(0..100);

    println!("secret number = {}", secret_number);
    println!("guess a number");

    loop {
        let mut guess = String::new();
        io::stdin().read_line(&mut guess).expect("error!");
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue
        };  

        // println!("what you guess in {}", guess);

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("too small"),
            Ordering::Greater => println!("too big"),
            Ordering::Equal => {
                println!("you win!");
                break;
            },
        }
    }
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;
        }
    };
    // println!("result = {}", result);
}
