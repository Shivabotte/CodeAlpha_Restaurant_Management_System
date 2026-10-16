from . import views
from django.urls import include, path

urlpatterns = [
   path('',views.home,name='home'),
   path('place-order/', views.place_order, name='place_order'),
   path('order-success/<int:order_id>/',views.order_success, name='order_success'),
   path(
    'add-to-cart/<int:item_id>/',
    views.add_to_cart,
    name='add_to_cart'
),
path('cart/', views.view_cart, name='view_cart'),

path(
    'update-cart/<int:item_id>/',
    views.update_cart_item,
    name='update_cart_item'
),
path(
    'remove-from-cart/<int:item_id>/',
    views.remove_from_cart,
    name='remove_from_cart'
),
path('checkout/', views.checkout, name='checkout'),
path('api/orders/', views.api_place_order, name='api_place_order'),
path(
    'api/tables/',
    views.api_available_tables,
    name='api_available_tables'
),

path(
    'api/reservations/',
    views.api_reserve_table,
    name='api_reserve_table'
),
path(
    'api/inventory/',
    views.api_inventory,
    name='api_inventory'
),
path(
    'api/inventory/update/',
    views.api_update_inventory,
    name='api_update_inventory'
),
]   
