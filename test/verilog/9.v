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