from django.urls import path
from django.contrib.auth import views as auth_views
from EntryApp import views

app_name = 'EntryApp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('begin-new-image/', views.BeginNewImageView.as_view(), name='begin_new_image'),
    path('submit-image/', views.submit_image, name="submit_image"),
    path('submit-breaker/', views.submit_breaker, name="submit_breaker"),
    path('submit-sheet/', views.submit_sheet, name="submit_sheet"),
    path('enter-sheet-data/', views.EnterSheetData.as_view(), name='enter_sheet_data'),
    path('enter-breaker-data/', views.EnterBreakerData.as_view(), name='enter_breaker_data'),
    path('enter-records', views.enter_records, name='enter_records')
]