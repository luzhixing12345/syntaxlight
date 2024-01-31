module top_module (
    input in1,
    input in2,
    input in3,
    output out);
    
    assign out = ~(in1^in2) ^ in3;

endmodule

module top_module( 
    input a, b,
    output out_and,
    output out_or,
    output out_xor,
    output out_nand,
    output out_nor,
    output out_xnor,
    output out_anotb
);
    
    assign out_and = a & b;
    assign out_or = a | b;
    assign out_xor = a ^ b;
    assign out_nand = ~ (a & b);
    assign out_nor = ~ (a | b);
    assign out_xnor = ~ a ^ b;
    assign out_anotb = a & ~b;

endmodule

module top_module(
	input [1:0] A,
	input [1:0] B,
	output z);

	assign z = (A[1:0]==B[1:0]);	// Comparisons produce a 1 or 0 result.
	
	// Another option is to use a 16-entry truth table ( {A,B} is 4 bits, with 16 combinations ).
	// There are 4 rows with a 1 result.  0000, 0101, 1010, and 1111.

endmodule

module top_module (input x, input y, output z);

    wire z1,z2,z3,z4;
     
    
    A_module IA1(x,y,z1);
    B_module IB1(x,y,z2);
    A_module IA2(x,y,z3);
    B_module IB2(x,y,z4);
    
    assign z = (z1 | z2) ^ (z3 & z4);
    
endmodule

module A_module (input x, input y, output z);

    assign z = (x^y) & x;
    
endmodule

module B_module ( input x, input y, output z );

    assign z = ~x^y;
    
endmodule

//solution 1
module top_module (
	input a,
	input b,
	input sel,
	output out
);

	assign out = (sel & b) | (~sel & a);	// Mux expressed as AND and OR
	
	// Ternary operator is easier to read, especially if vectors are used:
	// assign out = sel ? b : a;
	
endmodule

//solution 2
module top_module( 
    input a, b, sel,
    output out ); 

    assign out = sel? b:a;//ternary operator
    
endmodule

module top_module (
    input c,
    input d,
    output [3:0] mux_in
); 

    always @(*)begin
        mux_in = 4'b0000; // default
        case({c,d})
            2'b00: mux_in = 4'b0100;
            2'b01: mux_in = 4'b0001;
            2'b11: mux_in = 4'b1001;
            2'b10: mux_in = 4'b0101;
        endcase
    end
    
endmodule
