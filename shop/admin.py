from django.contrib import admin
from shop.models import CustomerUser, Product, ProductImages, Category

admin.site.register(CustomerUser)
admin.site.register(Product)
admin.site.register(ProductImages)
admin.site.register(Category)
