from django.urls import path, include
from . import views
from .views import (HomeView, ItemDetailView, OrderSummary, CheckoutView)
app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug:slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummary.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('remove_item_quantity_from_cart/<slug>', views.remove_item_quantity_from_cart, name="remove-item-quantity-from-cart"),
    
]
