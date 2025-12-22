from django.http import JsonResponse
from citas.models import Cita
from django.shortcuts import render

def lista_pacientes(request):
    citas = Cita.objects.all()
    data = [{'id': c.id, 'paciente': c.user.username, 'fecha': c.fecha} for c in citas]
    return JsonResponse(data, safe=False)

def home(request):
    return render(request, 'citas/home.html')