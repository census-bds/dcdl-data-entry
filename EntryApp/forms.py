from django import forms 
from EntryApp.models import Breaker, Image, Record, Sheet



class ImageForm(forms.ModelForm):
    """
    Form where user records the year and form type to which a sheet belongs 
    """

    class Meta:
        model = Image
        fields = ['year', 'image_type']
    
    def form_valid(self, form):
        return True


# class GetNewSheetForm(forms.Form):
#     """
#     Define form to look up new image in DB to enter
#     """
    
#     class Meta:
#         model = Sheet
#         fields = []