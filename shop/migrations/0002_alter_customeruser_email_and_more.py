# Generated by Django 5.1.4 on 2024-12-09 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeruser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='postal_code',
            field=models.CharField(max_length=6, null=True),
        ),
    ]