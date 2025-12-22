from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Encuentro(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()

    def __str__(self):
        return f"{self.patient.username} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

# Create your models here.
