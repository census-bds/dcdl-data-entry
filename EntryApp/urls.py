from django.urls import path

from EntryApp import views

app_name = 'EntryApp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('begin-new-image/', views.BeginNewImageView.as_view(), name='begin-new-image'),
    path('enter-sheet-data/', views.EnterSheetData.as_view(), name='enter-sheet-data'),
    path('enter-breaker-data/', views.EnterBreakerData.as_view(), name='enter-breaker-data'),
    path('thank-you/', views.ThankYou, name='thank-you')
]