from django.urls import path
from .views import *

app_name = 'oficina'

urlpatterns = [
    path('lista/',
        OficinaListView.as_view(),
        name='lista',
    ),
    path (
        'detalle/<int:pk>/',
        OficinaDetailView.as_view(),
        name='detalle',
    ),
    path (
        'crear/',
        OficinaCreateView.as_view(),
        name='crear',
    ),
    path (
        'editar/<int:pk>/',
        OficinaUpdateView.as_view(),
        name='editar',
    ),
    path(
        'eliminar/<int:pk>/',
        OficinaDeleteView.as_view(),
        name='eliminar',
    ),
    path(
        'buscar/',
        OficinaSearchView.as_view(),
        name='buscar',
    ),
]