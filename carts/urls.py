from django.urls import path
from .views import CartsViews
from django.urls import path
from . import views



urlpatterns = [
    path('carts/', CartsViews.as_view(), name='carts-api')
]
 