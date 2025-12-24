from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('tenant/', tenant_dashboard, name='tenant_dashboard'),
    path('request/<int:property_id>/', send_request, name='send_request'),
    path('owner/requests/', owner_requests, name='owner_requests'),
    path('pay/<int:booking_id>/', initiate_payment, name='initiate_payment'),
    path('payment-success/', payment_success, name='payment_success'),
    path('property/<int:pk>/', property_detail, name='property_detail'),
    path('request/update/<int:request_id>/<str:status>/', update_request, name='update_request'),
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
   
    path('add-property/', views.add_property, name='add_property'),
    path('request/<int:property_id>/', send_request, name='send_request'),
path('pay/<int:booking_id>/', initiate_payment, name='initiate_payment'),
  
]


