# citas/views.py
from __future__ import annotations

from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Line
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .models import Cita
from .forms import CitaForm


# ---------- Utilidades ----------
def _actualizar_estados_citas_pasadas() -> None:
    """
    Sincroniza estados: marca como 'completada' toda cita 'pendiente'
    cuya fecha+hora (programada) ya haya llegado.
    """
    Cita.actualizar_estados_en_bloque()


# ---------- Vistas ----------
@login_required
def citas_home(request):
    """
    Página de inicio del módulo de citas.
    """
    return render(request, "citas/home.html")


@login_required
def agendar_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = request.user
            cita.estado = Cita.ESTADO_PENDIENTE
            cita.save()
            messages.success(request, "✅ Tu cita ha sido agendada con éxito.")
            return redirect("citas:confirmacion_agendada")
    else:
        form = CitaForm()

    return render(request, "citas/agendar_cita.html", {"form": form})


@login_required
def lista_citas(request):
    """
    Lista de citas del usuario:
    - Actualiza estados antes de mostrar.
    - Ordena por fecha y hora.
    """
    _actualizar_estados_citas_pasadas()
    citas = Cita.objects.filter(paciente=request.user).order_by("fecha", "hora")
    return render(request, "citas/lista_citas.html", {"citas": citas})


@login_required
def editar_cita(request, cita_id: int):
    """
    Editar cita existente:
    - Vuelve a validar que no quede en el pasado.
    """
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "La cita ha sido actualizada.")
            return redirect("citas:lista_citas")
        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = CitaForm(instance=cita)

    return render(request, "citas/agendar_cita.html", {"form": form})


@login_required
def cancelar_cita(request, cita_id: int):
    """
    Cancela una cita (no borra). Solo acepta POST.
    """
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if request.method == "POST":
        cita.estado = Cita.ESTADO_CANCELADA
        cita.save(update_fields=["estado"])
        messages.success(request, "La cita ha sido cancelada.")
    return redirect("citas:lista_citas")


@login_required
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id, paciente=request.user)

    if cita.estado not in [Cita.ESTADO_CANCELADA, Cita.ESTADO_COMPLETADA]:
        messages.error(request, "Solo puedes eliminar citas canceladas o completadas.")
        return redirect("citas:lista_citas")

    if request.method == "POST":
        cita.delete()
        messages.success(request, "La cita ha sido eliminada correctamente.")
        return redirect("citas:lista_citas")

    return render(request, "citas/confirmar_eliminar.html", {"cita": cita})



@login_required
def detalle_cita(request, cita_id: int):
    """
    Detalle de la cita.
    """
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    return render(request, "citas/detalles.html", {"cita": cita})


@login_required
def confirmacion_agendada(request):
    """
    Pantalla de confirmación tras agendar.
    """
    return render(request, "citas/confirmacion_agendada.html")


@login_required
def exportar_pdf(request):
    """
    Exporta a PDF las citas del usuario (tras actualizar estados).
    """
    _actualizar_estados_citas_pasadas()

    nombre_archivo = f"citas_{request.user.last_name or request.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40,
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilos
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=colors.HexColor("#2c3e50"),
        alignment=1,
        spaceAfter=10,
        leading=30,
    )
    estilo_banner = ParagraphStyle(
        "banner",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.white,
        alignment=1,
        spaceAfter=20,
    )
    estilo_usuario = ParagraphStyle(
        "usuario",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12,
    )
    estilo_footer = ParagraphStyle(
        "footer",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=1,
    )

    # Cabecera
    elements.append(Paragraph("HOSPITAL SYSTEM", estilo_titulo))
    banner = Table([[Paragraph("Reporte de citas médicas", estilo_banner)]], colWidths=[460])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e74c3c")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 20))

    # Línea separadora
    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#95a5a6"), strokeWidth=1.5))
    elements.append(linea)
    elements.append(Spacer(1, 20))

    # Usuario
    u = request.user
    nombre_visible = f"{u.first_name} {u.last_name}".strip() or u.username
    elements.append(Paragraph(f"<b>Paciente:</b> {nombre_visible}<br/><b>Correo:</b> {u.email}", estilo_usuario))
    elements.append(Spacer(1, 15))

    # Datos
    citas = Cita.objects.filter(paciente=u).order_by("fecha", "hora")
    if not citas.exists():
        elements.append(Paragraph("No tienes citas registradas.", styles["Normal"]))
    else:
        data = [[Paragraph("<b>Fecha</b>", styles["Normal"]),
                 Paragraph("<b>Hora</b>", styles["Normal"]),
                 Paragraph("<b>Médico</b>", styles["Normal"]),
                 Paragraph("<b>Estado</b>", styles["Normal"])]]

        for c in citas:
            color = {"completada": "green", "pendiente": "orange", "cancelada": "red"}[c.estado]
            medico_nombre = f"{c.medico.first_name} {c.medico.last_name}".strip() or c.medico.username
            data.append([
                Paragraph(c.fecha.strftime("%d/%m/%Y"), styles["Normal"]),
                Paragraph(c.hora.strftime("%H:%M"), styles["Normal"]),
                Paragraph(medico_nombre, styles["Normal"]),
                Paragraph(f'<font color="{color}"><b>{c.estado.upper()}</b></font>', styles["Normal"]),
            ])

        table = Table(data, colWidths=[100, 80, 200, 120])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 13),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
        ]))
        # Bandas alternas
        for i in range(1, len(data)):
            bg = colors.HexColor("#ecf0f1") if i % 2 == 0 else colors.HexColor("#dfe6e9")
            table.setStyle(TableStyle([("BACKGROUND", (0, i), (-1, i), bg)]))
        elements.append(table)

    elements.append(Spacer(1, 30))
    linea_footer = Drawing(500, 1)
    linea_footer.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#bdc3c7"), strokeWidth=0.5))
    elements.append(linea_footer)
    elements.append(Spacer(1, 10))

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Generado el {fecha_actual} | © Hospital System", estilo_footer))

    doc.build(elements)
    return response
