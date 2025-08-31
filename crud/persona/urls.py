from django.urls import path
from .views import *

app_name = 'persona'

urlpatterns = [
    path('lista/',
        PersonaListView.as_view(),
        name='lista',
    ),
    path (
        'detalle/<int:pk>/',
        PersonaDetailView.as_view(),
        name='detalle',
    ),
    path (
        'crear/',
        PersonaCreateView.as_view(),
        name='crear',
    ),
    path (
        'editar/<int:pk>/',
        PersonaUpdateView.as_view(),
        name='editar',
    ),
    path(
        'eliminar/<int:pk>/',
        DeletePersonaView.as_view(),
        name='eliminar',
    ),
    path(
        'buscar/',
        PersonaSearchView.as_view(),
        name='buscar',
    ),
]