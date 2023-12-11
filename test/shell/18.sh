Intel(R) Memory Latency Checker - v3.11
*** Unable to modify prefetchers (try executing 'modprobe msr')
*** So, enabling random access for latency measurements
Measuring idle latencies for random access (in ns)...
                Numa node
Numa node            0       1
       0         253.1   429.6
       1         392.7   287.3

Measuring Peak Injection Memory Bandwidths for the system
Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
Using all the threads from each core if Hyper-threading is enabled
Using traffic with the following read-write ratios
ALL Reads        :      199381.1
3:1 Reads-Writes :      218009.3
2:1 Reads-Writes :      216701.3
1:1 Reads-Writes :      208055.7
Stream-triad like:      205531.7

Measuring Memory Bandwidths between nodes within system
Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
Using all the threads from each core if Hyper-threading is enabled
Using Read-only traffic type
                Numa node
Numa node            0       1
       0        101203.0        80509.9
       1        87389.3 90140.2

Measuring Loaded Latencies for the system
Using all the threads from each core if Hyper-threading is enabled
Using Read-only traffic type
Inject  Latency Bandwidth
Delay   (ns)    MB/sec
==========================
 00000  642.45   198317.3
 00002  641.75   198628.1
 00008  609.64   198505.1
 00015  555.02   195734.2
 00050  517.77   190798.8
 00100  394.57   178862.7
 00200  261.29    96680.8
 00300  249.25    61850.5
 00400  243.05    47526.6
 00500  272.35    39008.2
 00700  231.46    28640.9
 01000  228.66    20313.0
 01300  227.70    15908.8
 01700  226.91    12434.8
 02500  225.83     8690.3
 03500  232.78     6425.1
 05000  223.81     4588.6
 09000  222.93     2668.6
 20000  220.31     1350.0

Measuring cache-to-cache transfer latency (in ns)...
Local Socket L2->L2 HIT  latency        178.1
Local Socket L2->L2 HITM latency        175.1
Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                        Reader Numa Node
Writer Numa Node     0       1
            0        -   336.8
            1    363.9       -
Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                        Reader Numa Node
Writer Numa Node     0       1
            0        -   346.8
            1    326.3       -