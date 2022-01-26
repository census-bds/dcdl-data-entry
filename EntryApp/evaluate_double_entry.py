#===============================================================#
# MODULE DEFINING FUNCTIONS TO FIND CONFLICTS
#===============================================================#

import pandas as pd

from EntryApp.models import Breaker
from EntryApp.models import Image
from EntryApp.models import ImageFile
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet



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


def check_matches_in_sheet_records(reel):
    '''
    Walks through a double-entered sheet in a reel checking each record for match

    Takes:
    - reel object
    Returns:
    - data frame with results for each record
    '''

    # get all the image files in the reel
    image_file_qs = ImageFile.objects.filter(img_reel_id=reel.id)

    # initialize results dict
    results = {
        'image_file': [],
        'image_id': [],
        'breaker_id': [],
        'sheet_id': [],
        'record_id': [],
        'keyer_one': [],
        'keyer_two': [],
        'num_matches': [],
        'num_checked': [],
        'mismatch': [],
        'breaker_matches': [],
        'breaker_checked': [],
        'breaker_mismatch': [],
        'sheet_matches': [],
        'sheet_checked': [],
        'sheet_mismatch': [],
        'record_matches': [],
        'record_checked': [],
        'record_mismatch': [],
    }

    # loop through to do comparison
    for image_file in image_file_qs:

        results['image_file'].append(image_file.img_file_name)

        # get records associated with this image file
        image_qs = Image.objects.filter(image_file = image_file)
        image_qs = image_qs.exclude(jbid = 'jbid123')

        # skip if we don't have exactly two entries 
        if len(image_qs) != 2:
            continue

        # get keyer info - TODO this seems suboptimal as written
        results['keyer_one'].append(image_qs[0].jbid)
        results['keyer_two'].append(image_qs[1].jbid)

        # get id info
        results['image_id'].append([image_qs[0].id, image_qs[1].id])

        # check matches
        num_matches, num_fields, mismatch = compute_match(image_qs)
        results['num_matches'].append(num_matches)
        results['num_checked'].append(num_fields)
        results['mismatch'].append(mismatch)

        # if the image types don't agree, move on to next image file
        if image_qs[0].image_type != image_qs[1].image_type:

            # make all additional results columns blank
            results['breaker_matches'].append('')
            results['breaker_checked'].append('')
            results['breaker_mismatch'].append([])
            results['sheet_matches'].append('')
            results['sheet_checked'].append('')
            results['sheet_mismatch'].append([])
            results['record_matches'].append('')
            results['record_checked'].append('')
            results['record_mismatch'].append([])

            continue

        elif image_qs[0].image_type == "other":

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
            results['num_matches'].append('')
            results['num_checked'].append('')
            results['mismatch'].append([])
            results['sheet_matches'].append('')
            results['sheet_checked'].append('')
            results['sheet_mismatch'].append([])



        elif image_qs[0].image_type == "sheet":

            # look at the sheet mismatches
            sheet_qs = Sheet.objects.filter(img__in = (image_qs[i].id for i in range(len(image_qs))))
            sheet_matches, sheet_checked, sheet_mismatches = compute_match(sheet_qs)    

            # add to results and make breakers blank
            results['sheet_matches'].append(sheet_matches)
            results['sheet_checked'].append(sheet_checked)
            results['sheet_mismatch'].append(sheet_mismatches)
            results['breaker_matches'].append('')
            results['breaker_checked'].append('')
            results['breaker_mismatch'].append([])
            

            # now look for the record mismatches
            record_keyer_one_qs = Record.objects.filter(sheet = sheet_qs[0])
            record_keyer_two_qs = Record.objects.filter(sheet = sheet_qs[1])
        
            # some kind of tuple data structure?
            for record_one, record_two in zip(record_keyer_one_qs, record_keyer_two_qs):

                record_qs = Record.objects.filter(id__in=(record_one.id, record_two.id))
                record_match, record_checked, record_mismatches = compute_match(record_qs)

                # record matches
                results['record_matches'].append(record_match)
                results['record_checked'].append(record_checked)
                results['record_mismatch'].append(record_mismatches)

                # and make other entries blank
                results['num_matches'].append('')
                results['num_checked'].append('')
                results['mismatch'].append([])
                results['sheet_matches'].append('')
                results['sheet_checked'].append('')
                results['sheet_mismatch'].append([])
                results['breaker_matches'].append('')
                results['breaker_checked'].append('')
                results['breaker_mismatch'].append([])



    return results

    results = check_matches_in_sheet_records(r)
