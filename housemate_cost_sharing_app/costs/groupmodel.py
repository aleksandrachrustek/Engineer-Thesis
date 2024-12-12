import string
import secrets
from django.db import models
from django.contrib.auth.models import User


class CustomGroup(models.Model):
    CODE_LENGTH = 10 

    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name="user_groups", blank=True)
    code = models.CharField(max_length=CODE_LENGTH, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_random_code()
        super().save(*args, **kwargs)

    def generate_random_code(self):
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(self.CODE_LENGTH))
