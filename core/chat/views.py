from django.shortcuts import render, get_object_or_404, redirect
from .models import Message, Profile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from random import choice
from .forms import DeliveryAddressForm, EditProfileForm, UpdateUser
from django.contrib.auth.models import auth
from django.urls import reverse
from products.models import Product,Notification, Business, Wishlist
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from products.models import Order
from products.models import Category, Product, Business, Wishlist
import random
User = get_user_model()


def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Handle checkbox: If checked, it sends 'on', otherwise it's not present
        is_seller = 'yes' if request.POST.get('is_seller') else 'no'

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse('chat:signup'))

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect(reverse('chat:signup'))
        
        if len(password) < 8:
            messages.info(request, "Password must contain at least 8 characters.")
            return redirect(reverse('chat:signup'))
        
        user = User.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_seller=is_seller
        )
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect(reverse('chat:login'))
    
    return render(request, 'chat/temp-signup.html')

def login_view(request):
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if Business.objects.filter(user=user).exists():
                return redirect(reverse('manage_business:home'))
            else:
                return redirect(reverse('chat:home'))
        else:
            messages.error(request, "Invalid email or password.")
            return redirect(reverse('chat:login'))
    return render(request, 'chat/temp_login.html')

def landingPage(request):
    products = Product.objects.order_by('?')[:10]
    categories = Category.objects.order_by('?')
    query = request.GET.get('q', '')
    results = Product.objects.filter(product_name__icontains=query) if query else []
    new_arrivals = Product.objects.all().order_by("-created_at")[:4]
    
    context = {
        'query':query,
        'products':products,
        'results':results,
        'categories':categories,
        'new_arrivals':new_arrivals
    }
    return render(request, 'chat/landing_page.html', context)

@login_required(login_url='/login/')
def home(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).aggregate()
    products = Product.objects.all()
    users_with_business = User.objects.filter(business__isnull=False)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    results = Product.objects.filter(product_name__icontains=query) if query else []
    new_arrivals = Product.objects.all().order_by("-created_at")[:4]
    
    context = {
        'query':query,
        'products':products,
        'has_business':users_with_business,
        'results':results,
        'unread_notifications': unread_notifications,
        'categories':categories,
        'new_arrivals':new_arrivals
    }
    return render(request, 'chat/home.html', context)

@login_required(login_url='/login/')
def error_page(request):
    return render(request, 'chat/404error.html')

@login_required(login_url='/login/')
def about_page(request):
    return render(request, 'chat/about.html')

# @login_required(login_url='/login/')
# def conversation(request, chat_id=None):
#     from django.db.models import Max, Q

#     # Filter users to include only those with whom the logged-in user has a conversation
#     users = User.objects.filter(
#         Q(received_messages__sender=request.user) | Q(sent_messages__receiver=request.user)
#     ).distinct()

#     # Annotate each user with the latest message timestamp
#     users = users.annotate(
#         latest_message_time=Max(
#             'received_messages__timestamp',
#             filter=Q(received_messages__sender=request.user) | Q(sent_messages__receiver=request.user)
#         )
#     ).order_by('-latest_message_time')

#     # Search functionality
#     search_query = request.GET.get('search_user')
#     if search_query:
#         users = users.filter(first_name__icontains=search_query)

#     # Chat logic
#     current_user = None
#     messages = []
#     last_messages = {}
#     if chat_id:
#         current_user = get_object_or_404(User, id=chat_id)
#         if request.method == 'POST':
#             content = request.POST.get('content')
#             if content:
#                 Message.objects.create(sender=request.user, receiver=current_user, content=content)

#         # Fetch messages between the logged-in user and the selected user
#         messages = Message.objects.filter(
#             Q(sender=request.user, receiver=current_user) | Q(sender=current_user, receiver=request.user)
#         ).order_by('timestamp')

#     # Retrieve the last message for each user
#     for user in users:
#         last_message = Message.objects.filter(
#             Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
#         ).order_by('-timestamp').first()
#         last_messages[user.id] = last_message

