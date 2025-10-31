from django.db import models
from django.conf import settings

# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "init"),
        ("in_progres", "in_progres"),
        ("finished", "finished"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='init')
