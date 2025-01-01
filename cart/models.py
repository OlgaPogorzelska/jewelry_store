from django.db import models
from shop.models import CustomerUser, Product


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity


class Cart(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE, default=1)
    data_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user}"

    def get_total_price_cart(self):
        return sum(item.get_total_price() for item in self.cartitem_set.all())





