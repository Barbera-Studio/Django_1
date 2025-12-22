# citas/forms.py
from __future__ import annotations
from datetime import datetime
from django import forms
from django.utils import timezone
from .models import Cita
from usuarios.models import Usuario

class CitaForm(forms.ModelForm):
    medico = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(es_medico=True).order_by("last_name", "first_name"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Médico"
    )

    class Meta:
        model = Cita
        fields = ["medico", "fecha", "hora", "motivo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "motivo": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Describe el motivo"}),
        }

    def clean(self):
        cleaned = super().clean()
        fecha = cleaned.get("fecha")
        hora = cleaned.get("hora")
        medico = cleaned.get("medico")

        if medico is None or not getattr(medico, "es_medico", False):
            raise forms.ValidationError("Debes seleccionar un médico válido.")

        if not fecha or not hora:
            raise forms.ValidationError("Debes proporcionar fecha y hora.")

        naive = datetime.combine(fecha, hora)
        programada = timezone.make_aware(naive, timezone.get_current_timezone())
        if programada <= timezone.now():
            raise forms.ValidationError("La fecha y hora de la cita no pueden estar en el pasado.")

        return cleaned
