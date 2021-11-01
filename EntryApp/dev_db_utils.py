#===============================================================#
# METHODS FOR WORKING WITH DB (DEV)
#===============================================================#

# EntryApp models
from EntryApp.models import Breaker
from EntryApp.models import CurrentEntry
from EntryApp.models import FormField
from EntryApp.models import Image
from EntryApp.models import ImageFile
from EntryApp.models import Keyer
from EntryApp.models import LongForm1990
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet


def move_keyer_back_one(this_keyer):
    '''
    Convenience method to undo last entry

    Takes: keyer object
    Returns: None
    '''
    current = CurrentEntry.objects.get(jbid = this_keyer.jbid)

    # get the previous image
    image_qs = Image.objects.filter(image_file__img_reel = current.reel)
    user_image_qs = image_qs.filter(jbid = this_keyer.jbid)
    completed_image_qs = user_image_qs.filter(is_complete = True)
    last_image = completed_image_qs.order_by('-id')[:1].get()

    # use it to get the associated image file
    last_image_file = ImageFile.objects.get(id = last_image.image_file.id)

    # now delete data in the image
    last_image.image_type = None
    last_image.is_complete = False
    last_image.problem = None
    
    # UGH but there is also data in Sheet, Breaker, Other, and Record, oyyy


    # set image file and image pointers in CurrentEntry
    # also change batch_position, same table
    # delete the data associated with the image that was entered - so, delete + recreate?

    