#     context = {
#         'users': users,
#         'user_profile': users,
#         'current_user': current_user,
#         'messages': messages,
#         'last_message': last_messages,
#     }

#     return render(request, 'chat/conversation.html', context)

@login_required(login_url='/login/')
def conversation(request, chat_id=None):
    from django.db.models import Max, Q
    from django.utils.timezone import now

    users = User.objects.filter(
        Q(received_messages__sender=request.user) | Q(sent_messages__receiver=request.user)
    ).distinct()

    users = users.annotate(
        latest_message_time=Max(
            'received_messages__timestamp',
            filter=Q(received_messages__sender=request.user) | Q(sent_messages__receiver=request.user)
        )
    ).order_by('-latest_message_time')

    search_query = request.GET.get('search_user')
    if search_query:
        users = users.filter(first_name__icontains=search_query)

    current_user = None
    messages = []
    last_messages = {}

    if chat_id:
        current_user = get_object_or_404(User, id=chat_id)
        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                Message.objects.create(sender=request.user, receiver=current_user, content=content)

        messages = Message.objects.filter(
            Q(sender=request.user, receiver=current_user) | Q(sender=current_user, receiver=request.user)
        ).order_by('timestamp')

        # Check if user is offline and send an auto-message
        if not current_user.profile.is_online():
            auto_message = "Hello! I'm currently offline. I'll get back to you soon."
            Message.objects.create(sender=current_user, receiver=request.user, content=auto_message)

    for user in users:
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()
        last_messages[user.id] = last_message

    context = {
        'users': users,
        'user_profile': users,
        'current_user': current_user,
        'messages': messages,
        'last_message': last_messages,
    }

    return render(request, 'chat/conversation.html', context)


@login_required(login_url='/login/')
def get_unread_messages_count(request):
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({"count": unread_count})

@login_required(login_url='/login/')
def mark_messages_read(request):
    Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "success"})

@login_required(login_url='/login/')
def edit_address(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = DeliveryAddressForm()
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('chat:profile_detail'))
    else:
        form = DeliveryAddressForm(instance=profile)
    return render(request, 'chat/edit_address.html', {'form': form})

@login_required(login_url='/login/')
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('chat:profile_detail'))
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'chat/edit_profile.html', {'form': form})

@login_required(login_url='/login/')
def profile_detail(request):
    business = Business.objects.all()
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    user  = request.user
    profile = get_object_or_404(Profile, user=request.user)
    order_history = Order.objects.filter(buyer = user)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    read_notifications = Notification.objects.filter(user=request.user, is_read=True).order_by('-created_at')

    # Mark unread notifications as read
    unread_notifications.update(is_read=True)

    context = { 
        'profile':profile,
        'user':user,
        'wishlist':wishlist_items,
        'order_history':order_history,
        "unread_notifications": unread_notifications,
        "read_notifications": read_notifications
    }
    return render(request, 'chat/profile_detail.html',context)

@login_required(login_url='/login/')
def help(request):
    return render(request, 'chat/help.html')

@login_required(login_url='/login/')
def update_user(request, id):
    instance = get_object_or_404(User, pk=id)
    if request.method == 'POST':
        form = UpdateUser(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('chat:profile_detail'))
    else:
        form = UpdateUser(instance=instance)

    context = {'form':form}
    return render(request, 'chat/update-user.html', context)

@login_required(login_url='/login/')
def mark_notifications_read(request):
    if request.method == "POST":
        # Fetch unread notifications
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        
        # Get notification data for the response
        notifications_list = list(notifications.values("id", "message", "created_at"))

        # Mark notifications as read
        notifications.update(is_read=True)

        # Return the notifications and success message
        return JsonResponse({"message": "Notifications marked as read", "notifications": notifications_list})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return JsonResponse({"count": notifications.count()})

@login_required
def buyer_notification(request):
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    read_notifications = Notification.objects.filter(user=request.user, is_read=True).order_by('-created_at')
    
    # Mark unread notifications as read
    unread_notifications.update(is_read=True)

    return render(request, "chat/buyer_notification.html", {
        "unread_notifications": unread_notifications,
        "read_notifications": read_notifications
    })




