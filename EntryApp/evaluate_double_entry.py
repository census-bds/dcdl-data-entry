#===============================================================#
# MODULE DEFINING FUNCTIONS TO FIND CONFLICTS
#===============================================================#

import numpy as np
import pandas as pd

from EntryApp.models import Breaker
from EntryApp.models import Image
from EntryApp.models import ImageFile
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet


RESULTS_KEYS = [
        'image_file', 'image_id', 'breaker_id', 'sheet_id', \
        'record_id', 'keyer_one', 'keyer_two', 'image_matches', \
        'image_checked', 'image_mismatch', 'breaker_matches', \
        'breaker_checked', 'breaker_mismatch', 'sheet_matches', \
        'sheet_checked', 'sheet_mismatch', 'record_matches', \
        'record_checked', 'record_mismatch'
        ]


def compute_match(queryset, **kwargs):
    '''
    Check values in double-entered records: % match and mismatched fields 
    CURRENTLY ASSUMES ONLY TWO ENTRY VALUES, SO CHECK FOR THAT FIRST

    Takes:
    - queryset of data model objects
    - keyword args for filtering
    Returns:
    - # values that match
    - # values total
    - list of mismatched fields
    '''

    # filter more if desired
    entries = queryset.filter(**kwargs).values()

    num_matches = 0
    mismatch = []
    for k in entries[0].keys():

        # skip certain fields we wouldn't expect to match
        fields_to_skip = ['id', 'jbid', 'create_date', 'last_modified',
                        'img_id', 'breaker_id', 'timestamp', ]
        if k in fields_to_skip:
            continue

        elif entries[0][k] == entries[1][k]:
            num_matches += 1
        
        else:
            mismatch.append(k)

    num_fields_checked = len(entries[0].keys()) - len(fields_to_skip)

    return num_matches, num_fields_checked, mismatch

#TODO: rename or eliminate
def check_matches_in_reel(reel):
    '''
    Walks through a double-entered reel checking each image file for match

    Takes:
    - Reel object
    Returns:
    - data frame with comparison for each image, sheet, and record
    '''

    # get all the image files in the reel
    image_file_qs = ImageFile.objects.filter(img_reel_id=reel.id)

    # initialize results dict
    results = {
        'image_file': [],
        'keyer_one': [],
        'keyer_two': [],
        'num_matches': [],
        'num_fields': [],
        'mismatch': [],
    }

    # loop through to do comparison
    for image_file in image_file_qs:

        results['image_file'].append(image_file.img_file_name)

        # get images associated with this image file
        image_qs = Image.objects.filter(image_file = image_file)
        image_qs = image_qs.exclude(jbid='jbid123')

        # skip if we don't have exactly two entries 
        if len(image_qs) != 2:
            continue

        # get keyer info - TODO this seems suboptimal as written
        results['keyer_one'].append(image_qs[0].jbid)
        results['keyer_two'].append(image_qs[1].jbid)

        # check matches
        num_matches, num_fields, mismatch = compute_match(image_qs)
        results['num_matches'].append(num_matches)
        results['num_fields'].append(num_fields)
        results['mismatch'].append(mismatch)

    return pd.DataFrame.from_dict(results)


def append_blanks(d, fields):
    '''
    Appends empty string to every specified field in dict

    Takes:
    - results dictionary
    - optional list of fields to subset to
    Returns:
    - updated dictionary
    '''

    for f in fields:
        d[f].append('')

    return d


def clean_results_df(results_df):
    '''
    Fill down the blank values in results df

    Takes:
    - results df
    Returns:
    - results df with missing filled in
    '''

    df = results_df.replace({'': np.nan })
    return df.fillna(method="ffill")


