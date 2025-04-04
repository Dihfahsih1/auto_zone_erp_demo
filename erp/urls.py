 
from django.contrib import admin
from django.urls import path,include 
from . import views

urlpatterns = [
     path('', views.dashboard, name='dashboard'),
     path('dispatches/', views.dispatch_list_view, name='dispatch_list'),
     path('dispatch/mark-delivered/', views.dispatch_view, name='mark_dispatch_delivered'),
     path('dispatch/<int:dispatch_id>/mark-delivered/', views.mark_delivered, name='mark_delivered'),
     path('delivery/upload/', views.upload_delivery_note, name='upload_delivery_note'),
     path('delivery/notes/', views.delivery_note_list, name='delivery_note_list'),
     path('record/', views.record_estimate, name='record_estimate'),
     path('list/', views.list_estimates, name='list_estimates'),
      path('download-template/', views.download_estimate_template, name='download_estimate_template'),
    
]
