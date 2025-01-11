import pytest

from shop.models import CustomerUser


@pytest.fixture
def kamil(db):
    return CustomerUser.objects.create(
        email='kwait@gmail.com',
        first_name='Kamil',
        last_name='Kwiatkowski',
        phone_number='123123123',
        street='Kwiatowa',
        house_number='22',
        apartment_number='',
        city='Warszawa',
        postal_code='00-011',
        country='Polska',
        password='kamil123'

    )


@pytest.fixture
def krysia():
    return CustomerUser.objects.create(
        email='krysia@gmail.com',
        first_name='Krysia',
        last_name='Kwiatkowski',
        phone_number='123123223',
        street='Monte Cassino',
        house_number='22A',
        apartment_number='',
        city='Kraków',
        postal_code='30-007',
        country='Polska',

    )


@pytest.fixture
def kasia():
    return CustomerUser.objects.create(
        email='kasia@gmail.com',
        first_name='Kasia',
        last_name='Kowalska',
        phone_number='222123123',
        street='Jana Pawła II',
        house_number='12',
        apartment_number='1',
        city='Poznań',
        postal_code='60-106',
        country='Polska',
        password='kamil123',

    )



