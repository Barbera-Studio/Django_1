from django.urls import path, reverse_lazy
from . import views
from .views import login_view, registro_view, dashboard
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [
    path('', views.inicio, name='usuarios_index'),
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('inicio/', dashboard, name='inicio'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Recuperación de contraseña
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="usuarios/password_reset.html",
        email_template_name="usuarios/password_reset_email.txt", 
        html_email_template_name="usuarios/password_reset_email.html",  
        subject_template_name="usuarios/password_reset_subject.txt",
        success_url=reverse_lazy("usuarios:password_reset_done"),
    ), name="password_reset"),

    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(
        template_name="usuarios/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="usuarios/password_reset_confirm.html",
        success_url=reverse_lazy("usuarios:password_reset_complete")
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="usuarios/password_reset_complete.html"
    ), name="password_reset_complete"),
]

