from django.urls import path
from energy_consumption import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data_upload/', views.data_upload, name='data_upload'),
    path('buildings/', views.buildings, name='buildings'),
    path('buildings/<int:pk>', views.building_detail, name='buildings_detail'),
    path('meters/', views.meters, name='meters'),
    path('meters/<int:pk>', views.meter_detail, name='meters_detail'),
    path('meter_readings/', views.meter_readings, name='meter_readings'),
    path('water_chart/', views.water_chart, name='water_chart'),
]