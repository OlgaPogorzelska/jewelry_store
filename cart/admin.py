from django.contrib import admin
from cart.models import Cart, CartItem, Shipping, Order, OrderItem

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Shipping)
admin.site.register(Order)
admin.site.register(OrderItem)


