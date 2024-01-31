module top_module(
    input a, 
    input b,
    output wire out_assign,
    output reg out_alwaysblock
);
    assign out_assign = a & b;

    always @ (*) out_alwaysblock = a & b;
	
endmodule

module top_module(
    input clk,
    input a,
    input b,
    output wire out_assign,
    output reg out_always_comb,
    output reg out_always_ff   );

    assign out_assign = a ^ b;

    always @ (*) out_always_comb = a ^ b;

    always @(posedge clk) out_always_ff <= a ^ b;
endmodule

module top_module(
    input a,
    input b,
    input sel_b1,
    input sel_b2,
    output wire out_assign,
    output reg out_always   ); 

    assign out_assign = (sel_b1 && sel_b2)?  b : a;
    
    always @ (*)
    begin
        if (sel_b1 && sel_b2) begin 
            out_always <= b ;
        end
        else begin
            out_always <= a ;
        end
    end


endmodule

module top_module (
    input      cpu_overheated,
    output reg shut_off_computer,
    input      arrived,
    input      gas_tank_empty,
    output reg keep_driving  ); //

    always @(*) begin
        if (cpu_overheated)
           shut_off_computer = 1;
        else
           shut_off_computer = 0;
    end

    always @(*) begin
        if (~arrived)
           keep_driving = ~gas_tank_empty;//
        else 
           keep_driving = 0;
    end

endmodule

module top_module ( 
    input [2:0] sel, 
    input [3:0] data0,
    input [3:0] data1,
    input [3:0] data2,
    input [3:0] data3,
    input [3:0] data4,
    input [3:0] data5,
    output reg [3:0] out   );//

    always@(*) begin  // This is a combinational circuit
        case(sel)
            3'b000: out = data0;
            3'b001: out = data1;
            3'b010: out = data2;
            3'b011: out = data3;
            3'b100: out = data4;
            3'b101: out = data5;
            default: out = 3'b0000;
        endcase
    end

endmodule

//solution 1
module top_module (
    input [3:0] in,
    output reg [1:0] pos  );

    always @ (*)begin
        casex (in)
            4'bxxx1: pos = 2'd0;
            4'bxx10: pos = 2'd1;
            4'bx100: pos = 2'd2;
            4'b1000: pos = 2'd3;
            default: pos = 2'd0;
        endcase
    end

endmodule

//solution 2
module top_module (
    input [3:0] in,
    output reg [1:0] pos  );

    always @ (*)begin
        casez (in)
            4'b???1: pos = 2'd0;//按照case项的顺序比较,若匹配上了就不再比较
            4'b??10: pos = 2'd1;
            4'b?100: pos = 2'd2;
            4'b1000: pos = 2'd3;
            default: pos = 2'd0;
        endcase
    end
    
endmodule

//solution 3
module top_module (
	input [3:0] in,
	output reg [1:0] pos
);

	always @(*) begin			// Combinational always block
		case (in)
			4'h0: pos = 2'h0;	// I like hexadecimal because it saves typing.
			4'h1: pos = 2'h0;
			4'h2: pos = 2'h1;
			4'h3: pos = 2'h0;
			4'h4: pos = 2'h2;
			4'h5: pos = 2'h0;
			4'h6: pos = 2'h1;
			4'h7: pos = 2'h0;
			4'h8: pos = 2'h3;
			4'h9: pos = 2'h0;
			4'ha: pos = 2'h1;
			4'hb: pos = 2'h0;
			4'hc: pos = 2'h2;
			4'hd: pos = 2'h0;
			4'he: pos = 2'h1;
			4'hf: pos = 2'h0;
			default: pos = 2'b0;	// Default case is not strictly necessary because all 16 combinations are covered.
		endcase
	end
	
	// There is an easier way to code this. See the next problem (always_casez).
	
endmodule

module top_module (
    input [7:0] in,
    output reg [2:0] pos  );

    always @(*)begin
        casez(in)
            8'b???????1: pos = 3'd0;
            8'b??????10: pos = 3'd1;
            8'b?????100: pos = 3'd2;
            8'b????1000: pos = 3'd3;
            8'b???10000: pos = 3'd4;
            8'b??100000: pos = 3'd5;
            8'b?1000000: pos = 3'd6;
            8'b10000000: pos = 3'd7;
            default: pos = 3'd0;
        endcase
    end
endmodule