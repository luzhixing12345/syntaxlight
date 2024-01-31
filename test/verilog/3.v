module top_module(
	input [2:0] vec, 
	output [2:0] outv,
	output o2,
	output o1,
	output o0
);
	
	assign outv = vec;

	// This is ok too: assign {o2, o1, o0} = vec;
	assign o0 = vec[0];
	assign o1 = vec[1];
	assign o2 = vec[2];
	
endmodule

module top_module (
	input [15:0] in,
	output [7:0] out_hi,
	output [7:0] out_lo
);
	
	assign out_hi = in[15:8];
	assign out_lo = in[7:0];
	
	// Concatenation operator also works: assign {out_hi, out_lo} = in;
	
endmodule

module top_module (
	input [31:0] in,
	output [31:0] out
);

	assign out[31:24] = in[ 7: 0];	
	assign out[23:16] = in[15: 8];	
	assign out[15: 8] = in[23:16];	
	assign out[ 7: 0] = in[31:24];	
	
endmodule

module top_module( 
    input [3:0] in,
    output out_and,
    output out_or,
    output out_xor
);
    
    assign out_and = in[0]&in[1]&in[2]&in[3];
    assign out_or = in[0]|in[1]|in[2]|in[3];
    assign out_xor = in[0]^in[1]^in[2]^in[3];

endmodule

//solution 2
module top_module( 
    input [3:0] in,
    output out_and,
    output out_or,
    output out_xor
);
    
    assign out_and = &in;//reduction operator
    assign out_or = |in;
    assign out_xor = ^in;

endmodule

module top_module (
    input [4:0] a, b, c, d, e, f,
    output [7:0] w, x, y, z );//

    assign {w, x, y, z}={a, b, c, d, e, f, 2'b11};
    // assign { ... } = { ... };

endmodule

//solution 1
module top_module (
	input [7:0] in,
	output [7:0] out
);
	
	assign {out[0],out[1],out[2],out[3],out[4],out[5],out[6],out[7]} = in;

endmodule

module top_module (
	input [7:0] in,
	output [31:0] out
);

	// Concatenate two things together:
	// 1: {in[7]} repeated 24 times (24 bits)
	// 2: in[7:0] (8 bits)
	assign out = { {24{in[7]}}, in };//notice the braces
	
endmodule

module top_module (
	input a, b, c, d, e,
	output [24:0] out
);

	wire [24:0] top, bottom;
	assign top    = { {5{a}}, {5{b}}, {5{c}}, {5{d}}, {5{e}} };
	assign bottom = {5{a,b,c,d,e}};
	assign out = ~top ^ bottom;	// Bitwise XNOR

	// This could be done on one line:
	assign out = ~{ {5{a}}, {5{b}}, {5{c}}, {5{d}}, {5{e}} } ^ {5{a,b,c,d,e}};
	
endmodule