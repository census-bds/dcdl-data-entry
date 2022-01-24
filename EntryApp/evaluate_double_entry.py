#===============================================================#
# MODULE DEFINING FUNCTIONS TO FIND CONFLICTS
#===============================================================#

import pandas as pd
import psycopg2 as pg

from EntryApp.models import Breaker
from EntryApp.models import Image
from EntryApp.models import Record
from EntryApp.models import Sheet


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

        # skip certain fields we wouldn't expect to match
        if k is in ['id', 'jbid', 'create_date', 'last_modified',]:
            continue

        elif entries[0][k] == entries[1][k]:
            matches += 1
        
        else:
            mismatch.append(k)

    return matches, len(entries[0].keys()), mismatch


