from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViews

router = DefaultRouter()
router.register(r'books', BookViews)

urlpatterns = [
    path('api/', include(router.urls)),
]
