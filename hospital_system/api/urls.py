from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Ejemplo de endpoint API
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('citas/', include('citas.urls')),
    path('home/', views.home, name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
]