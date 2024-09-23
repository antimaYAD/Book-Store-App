from django.urls import path
from .views import RegistrationUserView,LoginUserView,verify_email
from django.urls import path
from . import views



urlpatterns = [
    path('userregister/', RegistrationUserView.as_view(), name='register_user'),
    path('email_verify/<str:token>/',verify_email,name='verify_email'),
    path('userlogin/', LoginUserView.as_view(), name='login_user'),
]

