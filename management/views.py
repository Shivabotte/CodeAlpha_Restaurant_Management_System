from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MenuItem
import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from .models import MenuItem, Order, OrderItem
# Create your views here.
def home(req):
    from django.shortcuts import render
from .models import MenuItem

def home(request):
    menu_items = MenuItem.objects.all()

    return render(request, 'management/home.html', {
        'menu_items': menu_items
    })
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django import forms

from .models import MenuItem, Order, OrderItem


def place_order(request):
    available_items = MenuItem.objects.filter(is_available=True)

    if request.method == 'POST':
        menu_item_id = request.POST.get('menu_item')
        quantity_text = request.POST.get('quantity', '')

        try:
            quantity = int(quantity_text)
            if quantity < 1 or quantity > 100:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Enter a quantity between 1 and 100.')
            return redirect('place_order')

        menu_item = available_items.filter(
            id=menu_item_id
        ).first()

        if menu_item is None:
            messages.error(request, 'Please select an available menu item.')
            return redirect('place_order')

        with transaction.atomic():
            total = menu_item.price * quantity

            order = Order.objects.create(
                total_amount=total,
                status='pending'
            )

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                unit_price=menu_item.price
            )

        return redirect('order_success', order_id=order.id)

    return render(request, 'management/place_order.html', {
        'menu_items': available_items
    })


def order_success(request, order_id):
    order = Order.objects.get(id=order_id)

    return render(request, 'management/order_success.html', {
        'order': order
    })

def add_to_cart(request, item_id):
    if request.method != 'POST':
        return redirect('home')

    menu_item = get_object_or_404(
        MenuItem,
        id=item_id,
        is_available=True
    )

    cart = request.session.get('cart', {})
    item_key = str(menu_item.id)

    # Add one item or increase its quantity
    cart[item_key] = cart.get(item_key, 0) + 1

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f'{menu_item.name} added to cart!')
    return redirect('view_cart')
