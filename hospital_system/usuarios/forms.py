from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from .models import Usuario
from citas.models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'hora', 'motivo', 'estado']

    def __init__(self, *args, **kwargs):
        super(CitaForm, self).__init__(*args, **kwargs)
        try:
            grupo_medicos = Group.objects.filter(name='Médicos').first()
            if grupo_medicos and grupo_medicos.user_set.exists():
                self.fields['medico'].queryset = Usuario.objects.filter(groups=grupo_medicos).order_by('first_name', 'last_name')
            else:
                self.fields['medico'].queryset = Usuario.objects.filter(es_medico=True).order_by('first_name', 'last_name')
        except Group.DoesNotExist:
            self.fields['medico'].queryset = Usuario.objects.filter(es_medico=True).order_by('first_name', 'last_name')

        self.fields['medico'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['medico'].help_text = "Selecciona el médico que atenderá la cita"
        self.fields['fecha'].help_text = "Formato: AAAA-MM-DD"
        self.fields['hora'].help_text = "Formato: HH:MM"

class RegistroForm(UserCreationForm):
    es_medico = forms.BooleanField(required=False, label='¿Eres médico?')

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'es_medico', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'autofocus': True})
    )



