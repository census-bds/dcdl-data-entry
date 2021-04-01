import csv

from django.contrib import admin
from django.http import HttpResponse

from djqscsv import render_to_csv_response

from .models import Breaker, Image, OtherImage, Record, Sheet


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
admin.site.register(Image)
admin.site.register(OtherImage)
admin.site.register(Record)
admin.site.register(Sheet)

admin.site.add_action(export_to_csv, 'export_to_csv')