def check_matches_in_sheet_records(reel):
    '''
    Walks through a double-entered sheet in a reel checking each record for match

    Takes:
    - reel object
    Returns:
    - data frame with results for each record
    '''

    # initialize results dict
    results = {k: [] for k in RESULTS_KEYS}
    row_count = 0

    # get all the image files in the reel
    image_file_qs = ImageFile.objects.filter(img_reel_id=reel.id)

    # loop through to do comparison
    for image_file in image_file_qs:

        row_count +=1

        # get records associated with this image file
        image_qs = Image.objects.filter(image_file = image_file)
        image_qs = image_qs.exclude(jbid = 'jbid123')

        # skip if we don't have exactly two entries 
        # if len(image_qs) != 2:
        #     continue

        # get image  info - TODO this seems suboptimal as written
        results['image_file'].append(image_file.img_file_name)
        results['keyer_one'].append(image_qs[0].jbid)
        results['keyer_two'].append(image_qs[1].jbid)
        results['image_id'].append([image_qs[0].id, image_qs[1].id])

        # check matches
        num_matches, num_fields, mismatch = compute_match(image_qs)
        results['image_matches'].append(num_matches)
        results['image_checked'].append(num_fields)
        results['image_mismatch'].append(mismatch)

        

        # if the image types don't agree, move on to next image file
        if image_qs[0].image_type != image_qs[1].image_type:

            print("Case 1")

            # make all additional results columns blank
            blank_fields = [
                'breaker_id', 'sheet_id', 'record_id',
                'breaker_matches', 'breaker_checked', 'breaker_mismatch',
                'sheet_matches', 'sheet_checked', 'sheet_mismatch',
                'record_matches', 'record_checked', 'record_mismatch',
            ]
            results = append_blanks(results, blank_fields)
            continue

        elif image_qs[0].image_type == "other":

            blank_fields = [
                'breaker_id', 'sheet_id', 'record_id',
                'breaker_matches', 'breaker_checked', 'breaker_mismatch',
                'sheet_matches', 'sheet_checked', 'sheet_mismatch',
                'record_matches', 'record_checked', 'record_mismatch',
            ]
            results = append_blanks(results, blank_fields)
            continue

        elif image_qs[0].image_type == "breaker":

            # get breaker mismatches and add to results
            breaker_qs = Breaker.objects.filter(img__in = (image_qs[i].id for i in range(len(image_qs))))
            breaker_matches, breaker_checked, breaker_mismatches = compute_match(breaker_qs)    

            results['breaker_matches'].append(breaker_matches)
            results['breaker_checked'].append(breaker_checked)
            results['breaker_mismatch'].append(breaker_mismatches)

            # get id info
            results['breaker_id'].append([breaker_qs[0].id, breaker_qs[1].id])


            # make the irrelevant results columns blank
            blank_fields = [
                'sheet_id', 'record_id',
                'sheet_matches', 'sheet_checked', 'sheet_mismatch',
                'record_matches', 'record_checked', 'record_mismatch',
            ]
            results = append_blanks(results, blank_fields)
            continue


        elif image_qs[0].image_type == "sheet":

            blank_fields = [
                'breaker_id', 'sheet_id', 'record_id',
                'breaker_matches', 'breaker_checked', 'breaker_mismatch',
                'sheet_matches', 'sheet_checked', 'sheet_mismatch',
                'record_matches', 'record_checked', 'record_mismatch',

            ]
            results = append_blanks(results, fields=blank_fields)

            row_count +=1

            # look at the sheet mismatches
            sheet_qs = Sheet.objects.filter(img__in = (image_qs[i].id for i in range(len(image_qs))))
            sheet_matches, sheet_checked, sheet_mismatches = compute_match(sheet_qs)    

            # add to results and make breakers blank
            results['sheet_id'].append([sheet_qs[0].id, sheet_qs[1].id])
            results['sheet_matches'].append(sheet_matches)
            results['sheet_checked'].append(sheet_checked)
            results['sheet_mismatch'].append(sheet_mismatches)
            
            blank_fields = [
                'image_file', 'image_id', 'keyer_one', 'keyer_two',
                'image_matches', 'image_checked', 'image_mismatch',
                'breaker_id', 'record_id',
                'breaker_matches', 'breaker_checked', 'breaker_mismatch',
                'record_matches', 'record_checked', 'record_mismatch',
            ]
            results = append_blanks(results, fields=blank_fields)            

            # now look for the record mismatches
            record_keyer_one_qs = Record.objects.filter(sheet = sheet_qs[0])
            record_keyer_two_qs = Record.objects.filter(sheet = sheet_qs[1])
        
            # some kind of tuple data structure?
            for record_one, record_two in zip(record_keyer_one_qs, record_keyer_two_qs):

                row_count +=1

                record_qs = Record.objects.filter(id__in=(record_one.id, record_two.id))
                record_match, record_checked, record_mismatches = compute_match(record_qs)

                # record matches
                results['record_id'].append([record_qs[0].id, record_qs[1].id])
                results['record_matches'].append(record_match)
                results['record_checked'].append(record_checked)
                results['record_mismatch'].append(record_mismatches)

                blank_fields = [
                    'image_file', 'image_id', 'keyer_one', 'keyer_two',
                    'image_matches', 'image_checked', 'image_mismatch',
                    'breaker_id', 'sheet_id',
                    'breaker_matches', 'breaker_checked', 'breaker_mismatch',
                    'sheet_matches', 'sheet_checked', 'sheet_mismatch',
                ]
                results = append_blanks(results, fields=blank_fields)

    results_df = pd.DataFrame.from_dict(results)
    results_df = clean_results_df(results_df)

    return results_df #,  row_count



## code for shell
# from EntryApp.models import Reel, ImageFile, Image, Breaker, Sheet, Record, OtherImage
# import EntryApp.evaluate_double_entry as eval
# r = Reel.objects.all()[0]
# results_df = eval.check_matches_in_sheet_records(r)
