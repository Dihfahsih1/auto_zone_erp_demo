 
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
     path('dispatch/<int:dispatch_id>/verify/', views.verify_dispatch, name='verify-dispatch'),

     #customer module
     path('register/', views.register_customer, name='register_customer'),
     path('customers/', views.customer_list, name='customer_list'),
     path('customers/<int:pk>/view/', views.customer_view, name='customer_view'),
     path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
     path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),


     #Account registration and login
     path('accounts/register/', views.register_employee, name='register'),
     path('accounts/login/', views.login_employee, name='login'),
    
]
