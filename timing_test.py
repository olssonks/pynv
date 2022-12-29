import sys
from line_profiler import LineProfiler

from fast_scan_single_run import main

lp = LineProfiler()

lp_wrapper = lp(main)

lp_wrapper()

lp.print_stats()