from django.urls import path
from .views import CartsViews,OrderViews
from django.urls import path
from . import views



urlpatterns = [
    path('carts/', CartsViews.as_view(), name='carts-api'),
    path("orderapi/", OrderViews.as_view(), name="order-api"),
    path('delete_cart_item/<int:pk>/', CartsViews.as_view(), name='delete-cart-item'),
      

]
 