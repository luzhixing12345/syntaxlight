module top_module (
    input [7:0] a, b, c, d,
    output [7:0] min);//
    
    wire[7:0] abmin,cdmin;

    assign abmin = (a < b)? a:b;
    assign cdmin = (c < d)? c:d;
    assign min = (abmin < cdmin)? abmin:cdmin;
    
    // assign intermediate_result1 = compare? true: false;

endmodule

//solution 1
module top_module( 
    input [99:0] in,
    output [99:0] out
);
    always@(*)begin
        for(integer i = 0;i<100;i=i+1)
            out[i] = in[99-i];
    end

endmodule

//solution 2
module top_module (
	input [99:0] in,
	output reg [99:0] out
);
	
	always @(*) begin
		for (int i=0;i<$bits(out);i++)		// $bits() is a system function that returns the width of a signal.
			out[i] = in[$bits(out)-i-1];	// $bits(out) is 100 because out is 100 bits wide.
	end
	
endmodule

//solution 3
module top_module (
	input [99:0] in,
	output reg [99:0] out
);
	
    genvar i;//生成generate中的循环变量
    generate for (i=0;i<$bits(out);i=i+1)
        begin:Go//begin—_end和命名一定要有
            assign out[i] = in[$bits(out)-1-i];//此处要用assign语句
        end
    endgenerate
	
endmodule

module top_module( 
    input [99:0] a, b,
    input cin,
    output [99:0] cout,
    output [99:0] sum );

    always @(*)begin
        {cout[0],sum[0]} = a[0] + b[0] + cin;//全加器
        for (int i=1;i<$bits(a);i=i+1)
        {cout[i],sum[i]} = a[i] + b[i] + cout[i-1];
    end
    
endmodule

module top_module( 
    input [399:0] a, b,
    input cin,
    output cout,
    output [399:0] sum );

    wire [400:0] midcout;

    assign cout = midcout[400];
    
    bcd_fadd bcd_fadd_0(.a(a[3:0]), .b(b[3:0]), .cin(cin), .cout(midcout[4]), .sum(sum[3:0]));

    generate//子模块不可在always模块内部调用,可以生成模块重复调用
        genvar i;
        for(i=4;i<$bits(a);i=i+4)
            begin:Go
                bcd_fadd bcd_fadd_i(.a(a[i+3:i]), .b(b[i+3:i]), .cin(midcout[i]), .cout(midcout[i+4]), .sum(sum[i+3:i]));
            end
    endgenerate
    
endmodule