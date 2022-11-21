import sys
from line_profiler import LineProfiler

from fit_test import main

lp = LineProfiler()

lp_wrapper = lp(main)

lp_wrapper()

lp.print_stats()