from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, Business, Notification
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from products.models import Order, Notification, Business, Product
from django.db import models

@login_required
def seller_dashboard(request):
    if request.user.is_authenticated:
        products = Product.objects.filter(seller__user=request.user).order_by('-created_at')
    else:
        products = Product.objects.none()
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    orders = Order.objects.filter(product__seller__user=request.user)

    context = {
        "orders": orders,
        "notifications": notifications,
        'products':products
    }
    
    return render(request, "manage_business/seller_dashboard.html", context)
@login_required
def accept_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Accepted"
    order.save()
    print(f"Order Accepted by Seller: {request.user.username}")  
    print(f"Buyer: {order.buyer.username}") 
    Notification.objects.create(
        user=order.buyer,
        message=f"Your order for {order.product.product_name} has been accepted."
    )
    return redirect(reverse('manage_business:home'))

@login_required(login_url='/login/')
def reject_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Rejected"
    order.save()

    # Notify buyer
    Notification.objects.create(
        user=order.buyer,
        message=f"Your order for {order.product.product_name} has been rejected."
    )
    return redirect(reverse('manage_business:home'))

@login_required(login_url='/login/')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_business:home')



