from django.db import models

# Create your models here.
class UserProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name