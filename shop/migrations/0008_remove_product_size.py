# Generated by Django 5.1.4 on 2025-01-01 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_customeruser_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
    ]