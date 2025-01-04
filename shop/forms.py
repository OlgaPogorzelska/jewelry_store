from django import forms
import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from shop.models import CustomerUser, Product, Category, ProductImages


class RegistrationUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomerUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'street',
                  'house_number', 'apartment_number', 'city', 'postal_code',
                  'country', 'password']

        widgets = {
            'password': forms.PasswordInput
        }

    def clean(self):
        cd = super().clean()
        pwd1 = cd.get('password')
        pwd2 = cd.get('confirm_password')
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error('confirm_password', 'The passwords are not the same')
        return cd


class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        email = cd.get('email')
        pwd = cd.get('password')
        user = authenticate(username=email, password=pwd)
        if user is None:
            raise ValidationError('''You entered the wrong 
                                  password or login!''')
        else:
            self.user = user


class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False)
