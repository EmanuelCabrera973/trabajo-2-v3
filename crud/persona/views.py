from django.shortcuts import render
from django.views.generic import ListView
from .models import Persona

class PersonaListView(ListView):
    model = Persona
    template_name = "persona/lista.html"
    context_object_name = "personas"
    