# Generated by Django 5.1.4 on 2025-01-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_remove_product_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.CharField(blank=True, choices=[('S', 'S'), ('M', 'M'), ('L', 'L')], max_length=1, null=True),
        ),
    ]
