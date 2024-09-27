import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from user.models import Customer
from rest_framework.reverse import reverse
from rest_framework import status
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken



#User Resigtration Pytest
@pytest.mark.django_db
@pytest.mark.register_success
def test_user_registration(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    assert response.status_code == 200
    
@pytest.mark.django_db
@pytest.mark.userexist
def test_exists_user_registration(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    response = client.post(url,data=data,content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    

@pytest.mark.django_db
@pytest.mark.register_missi
def test_user_registration_missing_field(client):
    # Data missing required fields
    data = {
        "first_name": "Pinky",
        "email": "pinky1995@gmail.com",
        "password": "Pinky564"
    }
    
    url = reverse('register_user')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
@pytest.mark.django_db
@pytest.mark.invalid_email
def test_user_invalid_email(client):
    # Data missing required fields
    data = {
        "first_name": "Pinky",
        "last_name" : "Yadav",
        "email": "pinkgmail.com",
        "password": "Pinky564"
    }
    
    url = reverse('register_user')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
@pytest.mark.django_db
@pytest.mark.invalid_password
def test_user_invalid_password(client):
    # Data missing required fields
    data = {
        "first_name": "Pinky",
        "last_name" : "Yadav",
        "email": "pinky1995@gmail.com",
        "password": "Pin564"
    
    }
    
    url = reverse('register_user')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
@pytest.mark.django_db
@pytest.mark.nodata
def test_user_nodata(client):
    data = {}
    
    url = reverse('register_user')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
@pytest.mark.django_db
@pytest.mark.login
def test_user_login(client):
    user = Customer.objects.create_user(first_name="Sonal",last_name="Singh",email="sonaly03@gmail.com",password="Sonal123",is_verified=True)
    login_data = {"email":"sonaly03@gmail.com",
                  "password":"Sonal123"}   
    
    url = reverse('login_user')
    response = client.post(url,data=login_data,content_type='application/json')
    print(response.data)
    assert response.status_code ==  status.HTTP_200_OK
 
 
@pytest.mark.django_db
@pytest.mark.email_not_verifiy
def test_user_email_not_verifiy(client):
    user = Customer.objects.create_user(first_name="Sonal",last_name="Singh",email="sonaly03@gmail.com",password="Sonal123",is_verified=False)
    login_data = {"email":"sonaly03@gmail.com",
                  "password":"Sonal123"}   
    
    url = reverse('login_user')
    response = client.post(url,data=login_data,content_type='application/json')
    print(response.data)
    assert response.status_code ==  status.HTTP_400_BAD_REQUEST
    
    
@pytest.mark.django_db
@pytest.mark.password_invalid
def test_user_password_invalid(client):
    user = Customer.objects.create_user(first_name="Sonal",last_name="Singh",email="sonaly03@gmail.com",password="Sonal123",is_verified=False)
    login_data = {"email":"sonaly03@gmail.com",
                  "password":"Sonau123"}   
    
    url = reverse('login_user')
    response = client.post(url,data=login_data,content_type='application/json')
    print(response.data)
    assert response.status_code ==  status.HTTP_400_BAD_REQUEST
    
    
    
@pytest.mark.django_db
@pytest.mark.login_missing
def test_user_login_missing_field(client):
    user = Customer.objects.create_user(first_name="Sonal",last_name="Singh",email="sonaly03@gmail.com",password="Sonal123",is_verified=False)
    login_data = {"email":"sonaly03@gmail.com"}   
    
    url = reverse('login_user')
    response = client.post(url,data=login_data,content_type='application/json')
    print(response.data)
    assert response.status_code ==  status.HTTP_400_BAD_REQUEST
    
    
# @pytest