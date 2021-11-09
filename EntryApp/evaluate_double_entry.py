#===============================================================#
# MODULE DEFINING FUNCTIONS TO FIND CONFLICTS
#===============================================================#

import unittest

from EntryApp import Image, Breaker, Sheet, Record


def test_dbl_records(model, **kwargs):
    '''
    Assert that there are exactly two records for each unique observation
    '''
    return len(model.objects.filter(**kwargs)) == 2


def compute_match(model, **kwargs):
    '''
    Check values in double-entered records: % match and mismatched fields 
    CURRENTLY ASSUMES ONLY TWO ENTRY VALUES, SO CHECK FOR THAT FIRST

    Takes:
    - Model (e.g. Image, Sheet, Breaker)
    - keyword args for filtering
    Returns:
    - # values that match
    - # values total
    - list of mismatched fields
    '''

    entries = model.objects.filter(**kwargs).values()

    matches = 0
    mismatch = []
    for k in entries[0].keys():

        if entries[0][k] == entries[1][k]:
            matches += 1
        else:
            mismatch.append(k)

    return matches, len(entries[0].keys()), mismatch


