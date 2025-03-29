from django.urls import path
from . import views

app_name = 'manage_business'

urlpatterns = [
    path('seller/dashboard/', views.seller_dashboard, name='home'),
    path('order/accept/<int:order_id>/', views.accept_order, name='accept_order'),
    path('order/reject/<int:order_id>/', views.reject_order, name='reject_order'),
    path('delete-product/<uuid:product_id>/', views.delete_product, name='delete_product'),
]

























