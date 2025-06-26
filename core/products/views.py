from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, Business, Wishlist, Notification
from .forms import ProductForm, BusinessForm, ReviewForm, AddCategory 
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wishlist, Product, Order, Review,Category
from django.contrib.auth.decorators import login_required
from uuid import UUID
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, "Product added to your wishlist!")
    else:
        messages.info(request, "This product is already in your wishlist.")
    return redirect(reverse('chat:profile_detail'))

@login_required(login_url='/login/')
def add_category(request):
    if request.method == "POST":
        form = AddCategory(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, 'new category added')
            return redirect(reverse('manage_business:home'))  
    else:
        form = AddCategory()
    
    return render(request, "products/add-category.html", {"form": form})

@login_required
def add_new_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False) 
            product.seller = request.user.business 
            product.save()  
            messages.success(request, "Product added successfully!")
            return redirect('manage_business:home')  
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


@login_required(login_url='/login/')
def createBusiness(request):
    form = BusinessForm()
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        print('POST REQUEST')
        if form.is_valid():
            business = form.save(commit=False)  
            business.user = request.user
            business.save()
            print('valid form')
            messages.success(request, 'new store successfully created')
            return redirect(reverse('manage_business:home'))
        else:
            print('invalid form')
    context = {'form':form}
    return render(request, 'products/create-business.html', context)

def view_product(request, id):
    single_product = get_object_or_404(Product, pk=id)
    reviews = single_product.reviews.all()  
    form = ReviewForm(request.POST or None)

    if form.is_valid() and request.user.is_authenticated:
        review = form.save(commit=False)
        review.product = single_product
        review.user = request.user
        review.save()

    average_rating = single_product.average_rating
    keywords = single_product.product_name.split()
    query = Q()
    for word in keywords:
        query |= Q(product_name__icontains=word)
    related = Product.objects.filter(query).exclude(id=single_product.id)

    context = {
        'single_product': single_product,
        'related_product': related,
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating,  
    }
    return render(request, 'products/view-product.html', context)

@login_required(login_url='/login/')
def order_details(request, product_id):
    single_product = get_object_or_404(Product, pk=product_id)
    related_products = Product.objects.filter(product_name__icontains=single_product.product_name).exclude(id=single_product.id)
    shop = get_object_or_404(Business, pk=single_product.seller.id)

    context = {
        'single_product':single_product,
        'related_products':related_products,
        'shop':shop,
    }
    return render(request, 'products/old-order_details.html', context)

@login_required(login_url='/login/')
def place_order(request, product_id):
    product = Product.objects.get(id=product_id)
    seller = product.seller.user  
    order_quantity = request.POST.get('quantity')
    print('Quantity: '+str(order_quantity))
    order = Order.objects.create(product=product, order_quantity=order_quantity ,buyer=request.user, status="Pending")

    Notification.objects.create(
        user=seller,
        message=f"You have a new order for {product.product_name} from {request.user.first_name} {request.user.last_name}. quantity {order_quantity}"
    )
    messages.info(request, 'order placed successfully!')
    return redirect(reverse("products:success_purchase"))

@login_required(login_url='/login/')
def success_purchase(request):
    return render(request, 'products/order_sucess.html')

def show_products_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()
    all_products = products.count()
    context = {
        'category':category,
        'products':products,
        'all_products':all_products,
    }
    return render(request, 'products/view_category_product.html', context)

