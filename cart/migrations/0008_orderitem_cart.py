# Generated by Django 5.1.4 on 2025-01-06 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0007_order_shipping_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.cart'),
        ),
    ]
