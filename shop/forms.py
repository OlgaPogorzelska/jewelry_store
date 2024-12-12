from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from shop.models import CustomerUser


class RegistrationUserForm(forms.ModelForm):
    email = forms.EmailField(validators=[EmailValidator()])
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomerUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'street',
                  'house_number', 'apartment_number', 'city', 'postal_code',
                  'country', 'password']


