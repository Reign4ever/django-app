from django.db import models

# Create your models here.
class UserProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Event(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"

    class Meta:
        ordering = ['date', 'time']