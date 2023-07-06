program AddTwoNumbers;
var
  num1, num2, sum: integer;
begin
  writeln('please enter number 1:');
  readln(num1);
  
  writeln('please enter number 2:');
  readln(num2);
  
  sum := num1 + num2;
  
  writeln('sum of number 1 and number 2 is ', sum);
end.