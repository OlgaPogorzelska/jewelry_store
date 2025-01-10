from django import forms
import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from shop.models import CustomerUser, Product, Category, ProductImages


class RegistrationUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Powtórz hasło'}))

    class Meta:
        model = CustomerUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'street',
                  'house_number', 'apartment_number', 'city', 'postal_code',
                  'country', 'password']

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Imię'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nazwisko'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
            'street': forms.TextInput(attrs={'placeholder': 'Ulica'}),
            'house_number': forms.TextInput(attrs={'placeholder': 'Nr domu'}),
            'apartment_number': forms.TextInput(attrs={'placeholder': 'Nr mieszkania'}),
            'city': forms.TextInput(attrs={'placeholder': 'Miasto'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Kod pocztowy'}),
            'country': forms.TextInput(attrs={'placeholder': 'Kraj'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Hasło'}),
        }

    def clean(self):
        cd = super().clean()
        pwd1 = cd.get('password')
        pwd2 = cd.get('confirm_password')
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error('confirm_password', 'The passwords are not the same')
        return cd

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""


class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False)
