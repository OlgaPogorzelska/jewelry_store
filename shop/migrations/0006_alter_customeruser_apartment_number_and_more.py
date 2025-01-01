# Generated by Django 5.1.4 on 2024-12-29 12:20

import shop.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_remove_customeruser_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeruser',
            name='apartment_number',
            field=models.CharField(blank=True, max_length=10, null=True, validators=[shop.models.validate_digit]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='city',
            field=models.CharField(max_length=100, null=True, validators=[shop.models.validate_alpha]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='country',
            field=models.CharField(default='Poland', max_length=100, null=True, validators=[shop.models.validate_alpha]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='first_name',
            field=models.CharField(max_length=255, null=True, validators=[shop.models.validate_alpha]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='house_number',
            field=models.CharField(max_length=10, null=True, validators=[shop.models.validate_house_number]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='last_name',
            field=models.CharField(max_length=255, null=True, validators=[shop.models.validate_alpha]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='phone_number',
            field=models.CharField(max_length=9, null=True, unique=True, validators=[shop.models.validate_digit]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='postal_code',
            field=models.CharField(max_length=6, null=True, validators=[shop.models.validate_postal_code]),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='street',
            field=models.CharField(max_length=255, null=True, validators=[shop.models.validate_street_name]),
        ),
    ]