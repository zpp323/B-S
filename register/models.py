from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField("person's name", max_length=32)
    password = models.CharField("password", max_length=32)

