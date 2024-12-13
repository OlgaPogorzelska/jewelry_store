from django.db import models
from shop.models import CustomerUser, Product


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quality = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} x {self.quality}"


class Cart(models.Model):
    data_add = models.DateTimeField(auto_now_add=True)






