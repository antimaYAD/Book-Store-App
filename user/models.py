from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .managers import CustomUserManager

class Customer(AbstractUser):
    username = None
    email = models.EmailField("email address", max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)

    # Overriding the default `groups` and `user_permissions` fields
    groups = models.ManyToManyField(
        Group,
        related_name='custom_customer_groups',  # Add related_name to resolve clash
        blank=True,
        help_text='The groups this customer belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_customer_permissions',  # Add related_name to resolve clash
        blank=True,
        help_text='Specific permissions for this customer.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "customer_detail"

    def __str__(self):
        return self.email
