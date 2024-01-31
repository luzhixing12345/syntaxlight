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