from django.db import models
from django.conf import settings
from book.models import Book

# Create your models here.
class CartModel(models.Model):
    total_price = models.PositiveIntegerField(default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    is_ordered = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "carts"  # Correct spelling of 'db_table'


class CartItems(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "carts_items"  # Correct table name for cart items




