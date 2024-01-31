module top_module (
	input a,
	input b,
	output out
);

	// Create an instance of "mod_a" named "inst1", and connect ports by name:
	mod_a inst1 ( 
		.in1(a), 	// Port"in1"connects to wire "a"
		.in2(b),	// Port "in2" connects to wire "b"
		.out(out)	// Port "out" connects to wire "out" 
				// (Note: mod_a's port "out" is not related to top_module's wire "out". 
				// It is simply coincidence that they have the same name)
	);

	// Create an instance of "mod_a" named "inst2", and connect ports by position:
	mod_a inst2 ( a, b, out );	// The three wires are connected to ports in1, in2, and out, respectively.
	
endmodule

module top_module ( 
    input a, 
    input b, 
    input c,
    input d,
    output out1,
    output out2
);

    mod_a instance1 ( .out1(out1), .out2(out2), .in1(a), .in2(b), .in3(c), .in4(d) );
    
endmodule

module top_module (
    input clk, 
    input [7:0] d, 
    input [1:0] sel, 
    output [7:0] q 
);
    wire [7:0] out1,out2,out3;
    my_dff8 instance1 (clk,d,out1);
    my_dff8 instance2 (clk,out1,out2);
    my_dff8 instance3 (clk,out2,out3);

    always @ (*)
    begin
        case (sel)
            2'b00: q = d;
            2'b01: q = out1;
            2'b10: q = out2;
            2'b11: q = out3;
        endcase
    end

endmodule

module top_module(
    input [31:0] a,
    input [31:0] b,
    output [31:0] sum
);

    wire [15:0] sumlow,sumhigh0,sumhigh1;
    wire coutlow,couthigh0,couthigh1;

    add16 add16low (a[15:0],b[15:0],1'b0,sumlow,coutlow);
    add16 add16high0 (a[31:16],b[31:16],1'b0,sumhigh0,couthigh0);
    add16 add16high1 (a[31:16],b[31:16],1'b1,sumhigh1,couthigh1);

    always @ (*)
    begin
        case (coutlow)
            1'b0: sum = {sumhigh0,sumlow};
            1'b1: sum = {sumhigh1,sumlow};
        endcase
    end

endmodule