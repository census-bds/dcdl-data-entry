from django.urls import path
from django.contrib.auth import views as auth_views
from EntryApp import views

app_name = 'EntryApp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('report-problem/', views.report_problem, name='report_problem'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('test-crispy-formset/<int:year>', views.test_crispy_formset_view, name='test_crispy_formset'),
    path( 'code-image/', views.CodeImage.as_view(), name="code_image" )
]
