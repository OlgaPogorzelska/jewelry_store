from django import forms
import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from shop.models import CustomerUser


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
            raise ValidationError('The passwords are not the same')

        p_code = cd.get('postal_code')
        if p_code and not is_valid_postal_code(p_code):
            raise ValidationError("Postal code must be in the"
                                  " format 'XX-XXX'.")

        f_name = cd.get('first_name')
        l_name = cd.get('last_name')
        street = cd.get('street')
        house_num = cd.get('house_number')
        apartment_num = cd.get('apartment_number')
        city = cd.get('city')
        country = cd.get('country')

        if f_name and not f_name.isalpha():
            raise ValidationError('First name must contain only letters.')
        if l_name and not l_name.isalpha():
            raise ValidationError('Last name must contain only letters.')
        if street and not validate_street_name(street):
            raise ValidationError('Street name must contain only letters,'
                                  ' spaces, and optional numbers at the end. '
                                  'Example: "Jana Pawła II", "Dywizjonu 303".')
        if house_num and not validate_house_number(house_num):
            raise ValidationError('House number must be a number'
                                  'with an optional letter at the end.'
                                  ' Examples: "123", "456A".')
        if apartment_num and apartment_num and not apartment_num.isdigit():
            raise ValidationError('Apartment number must contain only number.')
        if city and not city.isalpha():
            raise ValidationError('City name must contain only letters.')
        if country and not country.isalpha():
            raise ValidationError('Country name must contain only letters. ')
        return cd


@staticmethod
def is_valid_postal_code(postal_code):
    """
        Checks if the postal code is written in
         the form XX-XXX where X is a number.
    """
    return (len(postal_code) == 6
            and postal_code[:2].isdigit()
            and postal_code[2] == '-'
            and postal_code[3:].isdigit())


@staticmethod
def validate_house_number(house_number):
    """
        Checks if house_number is a number
         with an optional trailing letter.
    """
    pattern = r'^\d+[A-Za-z]?$'  # liczba z opcjonalną literą
    return re.match(pattern, house_number)


@staticmethod
def validate_street_name(street):
    """
        Checks if street is word or words with space and
         with an optional trailing number.
    """
    pattern = r'[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+(\d+)?$'  # słowo lub
    # słowa ze spacja pomiędzy sobą i z możliwością liczby na końcu
    return re.match(pattern, street)




