from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
import re
from django.db import models


def validate_postal_code(postal_code):
    """
        Checks if the postal code is written in
         the form XX-XXX where X is a number.
    """
    if (len(postal_code) == 6 and postal_code[:2].isdigit()
            and postal_code[2] == '-' and postal_code[3:].isdigit()):
        return True
    else:
        raise ValidationError("Kod pocztowy musi być w formacie 'XX-XXX'.")


def validate_house_number(house_number):
    """
        Checks if house_number is a number
         with an optional trailing letter.
    """
    pattern = r'^\d+[A-Za-z]?$'  # liczba z opcjonalną literą
    if re.match(pattern, house_number):
        return True
    else:
        raise ValidationError("Numer domu must contain only digits and an "
                              "optional letter at the end. "
                              "Examples: '123', '456A'")


def validate_street_name(street):
    """
        Checks if street is word or words with space and
         with an optional trailing number.
    """
    pattern = r'[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż ]+(\d+)?$'  # słowo lub
    # słowa ze spacja pomiędzy sobą i z możliwością liczby na końcu
    if re.match(pattern, street):
        return True
    else:
        raise ValidationError("Street name must contain only letters, "
                              "spaces, and optional numbers at the end. "
                              "Examples: 'Kwiatowa', 'Kwiatowa 12'")


def validate_alpha(name):
    if name.isalpha():
        return True
    else:
        raise ValidationError("Musi zawierać tylko litery.")


def validate_digit(number):
    if number.isdigit():
        return True
    else:
        raise ValidationError("Musi zawierać tylko cyfry.")


def validate_phone_numer(phone_number):
    if phone_number.isdigit() and len(phone_number) == 9:
        return True
    else:
        raise ValidationError("Phone number must contain only digits and "
                              "must be 9 digits long.")


SIZE = (
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
)


class CustomerUser(AbstractUser, PermissionsMixin):
    """
        Custom user model for a jewelry store.
    """
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True,
                                  validators=[validate_alpha])
    last_name = models.CharField(max_length=255, null=True,
                                 validators=[validate_alpha])
    phone_number = models.CharField(max_length=9, unique=True, null=True,
                                    validators=[validate_phone_numer])
    street = models.CharField(max_length=255, null=True,
                              validators=[validate_street_name])
    house_number = models.CharField(max_length=10, null=True,
                                    validators=[validate_house_number])
    apartment_number = models.CharField(max_length=10, blank=True, null=True,
                                        validators=[validate_digit])
    city = models.CharField(max_length=100, null=True,
                            validators=[validate_alpha])
    postal_code = models.CharField(max_length=6, null=True,
                                   validators=[validate_postal_code])
    country = models.CharField(max_length=100, null=True, default="Poland",
                               validators=[validate_alpha])

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    @property
    def full_street(self):
        if self.apartment_number:
            return (f"{self.street}  {self.house_number} "
                    f"{self.apartment_number}")
        return f"{self.street}  {self.house_number}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(null=True)
    description = models.TextField()
    size = models.CharField(choices=SIZE, max_length=1, blank=True, null=True)

    def __str__(self):
        return self.name + " " + str(self.price)


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
