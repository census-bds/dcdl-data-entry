#===============================================================#
# MODULE DEFINING FUNCTIONS TO FIND CONFLICTS
#===============================================================#

from EntryApp import Image, Breaker, Sheet, Record


def compare_breaker_entries(userA, userB):
    '''
    Compare data for breakers
    '''

    fields = Breaker._meta.get_fields()

    # define the records to compare 
    rows_A = Breaker.objects.filter(jbid=userA).filter(is_complete=True).order_by('img__img_path')
    rows_B = Breaker.objects.filter(jbid=userB).filter(is_complete=True).order_by('img__img_path')

    return rows_A, rows_B
    


def check_for_conflicts():
    '''
    Walk through data records in tables to check that values match for each jbid
    '''