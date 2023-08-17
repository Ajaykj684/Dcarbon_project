from django.urls import path
from . import views

urlpatterns =[ 
    path('',views.home_page,name='home_page'),
    path('process_image/',views.process_image,name='process_image'),
    path('map/',views.map_view,name='map'),
    path('save_destination/', views.save_destination, name='save_destination'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),

]
