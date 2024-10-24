"""
Comparators

These tools enable quick comparison of sets of exchanges to see if they match
"""
from math import isclose


def _rx_key(rx):
    return rx.process.external_ref, rx.flow.external_ref, rx.direction


def _exch_key(exch):
    return exch.flow.external_ref, exch.direction, tuple(exch.termination)


def compare_ref_exchanges(s1, s2):
    """
    Tests qualitative equivalence of two sets of *reference* exchanges (process, flow, direction).
    :param s1:
    :param s2:
    :return:
    """
    set1 = {_rx_key(s) for s in s1}
    set2 = {_rx_key(s) for s in s2}
    d1 = set1.difference(set2)
    d2 = set2.difference(set1)
    if len(d1) + len(d2) == 0:
        print('PASS (%d)' % len(set1))
    else:
        print('DIFFERENT (%d,%d / %d)' % (len(d1), len(d2), len(set1)))
    return d1, d2


def compare_exchanges(s1, s2):
    """
    Tests qualitative equivalence of two sets of *depenedent* exchanges (flow, direction, termination).
    Returns two sets: those present only in s1, those present only in s2
    :param s1:
    :param s2:
    :return:
    """
    set1 = {_exch_key(s) for s in s1}
    set2 = {_exch_key(s) for s in s2}
    d1 = set1.difference(set2)
    d2 = set2.difference(set1)
    if len(d1) + len(d2) == 0:
        print('PASS (%d)' % len(set1))
    else:
        print('DIFFERENT (%d,%d / %d)' % (len(d1), len(d2), len(set1)))
    return d1, d2


def compare_exchange_values(s1, s2, rel_tol=1e-6):
    """
    The exchanges are unordered, so it's nontrivial to test two sets of results against one another.
    We use the approach of mapping (flow.external_ref, direction, termination) to exchange value.
    This is a summary test that compares the two sets and returns the entries in s2 that do NOT match
    the entry in s1 (key error qualifies as nonmatch)
    Thus a return value of length 0 indicates a passed test.
    :param s1:
    :param s2:
    :param rel_tol: default 1e-6
    :return: a list of failed exchanges, expressed as 2-tuples: (bad_exch, good_val) or (bad_exch, None)
    """
    c = {_exch_key(x): x.value for x in s1}
    fail = []
    for s in s2:
        try:
            v = c[_exch_key(s)]
            if not isclose(v, s.value, rel_tol=rel_tol):
                fail.append((s, v))
        except KeyError:
            fail.append((s, None))
    if len(fail) == 0:
        print('PASS (%d)' % len(c))
    else:
        print('DIFFERENT (%d / %d)' % (len(fail), len(c)))
    return fail
