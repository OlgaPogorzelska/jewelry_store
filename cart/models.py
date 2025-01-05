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
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Shipping for {self.user}"

    def save(self, *args, **kwargs):
        if self.shipping_company == 'PP':
            self.shipping_price = 15
        elif self.shipping_company == 'IN':
            self.shipping_price = 18
        elif self.shipping_company == 'DP':
            self.shipping_price = 20
        super().save(*args, **kwargs)

    def get_shipping_price(self):
        return self.shipping_price

    def get_total_price_with_shipping(self):
        items_total_price = sum(item.get_total_price() for item in self.user.cart.cartitem_set.all())
        return items_total_price + self.shipping_price

    def get_shipping_email(self):
        return self.user.email

    def get_shipping_phone(self):
        return self.user.phone_number

    def get_shipping_address(self):
        """Pobieranie adres użytkownika z modelu User"""
        return f"{self.user.full_street}, {self.user.postal_code} {self.user.city} {self.user.country}"


class Order(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"
