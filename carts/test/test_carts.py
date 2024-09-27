import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from book.models import Book  
from carts.models import CartModel, CartItems 


