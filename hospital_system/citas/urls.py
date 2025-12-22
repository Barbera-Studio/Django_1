from django.urls import path
from . import views

app_name = "citas"

urlpatterns = [
    path("", views.citas_home, name="usuarios_home"),
    path("home/", views.citas_home, name="home"),
    path("agendar/", views.agendar_cita, name="agendar_cita"),
    path("lista_citas/", views.lista_citas, name="lista_citas"),
    path("editar/<int:cita_id>/", views.editar_cita, name="editar_cita"),
    path("cancelar/<int:cita_id>/", views.cancelar_cita, name="cancelar_cita"),
    path("eliminar/<int:cita_id>/", views.eliminar_cita, name="eliminar_cita"),
    path("detalle/<int:cita_id>/", views.detalle_cita, name="detalle_cita"),
    path("confirmacion/", views.confirmacion_agendada, name="confirmacion_agendada"),
    path("exportar_pdf/", views.exportar_pdf, name="exportar_pdf"),
]
