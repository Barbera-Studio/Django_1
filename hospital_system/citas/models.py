from datetime import datetime

from django.db import models
from django.utils import timezone

from usuarios.models import Usuario


class Cita(models.Model):
    """
    Cita médica con fecha y hora separadas y tres estados:
    - pendiente: creada y aún no ha llegado la hora.
    - completada: llegó la fecha/hora programada.
    - cancelada: anulada por el usuario (no cambia automáticamente).
    """

    # Estados
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_COMPLETADA = "completada"
    ESTADO_CANCELADA = "cancelada"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_COMPLETADA, "Completada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    # Relaciones
    medico = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="citas_como_medico",
        help_text="Profesional que atenderá la cita (debe tener es_medico=True).",
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="citas_como_paciente",
        help_text="Usuario que solicita la cita.",
    )

    # Datos de la cita
    fecha = models.DateField(help_text="Fecha de la cita (YYYY-MM-DD).")
    hora = models.TimeField(help_text="Hora de la cita (HH:MM).")
    motivo = models.TextField(help_text="Breve descripción del motivo de la cita.")
    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        help_text="Estado actual de la cita.",
    )

    class Meta:
        ordering = ["fecha", "hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        indexes = [
            models.Index(fields=["paciente", "fecha", "hora"]),
            models.Index(fields=["medico", "fecha", "hora"]),
            models.Index(fields=["estado", "fecha", "hora"]),
        ]

    def __str__(self) -> str:
        paciente = f"{self.paciente.first_name} {self.paciente.last_name}".strip() or self.paciente.username
        medico = f"{self.medico.first_name} {self.medico.last_name}".strip() or self.medico.username
        return f"{paciente} con {medico} el {self.fecha} {self.hora} [{self.estado}]"

    @property
    def programada(self):
        """
        Devuelve la fecha y hora combinadas como datetime aware en la TZ del proyecto.
        Evita errores de comparación entre naive/aware.
        """
        naive = datetime.combine(self.fecha, self.hora)
        return timezone.make_aware(naive, timezone.get_current_timezone())

    def actualizar_estado_por_tiempo(self) -> None:
        """
        Marca la cita como completada si ya llegó su fecha/hora y sigue pendiente.
        """
        if self.estado == self.ESTADO_PENDIENTE and self.programada <= timezone.now():
            self.estado = self.ESTADO_COMPLETADA
            self.save(update_fields=["estado"])

    @staticmethod
    def actualizar_estados_en_bloque() -> None:
        """
        Actualiza todas las citas pendientes que ya han alcanzado su fecha/hora.
        Se ejecuta antes de listar o exportar, garantizando estados correctos.
        """
        ahora = timezone.now()
        # Iteración para usar programada (aware) y evitar divergencias por TZ.
        # Se actualiza con filtro por PK para evitar condiciones de carrera.
        for cita in Cita.objects.filter(estado=Cita.ESTADO_PENDIENTE):
            if cita.programada <= ahora:
                Cita.objects.filter(pk=cita.pk, estado=Cita.ESTADO_PENDIENTE).update(estado=Cita.ESTADO_COMPLETADA)
