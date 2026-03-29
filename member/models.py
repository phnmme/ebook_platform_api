from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings 


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

class UsageHistory(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='usage_histories'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Usage Histories"

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp.strftime('%d-%m-%Y %H:%M:%S')}"
    
    