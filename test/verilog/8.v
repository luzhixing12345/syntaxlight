module top_module (
    input clk,
    input resetn,
    input [1:0] byteena,
    input [15:0] d,
    output [15:0] q
);
    always@(posedge clk)begin
        if(~resetn)
            q <= 16'd0;
        else
            begin
            if(byteena[0])
                q[7:0] <= d[7:0];
        	if(byteena[1])
            	q[15:8] <= d[15:8];
            end
    end

endmodule

module top_module (
    input clk,
    input reset,
    output OneHertz,
    output [2:0] c_enable
); //
    
    reg [3:0] Q0,Q1,Q2;

    always@(posedge clk)begin
        if(reset)
            c_enable[0] = 1;
    end
    
    assign c_enable[1] = (Q0 == 4'd9);
    assign c_enable[2] = ({Q1,Q0} == 8'h99);
    assign OneHertz = ({Q2,Q1,Q0} == 12'h999)? 1'b1:1'b0;
    
    bcdcount counter0 (clk, reset, c_enable[0], Q0);
    bcdcount counter1 (clk, reset, c_enable[1], Q1);
    bcdcount counter2 (clk, reset, c_enable[2], Q2);

endmodule

// solution 1
module top_module (
    input clk,
    input reset,   // Synchronous active-high reset
    output [3:1] ena,
    output [15:0] q);
    
	wire ena0;
    always@(posedge clk)begin
        if(reset)
            ena0 = 1;
    end
    
    assign ena[1] = (q[3:0] == 4'h9);
    assign ena[2] = (q[7:0] == 8'h99);
    assign ena[3] = (q[11:0] == 12'h999);
    
   	modulo_10 counter0 (clk, reset, ena0, q[3:0]);
    modulo_10 counter1 (clk, reset, ena[1], q[7:4]);
    modulo_10 counter2 (clk, reset, ena[2], q[11:8]);
    modulo_10 counter3 (clk, reset, ena[3], q[15:12]);

endmodule

module modulo_10 (
    input clk,
    input reset,
    input slowena,
    output [3:0] q);

    always@(posedge clk)begin
        if(reset)
            q <= 0;
        else if(slowena)begin
            if (q == 9)//slowena is high
               	q <= 0;
	        	else
                q <= q + 1;
        end
        else
            q <= q;
    end
endmodule

// solution 2
module top_module (
    input clk,
    input reset,   // Synchronous active-high reset
    output [3:1] ena,
    output [15:0] q);
    
    reg [3:0]	ones;
    reg [3:0]	tens;
    reg [3:0]	hundreds;
    reg [3:0]	thousands;
    
    always@(posedge clk)begin
        if(reset)begin
            ones <= 4'd0;
        end
        else if(ones == 4'd9)begin
            ones <= 4'd0;
        end
        else begin
            ones <= ones + 1'b1;
        end
    end
    
    always@(posedge clk)begin
        if(reset)begin
            tens <= 4'd0;
        end
        else if(tens == 4'd9 && ones == 4'd9)begin
            tens <= 4'd0;
        end
        else if(ones == 4'd9) begin
            tens <= tens + 1'b1;
        end
    end
    
    always@(posedge clk)begin
        if(reset)begin
            hundreds <= 4'd0;
        end
        else if(hundreds == 4'd9 && tens == 4'd9 && ones == 4'd9)begin
            hundreds <= 4'd0;
        end
        else if(tens == 4'd9 && ones == 4'd9) begin
            hundreds <= hundreds + 1'b1;
        end
    end
    
    always@(posedge clk)begin
        if(reset)begin
            thousands <= 4'd0;
        end
        else if(thousands == 4'd9 && hundreds == 4'd9 && tens == 4'd9 && ones == 4'd9)begin
            thousands <= 4'd0;
        end
        else if(hundreds == 4'd9 && tens == 4'd9 && ones == 4'd9) begin
            thousands <= thousands + 1'b1;
        end
    end
    
    assign q = {thousands, hundreds, tens, ones};
    assign ena[1] = (ones == 4'd9) ? 1'b1 : 1'b0;
    assign ena[2] = (tens == 4'd9 && ones == 4'd9) ? 1'b1 : 1'b0;
    assign ena[3] = (hundreds == 4'd9 && tens == 4'd9 && ones == 4'd9) ? 1'b1 : 1'b0;
 
endmodule