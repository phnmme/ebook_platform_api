from django.db import models
from django.contrib.auth.models import AbstractUser


class SystemUser(AbstractUser):
    ROLE_CHOICES = (
        ('author', 'Author'),
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    userid = models.BigAutoField(primary_key=True)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # เฉพาะ Author
    idcard = models.FileField(upload_to='idcard/', blank=True, null=True)
    expertise = models.TextField(blank=True, null=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'fullname']
