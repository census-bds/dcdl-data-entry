from django.urls import path
from django.contrib.auth import views as auth_views
from EntryApp import views

from django.conf import settings

app_name = 'EntryApp'
urlpatterns = [
    path('', views.IndexView.as_view(extra_context={'app_instance': settings.APP_INSTANCE}), name='index'),
    path( 'code-image/', views.CodeImage.as_view(), name="code_image" ),
    path('report-problem/', views.report_problem, name='report_problem'),
    path('test-crispy-formset/<int:year>/<str:form_type>', views.test_crispy_formset_view, name='test_crispy_formset'),
    path('develop-household1960/', views.test_household1960_form, name='test_household_1960'),
    path('render-image/', views.render_image, name='render_image'),
]
