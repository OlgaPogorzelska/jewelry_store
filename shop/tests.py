import pytest

from .forms import RegistrationUserForm, UserLoginForm
from .models import CustomerUser


@pytest.mark.django_db
def test_registration_view(client):
    response = client.get('/register/')
    assert response.status_code == 200
    assert isinstance(response.context['form'], RegistrationUserForm)


@pytest.mark.django_db
def test_registration_form_empty(client):
    form_data = {

    }

    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert form.errors  # ? Czy tak mogę, jak nie wiem, jaki wyskoczy błąd
    assert CustomerUser.objects.count() == 0  # czy mogę sprawdzać, że nic się nie dodało ?


@pytest.mark.django_db
def test_registration_form_valid_date(client):
    form_data = {
        'email': 'kwait@gmail.com',
        'first_name': 'Kamil',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa',
        'house_number': '22',
        'apartment_number': '',
        'city': 'Warszawa',
        'postal_code': '00-011',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    assert response.status_code == 302
    assert CustomerUser.objects.count() == 1


@pytest.mark.django_db
def test_registration_form_postal_code_invalid_date(client):
    form_data = {
        'email': 'kwait@gmail.com',
        'first_name': 'Kamil',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa',
        'house_number': '22',
        'apartment_number': '',
        'city': 'Warszawa',
        'postal_code': '001-0',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert 'postal_code' in form.errors
    assert form.errors['postal_code'] == ['''Postal code must be in the
                                  format 'XX-XXX'. ''']


@pytest.mark.django_db
def test_registration_form_first_name_invalid_date(client):
    form_data = {
        'email': 'kwait@gmail.com',
        'first_name': 'Kamil12',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa',
        'house_number': '22',
        'apartment_number': '',
        'city': 'Warszawa',
        'postal_code': '00-011',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert 'first_name' in form.errors
    assert form.errors['first_name'] == ['First name must contain only letters.']


@pytest.mark.django_db
def test_registration_form_house_number_invalid_date(client):
    form_data = {
        'email': 'kwait@gmail.com',
        'first_name': 'Kamil',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa',
        'house_number': '22A 3',
        'apartment_number': '12',
        'city': 'Warszawa',
        'postal_code': '00-011',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert 'house_number' in form.errors
    assert form.errors['house_number'] == ['''House number must be a number
                                  with an optional letter at the end.
                                  Examples: "123", "456A".''']


@pytest.mark.django_db
def test_registration_form_street_invalid_date(client):
    form_data = {
        'email': 'kwait@gmail.com',
        'first_name': 'Kamil',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa 2@',
        'house_number': '22',
        'apartment_number': '',
        'city': 'Warszawa',
        'postal_code': '00-011',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert 'street' in form.errors
    assert form.errors['street'] == ['''Street name must contain only letters,
                                  spaces, and optional numbers at the end. 
                                  Example: "Jana Pawła II", "Dywizjonu 303".''']


@pytest.mark.django_db
def test_registration_form_email_invalid_date(client):
    form_data = {
        'email': 'kwait@',
        'first_name': 'Kamil',
        'last_name': 'Kwiatkowski',
        'phone_number': '123123123',
        'street': 'Kwiatowa',
        'house_number': '22',
        'apartment_number': '',
        'city': 'Warszawa',
        'postal_code': '00-011',
        'country': 'Polska',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    }
    response = client.post('/register/', form_data)
    form = response.context['form']
    assert response.status_code == 200
    assert 'email' in form.errors
    assert form.errors['email']


@pytest.mark.django_db
def test_registration_uniq_email(client):
    pass


@pytest.mark.django_db
def test_login_view(client):
    response = client.get('/login/')
    assert response.status_code == 200
    assert isinstance(response.context['form'], UserLoginForm)


@pytest.mark.django_db
def test_login_valid_data(client, kamil):
    response = client.post('/login/', {
        'email': kamil.email,
        'password': 'kamil123'
    })

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_invalid_data(client, kamil):

    response = client.post('/login/', {
        'email': kamil.email,
        'password': 'niepoprawnehaslo'
    })
    form = response.context['form']
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert form.errors #???

@pytest.mark.django_db
def test_logout(client, kamil):

    client.login(email=kamil.email, password='kamil123')

    response = client.get('/logout/')# get, ponieważ w view użyliśmy get do logout, czy nie powinien być post?

    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated

