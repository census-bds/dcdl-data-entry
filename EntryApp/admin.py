"""
WEBSITE ADMIN CUSTOMIZATION

This module contains some code to extend the Django admin page so
it is possible to do CSV export from that page and so that it's 
easier to browse certain models.
"""


import csv
import logging

from django.contrib import admin
from django.http import HttpResponse

from djqscsv import render_to_csv_response

from .models import Breaker
from .models import CurrentEntry
from .models import FormField
from .models import Image
from .models import ImageFile
from .models import Keyer
from .models import LongForm1990
from .models import OtherImage
from .models import Record
from .models import Reel
from .models import Sheet

logger = logging.getLogger(__name__)


def export_to_csv(modeladmin, request, queryset):
    '''
    Export data from a given model to csv using admin
    '''

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename="records.csv"'
    writer = csv.writer(response)

    return render_to_csv_response(queryset.values())
export_to_csv.short_description = "Export selected to csv"


admin.site.register(Breaker)
admin.site.register(LongForm1990)
admin.site.register(OtherImage)
admin.site.register(Record)
admin.site.register(Sheet)

admin.site.register( CurrentEntry )
admin.site.register( FormField )

admin.site.add_action(export_to_csv, 'export_to_csv')

# Image ImageFile inline
class Image_ImageFileInline( admin.TabularInline ):

    model = Image
    extra = 1
    fk_name = 'image_file'

    fieldsets = [
        (
            None,
            {
                'fields' : [
                    'jbid',
                    'year',
                    'image_type',
                    'is_complete',
                    'timestamp',
                    'problem',
                    'prob_description',
                    'flagged_view'
                ]
            }
        )
    ]

#-- END class Image_ImageFileInline --#

@admin.register(ImageFile)
class ImageFileAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( "File info",
            {
                'fields' : [
                    'img_path',
                    'img_file_name',
                    'img_folder_path',
                    'img_reel',
                    'img_position'
                ]
            }
        ),
        ( "Preserved from Image",
            {
                'fields' : [
                    'year',
                    'image_type',
                    'is_complete',
                    'timestamp',
                    'problem',
                    'prob_description',
                    'flagged_view'
                ],
                "classes" : ( "collapse", )
            }
        ),
    ]

    inlines = [
        Image_ImageFileInline
    ]

    list_display = ( 'id', 'img_path', 'img_position' )
    list_display_links = ( 'id', 'img_path', )
    list_filter = [ 'img_reel' ]
    search_fields = [
        'img_path',
        'img_file_name',
        'img_folder_path',
        'img_reel',
        'img_position',
        'id'
    ]
    # date_hierarchy = 'status_date'
    ordering = [ 'img_reel', 'img_position' ]

#-- END ImageFileAdmin admin class --#


@admin.register(Image)
class ImageAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'image_file' ]

    fieldsets = [
        ( "Coding",
            {
                'fields' : [
                    'image_file',
                    'jbid',
                    'year',
                    'image_type',
                    'is_complete',
                    'timestamp',
                    'problem'
                ]
            }
        ),
        ( "Problem Details",
            {
                'fields' : [
                    'prob_description',
                    'flagged_view'
                ],
                "classes" : ( "collapse", )
            }
        ),
    ]

    list_display = (
        'id',
        'jbid',
        'image_file',
        'year',
        'image_type',
        'is_complete',
        'problem',
        'last_modified'
    )
    list_display_links = ( 'id', 'image_file' )
    list_filter = [ 'is_complete', 'problem', 'image_type', 'year', 'jbid' ]
    search_fields = [
        'jbid',
        'image_file.img_path',
        'year',
        'prob_description',
        'id',
    ]
    # date_hierarchy = 'status_date'
    ordering = [ 'last_modified' ]

#-- END ImageAdmin admin class --#

# Keyer inline, with current reel displayed
@admin.register(Keyer)
class KeyerAdmin( admin.ModelAdmin ):

    list_display = (
        'id',
        'jbid',
        'reel_count',
    )


# Reel inline
@admin.register(Reel)
class ReelAdmin( admin.ModelAdmin ):

    list_display = (
        'id',
        'reel_path',
        'year',
        'image_count',
        'keyer_one',
        'keyer_two',
    )

    list_display_links = [
        'id',
        'reel_path',
        'keyer_one',
        'keyer_two',
    ]



