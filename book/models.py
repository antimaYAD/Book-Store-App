
from django.db import models
from django.conf import settings

# Create your models here.


class Book(models.Model):
    name = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    stock = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return self.name




# Book Model:
# name= str, not-null, unique
# author= str, not-null, index
# description= text, nullable
# user= fk user model
# price= positive int, not-null