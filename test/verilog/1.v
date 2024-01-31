module top_module( output one );
	
	assign one = 1'b1;
	
endmodule

module top_module( input in, output out );
	
	assign out = in;
	// Note that wires are directional, so "assign in = out" is not equivalent.
	
endmodule

//solution 1
module top_module (
	input [7:0] in,
	output [7:0] out
);
	
	assign {out[0],out[1],out[2],out[3],out[4],out[5],out[6],out[7]} = in;

endmodule
	
//solution 2
module top_module (
	input [7:0] in,
	output [7:0] out
);

	always @(*) begin	
		for (int i=0; i<8; i++)	// int is a SystemVerilog type. Use integer for pure Verilog.
			out[i] = in[8-i-1];
	end

endmodule

//solution 3
module top_module (
	input [7:0] in,
	output [7:0] out
);

	generate
		genvar i;
		for (i=0; i<8; i = i+1) begin: my_block_name
			assign out[i] = in[8-i-1];
		end
	endgenerate

endmodule
