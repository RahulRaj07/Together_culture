from django.db import models
from django.contrib.auth.models import AbstractUser

class Member(AbstractUser):
    # Additional fields for members
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField('Interest', blank=True)
    is_approved = models.BooleanField(default=False)
    professional_background = models.TextField(blank=True)
    why_join = models.TextField(blank=True)
    how_contribute = models.TextField(blank=True)

class Interest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
