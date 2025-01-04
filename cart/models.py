from django.db import models
from shop.models import CustomerUser, Product

SIZE = (
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    size = models.CharField(choices=SIZE, max_length=1, blank=True, null=True)

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


class Shipping(models.Model):
    SHIPPING_COMPANIES = (
        ('PP', 'Poczta Polska'),
        ('IN', 'InPost'),
        ('DP', 'DPD'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    shipping_company = models.CharField(max_length=2, choices=SHIPPING_COMPANIES, default='PP')
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Shipping for {self.user}"

    def get_shipping_price(self):
        return self.shipping_price

    def get_shipping_email(self):
        return self.user.email

    def get_shipping_phone(self):
        return self.user.phone_number

    def get_shipping_address(self):
        """Pobieranie adres użytkownika z modelu User"""
        return f"{self.user.full_street}, {self.user.postal_code} {self.user.city} {self.user.country}"
