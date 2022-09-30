#===============================================================#
# HELPER METHODS FOR TESTING
#===============================================================#

from django.forms import formset_factory

from EntryApp.models import Breaker

### FORMSETS ###
# from https://stackoverflow.com/questions/1630754/django-formset-unit-test

def build_formset_form_data(form_number, **data):
    form = {}
    for key, value in data.items():
        form_key = f"form-{form_number}-{key}"
        form[form_key] = value
    return form

def build_formset_data(forms, **common_data):
    formset_dict = {
        "form-TOTAL_FORMS": [f"{len(forms)}", f"{len(forms)}"],
        "form-MAX_NUM_FORMS": ["1000", "1000",],
        "form-INITIAL_FORMS": ["1", "1", ]
    }
    formset_dict.update(common_data)
    for i, form_data in enumerate(forms):
        form_dict = build_formset_form_data(form_number=i, **form_data)
        formset_dict.update(form_dict)
    return formset_factory(form_kwargs=formset_dict)

# from https://stackoverflow.com/questions/1630754/django-formset-unit-test/64354805#64354805
# modified to handle no initial data
def create_formset_post_data(response, new_form_data=None):
    if new_form_data is None:
        new_form_data = []
    csrf_token = response.context['csrf_token']
    formset = response.context['formset']
    prefix_template = formset.empty_form.prefix  # default is 'form-__prefix__'
    
    # extract initial formset data if present
    management_form_data = formset.management_form.initial
    if formset.initial:
        form_data_list = formset.initial  # this is a list of dict objects
        # add new form data and update management form data
        form_data_list.extend(new_form_data)
    else:
        form_data_list = new_form_data
        
    # management_form_data['TOTAL_FORMS'] = [len(form_data_list), len(form_data_list)]
    # initialize the post data dict...
    post_data = dict(csrfmiddlewaretoken=[csrf_token, csrf_token])
    # add properly prefixed management form fields
    for key, value in management_form_data.items():
        prefix = prefix_template.replace('__prefix__', '')
        post_data[prefix + key] = [value]
        post_data[prefix + key].append(value)
    # add properly prefixed data form fields
    for index, form_data in enumerate(form_data_list):
        for key, value in form_data.items():
            prefix = prefix_template.replace('__prefix__', f'{index}-')
            post_data[prefix + key] = value
    return post_data