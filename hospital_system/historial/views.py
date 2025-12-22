from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'historial/index.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from citas.models import Cita
from usuarios.models import Usuario
from citas.forms import CitaForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Line
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from citas.forms import CitaForm


@login_required
def exportar_pdf(request):
    # Nombre personalizado del archivo
    nombre_archivo = f"citas_{request.user.last_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    # Configuración del documento
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        'titulo',
        parent=styles['Title'],
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=colors.HexColor("#2c3e50"),  # azul oscuro
        alignment=1,
        spaceAfter=10,
        leading=30
    )

    estilo_banner = ParagraphStyle(
        'banner',
        parent=styles['Normal'],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.white,
        alignment=1,
        spaceAfter=20
    )

    estilo_usuario = ParagraphStyle(
        'usuario',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12
    )

    estilo_footer = ParagraphStyle(
        'footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=1
    )

    # Título principal
    elements.append(Paragraph("HOSPITAL SYSTEM", estilo_titulo))

    # Banner rojo
    banner = Table([[Paragraph("Reporte de citas médicas", estilo_banner)]], colWidths=[460])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e74c3c")),  # rojo
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 20))

    # Línea decorativa
    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#95a5a6"), strokeWidth=1.5))
    elements.append(linea)
    elements.append(Spacer(1, 20))

    # Datos del usuario
    usuario = request.user
    datos_usuario = Paragraph(
        f"<b>Paciente:</b> {usuario.first_name} {usuario.last_name}<br/>"
        f"<b>Correo:</b> {usuario.email}",
        estilo_usuario
    )
    elements.append(datos_usuario)
    elements.append(Spacer(1, 15))

    # Citas
    citas = Cita.objects.filter(paciente=usuario).order_by('fecha')

    if not citas:
        elements.append(Paragraph("No tienes citas registradas.", styles['Normal']))
    else:
        data = [[
            Paragraph("<b>Fecha</b>", styles['Normal']),
            Paragraph("<b>Hora</b>", styles['Normal']),
            Paragraph("<b>Médico</b>", styles['Normal']),
            Paragraph("<b>Estado</b>", styles['Normal'])
        ]]

        for cita in citas:
            if cita.estado == "confirmada":
                estado = '<font color="green"><b>CONFIRMADA</b></font>'
            elif cita.estado == "pendiente":
                estado = '<font color="orange"><b>PENDIENTE</b></font>'
            else:
                estado = '<font color="red"><b>CANCELADA</b></font>'

            data.append([
                Paragraph(cita.fecha.strftime("%d/%m/%Y"), styles['Normal']),
                Paragraph(cita.hora.strftime("%H:%M"), styles['Normal']),
                Paragraph(f"{cita.medico.first_name} {cita.medico.last_name}", styles['Normal']),
                Paragraph(estado, styles['Normal'])
            ])

        table = Table(data, colWidths=[100, 80, 200, 120])
        estilo_tabla = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),  # azul
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 13),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.6, colors.grey),
        ])

        for i in range(1, len(data)):
            bg_color = colors.HexColor("#ecf0f1") if i % 2 == 0 else colors.HexColor("#dfe6e9")
            estilo_tabla.add('BACKGROUND', (0, i), (-1, i), bg_color)

        table.setStyle(estilo_tabla)
        elements.append(table)

    elements.append(Spacer(1, 30))

    # Línea decorativa antes del footer
    linea_footer = Drawing(500, 1)
    linea_footer.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#bdc3c7"), strokeWidth=0.5))
    elements.append(linea_footer)
    elements.append(Spacer(1, 10))

    # Pie de página
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    footer = Paragraph(
        f"Generado el {fecha_actual} | © Hospital System | Desarrollado por Iván",
        estilo_footer
    )
    elements.append(footer)

    doc.build(elements)
    return response

@login_required
@login_required
def agendar_cita(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        motivo = request.POST.get('motivo')
        medico_id = request.POST.get('medico')

        if not medico_id or not fecha or not hora or not motivo:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('citas:agendar_cita')

        try:
            medico_id = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            paciente = Usuario.objects.filter(es_medico=True)
            # Aquí podrías guardar la cita si tienes un modelo Cita
            messages.success(request, "Tu cita ha sido agendada con éxito.")
            return redirect('citas:confirmacion_agendada')
        except (ValueError, Usuario.DoesNotExist):
            messages.error(request, "Datos inválidos o médico no encontrado.")
            return redirect('citas:agendar_cita')

    # Método GET: mostrar formulario con médicos disponibles
    medicos = Usuario.objects.filter(es_medico=True)
    return render(request, 'citas/agendar_cita.html', {'medicos': medicos})

    paciente = request.user

    Cita.objects.create(
            paciente=paciente,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            medico=medico,
            estado='pendiente'
        )
    

    messages.success(request, "✅ Tu cita ha sido agendada con éxito.")
    return render(request, 'citas/confirmacion_agendada.html')

    # GET request: mostrar formulario
    medicos = Usuario.objects.filter(citas_como_medico__isnull=False).distinct()
    return render(request, 'citas/agendar_cita.html', {'medicos': medicos})

@login_required
def lista_citas(request):
    todas = Cita.objects.all()
    print("Todas las citas en DB:", todas)  # << debug
    citas = Cita.objects.filter(paciente=request.user).order_by('fecha')
    print("Citas filtradas por paciente:", citas)  # << debug
    return render(request, 'citas/lista_citas.html', {'citas': citas})

@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    medicos = Usuario.objects.filter(es_medico=True)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect('citas:lista_citas')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'citas/agendar_cita.html', {
        'form': form,
        'medicos': medicos
    })

@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    cita.delete()
    return redirect('citas:lista_citas')

@login_required
def citas_home(request):
    return render(request, 'citas/home.html')

def detalle_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    return render(request, 'citas/detalles.html', {'cita': cita})

def inicio(request):
    return render(request, 'citas/inicio.html')

def home(request):
    return render(request, 'citas/home.html')

def confirmacion_agendada(request):
    return render(request, 'citas/confirmacion_agendada.html')

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        motivo = request.POST.get('motivo')
        medico_id = request.POST.get('medico')

        if not medico_id or not fecha or not hora or not motivo:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('citas:agendar_cita')

        try:
            medico_id = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            paciente = Usuario.objects.filter(es_medico=True)
            # Aquí podrías guardar la cita si tienes un modelo Cita
            messages.success(request, "Tu cita ha sido agendada con éxito.")
            return redirect('citas:confirmacion_agendada')
        except (ValueError, Usuario.DoesNotExist):
            messages.error(request, "Datos inválidos o médico no encontrado.")
            return redirect('citas:agendar_cita')

    # Método GET: mostrar formulario con médicos disponibles
    medicos = Usuario.objects.filter(es_medico=True)
    return render(request, 'citas/agendar_cita.html', {'medicos': medicos})

    paciente = request.user

    Cita.objects.create(
            paciente=paciente,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            medico=medico,
            estado='pendiente'
        )
    

    messages.success(request, "✅ Tu cita ha sido agendada con éxito.")
    return render(request, 'citas/confirmacion_agendada.html')

    # GET request: mostrar formulario
    medicos = Usuario.objects.filter(citas_como_medico__isnull=False).distinct()
    return render(request, 'citas/agendar_cita.html', {'medicos': medicos})