@require_GET
def api_menu(request):
    menu_items = MenuItem.objects.filter(is_available=True)

    data = [
        {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': str(item.price),
            'is_available': item.is_available,
        }
        for item in menu_items
    ]

    return JsonResponse({
        'success': True,
        'count': len(data),
        'menu_items': data,
    })

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0

    for item_id, quantity in cart.items():
        menu_item = MenuItem.objects.filter(
            id=item_id,
            is_available=True
        ).first()

        if menu_item is None:
            continue

        subtotal = menu_item.price * quantity
        grand_total += subtotal

        cart_items.append({
            'menu_item': menu_item,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'management/cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })

def update_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('view_cart')

    cart = request.session.get('cart', {})
    item_key = str(item_id)

    if item_key not in cart:
        messages.error(request, 'Item not found in your cart.')
        return redirect('view_cart')

    try:
        quantity = int(request.POST.get('quantity', ''))
        if quantity < 1 or quantity > 100:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Enter a quantity between 1 and 100.')
        return redirect('view_cart')

    cart[item_key] = quantity
    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, 'Cart quantity updated!')
    return redirect('view_cart')


def remove_from_cart(request, item_id):
    if request.method != 'POST':
        return redirect('view_cart')

    cart = request.session.get('cart', {})
    item_key = str(item_id)

    if item_key in cart:
        del cart[item_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart.')
    else:
        messages.error(request, 'Item not found in your cart.')

    return redirect('view_cart')


from django.db import transaction


def checkout(request):
    if request.method != 'POST':
        return redirect('view_cart')

    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')

    order_items = []
    grand_total = 0

    # Validate each cart item before creating the order
    for item_id, quantity in cart.items():
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 100:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Invalid item quantity in your cart.')
            return redirect('view_cart')

        menu_item = MenuItem.objects.filter(
            id=item_id,
            is_available=True
        ).first()

        if menu_item is None:
            messages.error(
                request,
                'A food item in your cart is unavailable. Please review your cart.'
            )
            return redirect('view_cart')

        subtotal = menu_item.price * quantity
        grand_total += subtotal

        order_items.append({
            'menu_item': menu_item,
            'quantity': quantity,
            'unit_price': menu_item.price,
        })

    # Save the order and all its items in one database transaction
    with transaction.atomic():
        order = Order.objects.create(
            total_amount=grand_total,
            status='pending'
        )

        for item in order_items:
            OrderItem.objects.create(
                order=order,
                menu_item=item['menu_item'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )

    # Clear the cart only after the database transaction succeeds
    request.session['cart'] = {}
    request.session.modified = True

    return redirect('order_success', order_id=order.id)
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


@csrf_exempt
@require_POST
def api_place_order(request):
    # Read JSON request data
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        }, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({
            'success': False,
            'message': 'Request must contain a JSON object.'
        }, status=400)

    items = payload.get('items')

    if not isinstance(items, list) or not items:
        return JsonResponse({
            'success': False,
            'message': 'Provide at least one item.'
        }, status=400)

    validated_items = []
    total_amount = Decimal('0.00')

    # Validate items and calculate the total on the server
    for entry in items:
        if not isinstance(entry, dict):
            return JsonResponse({
                'success': False,
                'message': 'Each item must be a JSON object.'
            }, status=400)

        try:
            item_id = int(entry.get('menu_item_id'))
            quantity = int(entry.get('quantity'))
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Menu item ID and quantity must be integers.'
            }, status=400)

        if item_id < 1 or quantity < 1 or quantity > 100:
            return JsonResponse({
                'success': False,
                'message': 'Invalid menu item ID or quantity.'
            }, status=400)

        menu_item = MenuItem.objects.filter(
            id=item_id,
            is_available=True
        ).first()

        if menu_item is None:
            return JsonResponse({
                'success': False,
                'message': f'Menu item {item_id} is unavailable or does not exist.'
            }, status=400)

        total_amount += menu_item.price * quantity

        validated_items.append({
            'menu_item': menu_item,
            'quantity': quantity,
            'unit_price': menu_item.price
        })

    # Save order and its items together
    with transaction.atomic():
        order = Order.objects.create(
            total_amount=total_amount,
            status='pending'
        )

        for item in validated_items:
            OrderItem.objects.create(
                order=order,
                menu_item=item['menu_item'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )

    return JsonResponse({
        'success': True,
        'message': 'Order placed successfully.',
        'order_id': order.id,
        'status': order.status,
        'total_amount': str(order.total_amount)
    }, status=201)
from datetime import date, time
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import RestaurantTable, Reservation


# API 1: View available tables
@require_GET
def api_available_tables(request):
    tables = RestaurantTable.objects.filter(is_active=True)

    data = [
        {
            'id': table.id,
            'table_number': table.table_number,
            'capacity': table.capacity
        }
        for table in tables
    ]

    return JsonResponse({
        'success': True,
        'tables': data
    })


# API 2: Reserve a table
@csrf_exempt
@require_POST
def api_reserve_table(request):
    try:
        data = json.loads(request.body)

        customer_name = data['customer_name'].strip()
        phone = data['phone'].strip()
        table_id = int(data['table_id'])
        guests = int(data['guests'])
        reservation_date = date.fromisoformat(data['reservation_date'])
        start_time = time.fromisoformat(data['start_time'])
        end_time = time.fromisoformat(data['end_time'])

    except (ValueError, TypeError, KeyError, AttributeError,
            json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid or missing reservation details.'
        }, status=400)

    if not customer_name or not phone:
        return JsonResponse({
            'success': False,
            'message': 'Customer name and phone are required.'
        }, status=400)

    if len(phone) > 15:
        return JsonResponse({
            'success': False,
            'message': 'Phone number must not exceed 15 characters.'
        }, status=400)

    if guests < 1:
        return JsonResponse({
            'success': False,
            'message': 'Guests must be at least 1.'
        }, status=400)

    if start_time >= end_time:
        return JsonResponse({
            'success': False,
            'message': 'End time must be later than start time.'
        }, status=400)

    if reservation_date < date.today():
        return JsonResponse({
            'success': False,
            'message': 'Reservation date cannot be in the past.'
        }, status=400)

    if reservation_date == timezone.localdate() and start_time <= timezone.localtime().time():
        return JsonResponse({
            'success': False,
            'message': 'Reservation start time must be in the future.'
        }, status=400)

    try:
        table = RestaurantTable.objects.get(
            id=table_id,
            is_active=True
        )
    except RestaurantTable.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Table not found or inactive.'
        }, status=404)

    if guests > table.capacity:
        return JsonResponse({
            'success': False,
            'message': f'This table accommodates up to {table.capacity} guests.'
        }, status=400)

    # Check for overlapping active reservations
    overlapping = Reservation.objects.filter(
        table=table,
        reservation_date=reservation_date,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exclude(status='cancelled').exists()

    if overlapping:
        return JsonResponse({
            'success': False,
            'message': 'This table is already reserved for that time.'
        }, status=409)

    reservation = Reservation.objects.create(
        customer_name=customer_name,
        phone=phone,
        table=table,
        reservation_date=reservation_date,
        start_time=start_time,
        end_time=end_time,
        guests=guests,
        status='confirmed'
    )

    return JsonResponse({
        'success': True,
        'message': 'Table reserved successfully.',
        'reservation': {
            'id': reservation.id,
            'customer_name': reservation.customer_name,
            'table_number': table.table_number,
            'reservation_date': str(reservation.reservation_date),
            'start_time': reservation.start_time.strftime('%H:%M'),
            'end_time': reservation.end_time.strftime('%H:%M'),
            'guests': reservation.guests,
            'status': reservation.status
        }
    }, status=201)
from .models import InventoryItem
from django.views.decorators.http import require_GET


@require_GET
def api_inventory(request):
    items = InventoryItem.objects.all()

    data = [
        {
            'id': item.id,
            'name': item.name,
            'quantity': str(item.quantity),
            'unit': item.unit,
            'reorder_level': str(item.reorder_level)
        }
        for item in items
    ]

    return JsonResponse({
        'success': True,
        'count': len(data),
        'inventory': data
    })

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation


@csrf_exempt
@require_POST
def api_update_inventory(request):
    try:
        data = json.loads(request.body)

        item_id = int(data.get('item_id'))
        quantity = Decimal(str(data.get('quantity')))

        if not quantity.is_finite() or quantity < 0:
            raise ValueError

    except (ValueError, TypeError, InvalidOperation,
            json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Provide a valid item_id and non-negative quantity.'
        }, status=400)

    item = InventoryItem.objects.filter(id=item_id).first()

    if item is None:
        return JsonResponse({
            'success': False,
            'message': 'Inventory item not found.'
        }, status=404)

    item.quantity = quantity
    item.save(update_fields=['quantity', 'updated_at'])

    return JsonResponse({
        'success': True,
        'message': 'Inventory updated successfully.',
        'item': {
            'id': item.id,
            'name': item.name,
            'quantity': str(item.quantity),
            'unit': item.unit
        }
    }, status=200)