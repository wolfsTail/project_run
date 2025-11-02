from django.db import models
from django.conf import settings

# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "init"),
        ("in_progress", "in_progress"),
        ("finished", "finished"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='init')
    distance = models.FloatField(null=True, blank=True)


class AthleteInfo(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="athlete_info",
        unique=True,
    )
    goals = models.TextField(blank=True, default="")
    weight = models.IntegerField(null=True, blank=True)


class Challenge(models.Model):
    full_name = models.CharField(max_length=255)
    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenges"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("athlete", "full_name"),)


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="positions")
    latitude = models.DecimalField(max_digits=8, decimal_places=4)
    longitude = models.DecimalField(max_digits=9, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
