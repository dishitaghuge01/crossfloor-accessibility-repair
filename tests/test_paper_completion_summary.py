"""Regression for feasible heuristic runs disappearing from paper timings."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_revised_master import completed_time_summary


def test_feasible_greedy_time_is_reported_without_optimality_claim():
    rows=[dict(solver='greedy-improved',status='feasible',function_seconds=t) for t in [2.,1.,3.]]
    rows+=[dict(solver='greedy-improved',status='timeout',function_seconds=None)]
    assert completed_time_summary(rows,'greedy-improved')=='2.0000 [1.0000,3.0000]'


def test_failed_attempts_are_identified_not_given_a_completion_time():
    rows=[dict(solver='greedy-improved',status='timeout',function_seconds=None) for _ in range(3)]
    assert completed_time_summary(rows,'greedy-improved')=='3 timeout'


def test_exact_and_heuristic_failures_do_not_get_conflated():
    rows=[dict(solver='compressed',status='infeasible',function_seconds=.25),
          dict(solver='greedy-improved',status='heuristic_failed',function_seconds=.5)]
    assert completed_time_summary(rows,'compressed')=='0.2500 [0.2500,0.2500]'
    assert completed_time_summary(rows,'greedy-improved')=='1 heuristic failed'
