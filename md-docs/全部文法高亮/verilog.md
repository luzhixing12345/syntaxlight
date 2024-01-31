
# verilog
## [1.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/1.v)

```verilog
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

```
## [2.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/2.v)

```verilog
module top_module (
	input a,
	input b,
	input c,
	output w,
	output x,
	output y,
	output z  );
	
	assign w = a;
	assign x = b;
	assign y = b;
	assign z = c;

	// If we're certain about the width of each signal, using 
	// the concatenation operator is equivalent and shorter:
	// assign {w,x,y,z} = {a,b,b,c};
	
endmodule

module top_module(
	input in,
	output out
);
	
	assign out = ~in;
	
endmodule

module top_module( 
    input a, 
    input b, 
    output out );

    assign out = ~(a | b);

endmodule

module top_module (
	input a,
	input b,
	input c,
	input d,
	output out,
	output out_n );
	
	wire w1, w2;		// Declare two wires (named w1 and w2)
	assign w1 = a&b;	// First AND gate
	assign w2 = c&d;	// Second AND gate
	assign out = w1|w2;	// OR gate: Feeds both 'out' and the NOT gate

	assign out_n = ~out;	// NOT gate
	
endmodule

module top_module ( 
    input p1a, p1b, p1c, p1d, p1e, p1f,
    output p1y,
    input p2a, p2b, p2c, p2d,
    output p2y );

    assign p1y = (p1a & p1b & p1c)|(p1d & p1e & p1f);
    assign p2y = (p2a & p2b)|(p2c & p2d);
    
endmodule
```
## [3.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/3.v)

```verilog
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
```
## [4.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/4.v)

```verilog
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
```
## [5.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/5.v)

```verilog
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
```
## [6.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/6.v)

```verilog
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
```
## [7.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/7.v)

```verilog
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

```
## [8.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/8.v)

```verilog
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
```
## [9.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/9.v)

```verilog
module top_module(
    input clk,
    input reset,
    input ena,
    output pm,
    output [7:0] hh,
    output [7:0] mm,
    output [7:0] ss); 
    
    reg 		pm_temp;
    reg	[3:0]	ss_ones;
    reg [3:0]	ss_tens;
    reg	[3:0]	mm_ones;
    reg [3:0]	mm_tens;
    reg	[3:0]	hh_ones;
    reg [3:0]	hh_tens;
    wire		add_ss_ones;
    wire		end_ss_ones;
    wire		add_ss_tens;
    wire		end_ss_tens;
    wire		add_mm_ones;
    wire		end_mm_ones;
    wire		add_mm_tens;
    wire		end_mm_tens;
    wire		add_hh_ones;
    wire		end_hh_ones_0;
    wire		end_hh_ones_1;
    wire		add_hh_tens;
    wire		end_hh_tens_0;
    wire		end_hh_tens_1;
    wire		pm_ding;
    
    always@(posedge clk)begin
        if(reset)begin
            ss_ones <= 4'd0;
        end
        else if(add_ss_ones)begin
            if(end_ss_ones)begin
                ss_ones <= 4'd0;
            end
            else begin
                ss_ones <= ss_ones + 1'b1;
            end
        end
    end
    
    assign add_ss_ones = ena;
    assign end_ss_ones = add_ss_ones && ss_ones == 4'd9;
    
    always@(posedge clk)begin
        if(reset)begin
            ss_tens <= 4'd0;
        end
        else if(add_ss_tens)begin
            if(end_ss_tens)begin
                ss_tens <= 4'd0;
            end
            else begin
                ss_tens <= ss_tens + 1'b1;
            end
        end
    end
    
    assign add_ss_tens = end_ss_ones;
    assign end_ss_tens = add_ss_tens && ss_tens == 4'd5;
    
    always@(posedge clk)begin
        if(reset)begin
            mm_ones <= 4'd0;
        end
        else if(add_mm_ones)begin
            if(end_mm_ones)begin
                mm_ones <= 4'd0;
            end
            else begin
                mm_ones <= mm_ones + 1'b1;
            end
        end
    end
    
    assign add_mm_ones = end_ss_tens;
    assign end_mm_ones = add_mm_ones && mm_ones == 4'd9;
    
    always@(posedge clk)begin
        if(reset)begin
            mm_tens <= 4'd0;
        end
        else if(add_mm_tens)begin
            if(end_mm_tens)begin
                mm_tens <= 4'd0;
            end
            else begin
                mm_tens <= mm_tens + 1'b1;
            end
        end
    end
    
    assign add_mm_tens = end_mm_ones;
    assign end_mm_tens = add_mm_tens && mm_tens == 4'd5;
    
    always@(posedge clk)begin
        if(reset)begin
            hh_ones <= 4'd2;
        end
        else if(add_hh_ones)begin
            if(end_hh_ones_0)begin
                hh_ones <= 4'd0;
            end
            else if(end_hh_ones_1)begin
                hh_ones <= 4'd1;
            end
            else begin
                hh_ones <= hh_ones + 1'b1;
            end
        end
    end
    
    assign add_hh_ones = end_mm_tens;
    assign end_hh_ones_0 = add_hh_ones && hh_ones == 4'd9;
    assign end_hh_ones_1 = add_hh_ones && (hh_tens == 4'd1 && hh_ones == 4'd2);
    
    always@(posedge clk)begin
        if(reset)begin
            hh_tens <= 4'd1;
        end
        else if(add_hh_tens)begin
            if(end_hh_tens_0)begin
                hh_tens <= 4'd0;
            end
            else if(end_hh_tens_1)begin
                hh_tens <= hh_tens + 1'b1;
            end
        end
    end
    
    assign add_hh_tens = end_mm_tens;
    assign end_hh_tens_0 = add_hh_tens && end_hh_ones_1;
    assign end_hh_tens_1 = add_hh_tens && end_hh_ones_0;
    
    always@(posedge clk)begin
        if(reset)begin
            pm_temp <= 1'b0;
        end
        else if(pm_ding)begin
            pm_temp <= ~pm_temp;
        end
    end
    
    assign pm_ding = hh_tens == 4'd1 && hh_ones == 4'd1 && end_mm_tens;
    
    assign ss = {ss_tens, ss_ones};
    assign mm = {mm_tens, mm_ones};
    assign hh = {hh_tens, hh_ones};
    assign pm = pm_temp;
 
endmodule
```
## [10.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/10.v)

