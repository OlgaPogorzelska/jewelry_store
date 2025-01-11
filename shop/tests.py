import pytest
from pytest_django.asserts import assertTemplateUsed
from pytest_django.fixtures import django_user_model

from cart.models import Cart
from .forms import RegistrationUserForm, UserLoginForm
from .models import CustomerUser, Category
from django.urls import reverse


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
    assert form.errors['postal_code'] == ["Kod pocztowy musi być w formacie 'XX-XXX'."]


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
    assert form.errors['first_name'] == ['Musi zawierać tylko litery.']


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
    assert form.errors['house_number'] == ["Numer domu musi zawierać tylko cyfry i "
                                           "opcjonalną literę na końcu."
                                           "Przykłady: '123', '456A'"]


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
    assert form.errors['street'] == ["Nazwa ulicy musi zawierać tylko litery,"
                                     "spacje i opcjonalne cyfry na końcu."
                                     "Przykład: 'Jana Pawła II', 'Dywizjonu 303'."]


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
    # Tworzenie użytkownika
    user = CustomerUser.objects.create(
        email='kamil@example.com',
        first_name='Kamil',
        last_name='Nowak'
    )
    user.set_password('kamil123')  # Ustawianie zaszyfrowanego hasła
    user.save()

    # Wysłanie danych logowania (POST) do widoku logowania
    response = client.post('/login/', {
        'email': user.email,
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
    assert form.errors


@pytest.mark.django_db
def test_logout(client, kasia):
    client.login(email=kasia.email, password='kamil123')

    response = client.get('/logout/')  # get, ponieważ w view użyliśmy get do logout, czy nie powinien być post?

    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_details_view_status_code(client, kamil):
    kamil.set_password('kamil123')  # Ustawiamy hasło
    kamil.save()

    client.login(email=kamil.email, password='kamil123')
    response = client.get(reverse('user_details', kwargs={'pk': kamil.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_details_view_cart_in_context(client, kamil):
    kamil.set_password('kamil123')  # Ustawiamy hasło
    kamil.save()
    cart = Cart.objects.create(user=kamil)

    client.login(email=kamil.email, password='kamil123')

    response = client.get(reverse('user_details', kwargs={'pk': kamil.pk}))
    assert 'cart' in response.context
    assert response.context['cart'] == cart


@pytest.mark.django_db
def test_user_details_view_categories_in_context(client, kamil):
    kamil.set_password('kamil123')  # Ustawiamy hasło
    kamil.save()

    category = Category.objects.create(name='Moda')

    client.login(email=kamil.email, password='kamil123')
    response = client.get(reverse('user_details', kwargs={'pk': kamil.pk}))

    assert 'categories' in response.context
    assert list(response.context['categories']) == [category]
    assertTemplateUsed(response, 'shop/user.html')


@pytest.mark.django_db
def test_user_details_view_authenticated(client, kamil):
    kamil.set_password('kamil123')  # Hasło musi być ustawione za pomocą set_password
    kamil.save()
    client.login(email=kamil.email, password='kamil123')
    cart, created = Cart.objects.get_or_create(user=kamil)
    response = client.get(reverse('user_details', kwargs={'pk': kamil.pk}))

    assert response.status_code == 200
    assert response.context['user'].email == kamil.email
    assert response.context['user'].first_name == kamil.first_name
    assert response.context['user'].last_name == kamil.last_name
    cart = Cart.objects.get(user=kamil)
    assert response.context['cart'] == cart
    assert 'categories' in response.context


@pytest.mark.django_db
def test_user_details_view_anonymous(client):
    # Tworzymy użytkownika
    user = CustomerUser.objects.create(
        email='kamil@example.com',
        password='kamil123',
        first_name='Kamil',
        last_name='Nowak'
    )
    user.set_password('kamil123')
    user.save()
    response = client.get(reverse('user_details', kwargs={'pk': user.pk}))
    assert response.status_code == 302
    assert response.url.startswith('/login/')  # Sprawdzamy, czy przekierowanie jest do strony logowania


@pytest.mark.django_db
def test_update_user_view_requires_login(client):
    # Próbujemy uzyskać dostęp do widoku bez zalogowania
    response = client.get(reverse('update_user', kwargs={'pk': 1}))  # Używamy poprawnego pk

    # Sprawdzamy, czy odpowiedź to przekierowanie na stronę logowania
    assert response.status_code == 302
    assert response.url.startswith('/login/')


@pytest.mark.django_db
def test_update_user_view_invalid_data(client, kamil):
    kamil.set_password('kamil123')  # Hasło musi być ustawione za pomocą set_password
    kamil.save()
    client.login(email=kamil.email, password='kamil123')

    # Dane do zaktualizowania (niepoprawny email)
    invalid_data = {
        'first_name': 'Kamil Invalid',
        'last_name': 'Nowak Invalid',
        'email': 'invalid-email',  # Niepoprawny format emaila
    }

    # Wysłanie zapytania POST z błędnymi danymi
    response = client.post(reverse('update_user', kwargs={'pk': kamil.pk}), invalid_data)

    # Sprawdzamy, czy formularz ponownie się wyświetla z błędami
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors  # Sprawdzamy, czy są błędy


@pytest.mark.django_db
def test_update_user_view_rendered_with_user_data(client, kamil):
    kamil.set_password('kamil123')  # Hasło musi być ustawione za pomocą set_password
    kamil.save()
    client.login(email=kamil.email, password='kamil123')

    # Wysłanie zapytania GET, aby zobaczyć formularz
    response = client.get(reverse('update_user', kwargs={'pk': kamil.pk}))

    # Sprawdzamy, czy formularz jest renderowany z odpowiednimi danymi
    assert response.status_code == 200
    assert response.context['form'].initial['first_name'] == kamil.first_name
    assert response.context['form'].initial['last_name'] == kamil.last_name
    assert response.context['form'].initial['email'] == kamil.email


@pytest.mark.django_db
def test_start_view(client):
    # Tworzenie przykładowych kategorii
    category1 = Category.objects.create(name='Biżuteria')
    category2 = Category.objects.create(name='Akcesoria')

    response = client.get('')  # Użyj reverse do uzyskania URL-a

    assert response.status_code == 200  # Sprawdź, czy odpowiedź jest OK (200)
    assert 'categories' in response.context  # Upewnij się, że kategorie są w kontekście
    assert list(response.context['categories']) == [category1, category2]  # Sprawdź, czy kategorie są poprawne
    assert 'form' in response.context  # Upewnij się, że formularz jest w kontekście


@pytest.mark.django_db
def test_start_view_authenticated_user(client):
    # Tworzenie przykładowego użytkownika i logowanie go
    user = CustomerUser.objects.create(
        email='kamil@example.com',
        password='kamil123',
        first_name='Kamil',
        last_name='Nowak'
    )
    user.set_password('kamil123')  # Szyfrowanie hasła
    user.save()
    logged_in = client.login(email=user.email, password='kamil123')  # Logowanie użytkownika
    assert logged_in
    # Wywołanie widoku
    response = client.get('')

    # Sprawdzenie statusu odpowiedzi
    assert response.status_code == 200
    # Sprawdzenie, czy użytkownik jest zalogowany
    assert response.wsgi_request.user.is_authenticated
    assert 'cart' in response.context
    assert isinstance(response.context['cart'], Cart)


@pytest.mark.django_db
def test_start_view_anonymous_user(client):
    category1 = Category.objects.create(name='Biżuteria')
    category2 = Category.objects.create(name='Akcesoria')

    response = client.get('')  # Sprawdzenie odpowiedzi jako anonimowy użytkownik

    assert response.status_code == 200
    # Sprawdzamy, czy kategorie zostały dodane do kontekstu
    assert 'categories' in response.context
    assert list(response.context['categories']) == [category1, category2]
    assert 'form' in response.context
    assert response.context['cart'] is None


@pytest.mark.django_db
def test_about_us_view(client):
    category1 = Category.objects.create(name='Biżuteria')
    response = client.get(reverse('about_us'))

    assert response.status_code == 200

    assert 'categories' in response.context
    assert list(response.context['categories']) == [category1]
    assertTemplateUsed(response, 'shop/about_us.html')


@pytest.mark.django_db
def test_care_view(client):
    category1 = Category.objects.create(name='Akcesoria')
    response = client.get(reverse('care'))

    assert response.status_code == 200
    assert 'categories' in response.context
    assert list(response.context['categories']) == [category1]
    assertTemplateUsed(response, 'shop/care.html')


@pytest.mark.django_db
def test_contact_view(client):
    category1 = Category.objects.create(name='Moda')
    response = client.get(reverse('contact'))

    assert response.status_code == 200
    assert 'categories' in response.context
    assert list(response.context['categories']) == [category1]
    assertTemplateUsed(response, 'shop/contact.html')


@pytest.mark.django_db
def test_size_view(client):
    category1 = Category.objects.create(name='Odzież')
    response = client.get(reverse('sizes'))

    assert response.status_code == 200
    assert 'categories' in response.context
    assert list(response.context['categories']) == [category1]
    assertTemplateUsed(response, 'shop/size.html')
