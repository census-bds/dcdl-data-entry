from django.urls import path

from EntryApp import views

app_name = 'EntryApp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('get-next-image/', views.get_next_image, name='get-next-image'),
    path('image/', views.EnterImage.as_view(), name='image'),
    path('image/<int:pk>', views.EnterImage.as_view(), name='image'),
    path('enter-image/<int:pk>', views.enter_image, name='enter-image'),
    path('enter-sheet-data/', views.EnterSheetData.as_view(), name='enter-sheet-data'),
    path('enter-breaker-data/', views.EnterBreakerData.as_view(), name='enter-breaker-data'),
    # path('enter-breaker-data/<int:img_path>', views.EnterBreakerData.as_view(), name='enter-breaker-data'),
    path('thank-you/', views.ThankYou, name='thank-you')
]