```verilog
module top_module(
    input clk,
    input areset,    // Asynchronous reset to state B
    input in,
    output out);//  

    parameter A=0, B=1; 
    reg state, next_state;

    always @(*) begin    // This is a combinational always block
        // State transition logic
        case(state)
            A: next_state <= in? A:B;
            B: next_state <= in? B:A;
        endcase
    end

    always @(posedge clk, posedge areset) begin    // This is a sequential always block
        // State flip-flops with asynchronous reset
        if(areset)
            state <= B;
        else
            state <= next_state;
    end

    // Output logic
    // assign out = (state == ...);
    assign out = (state==B);

endmodule


```
## [11.v](https://github.com/luzhixing12345/syntaxlight/tree/main/test/verilog/11.v)

```verilog
module mem_model #(
 parameter ADDR_WIDTH=8;
 parameter DATA_WIDTH=32;)
 (clk, addr, data);

 input  clk;
 input  [ADDR_WIDTH-1:0] addr;
 output [DATA_WIDTH-1:0] data;

 //Creates mem_1 instance with default addr and data widths.
mem_model mem_1 (.clk(clk),
                 .addr(addr_1),
                 .data(data_1));

//Creates mem_2 instance with addr width = 4 and data width = 8.
mem_model #(4,8) mem_2 (.clk(clk),
                        .addr(addr_2),
                        .data(data_2));

//Creates mem_3 instance with addr width = 32 and data width = 64.
mem_model #(32,64) mem_3 (.clk(clk),
                          .addr(addr_3),
                          .data(data_3));

//Creates mem_4 instance with default addr width and data width = 64.
mem_model #(DATA_WIDTH=64) mem_4 (.clk(clk),
                                 .addr(addr_3),
                                 .data(data_3));

//ADDR_WIDTH value of mem_1 instance can be changed by using defparam as shown below,
defparam hierarchical_path.mem_1.ADDR_WIDTH = 32;

endmodule
```
