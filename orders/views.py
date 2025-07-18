from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Supplier, Order, Product
from django.http import JsonResponse
from .forms import OrderForm
import boto3
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from uuid import uuid4
from utils.sqs import send_order_event
from utils.sns import subscribe_user_email_to_sns
from .forms import CustomUserCreationForm
from ordercost.ordercost import OrderCostCalculator

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            subscribe_user_email_to_sns(user.email)

            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'orders/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'orders/home.html')

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'orders/supplier_list.html', {'suppliers': suppliers})

@login_required
def order_list(request):

    if request.user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)  # ← filter by current user
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def place_order(request):
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'Placed'

            # Handle image upload to S3
            image_file = request.FILES.get('reference_image')
            if image_file:
                s3 = boto3.client('s3')
                filename = f'reference_images/{uuid4()}_{image_file.name}'
                s3.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, filename)

                # Construct public URL
                order.reference_image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"

            order.save()
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'orders/place_order.html', {'form': form, 'suppliers': suppliers})


@login_required
def update_order_status(request, order_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()

        send_order_event(order, new_status)

        messages.success(request, f"Order #{order.id} status updated to '{new_status}'.")

    return redirect('order_list')

@login_required
def edit_reference_image(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST' and request.FILES.get('reference_image'):
        image_file = request.FILES['reference_image']
        s3 = boto3.client('s3')
        filename = f'reference_images/{uuid4()}_{image_file.name}'
        s3.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, filename)
        order.reference_image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
        order.save()
        return redirect('order_list')

    return render(request, 'orders/edit_reference_image.html', {'order': order})

@login_required
def load_products(request):
    supplier_id = request.GET.get('supplier')
    products = Product.objects.filter(supplier_id=supplier_id).values('id', 'name')
    return JsonResponse(list(products), safe=False)

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "Placed":
        return HttpResponseForbidden("You can only delete orders that are in 'Placed' status.")

    if request.method == 'POST':
        order.delete()
        messages.success(request, f"Order #{order_id} has been deleted.")
        return redirect('order_list')

    return render(request, 'orders/confirm_delete.html', {'order': order})

def order_cost_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    calc = OrderCostCalculator(
        price_per_unit=order.product.price_per_unit,
        quantity=order.quantity,
        tax_percent=0,          
        discount_percent=0
    )

    cost = calc.breakdown()

    return render(request, 'orders/order_cost_summary.html', {
        'order': order,
        'cost': cost
    })