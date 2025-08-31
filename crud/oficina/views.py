from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Oficina
#import login mixin
from django.contrib.auth.mixins import LoginRequiredMixin


class OficinaListView(ListView):
    model = Oficina
    template_name = "oficina/lista.html"
    context_object_name = "oficinas"
    paginate_by = 10
    
class OficinaDetailView(DetailView):
    model = Oficina
    template_name = "oficina/detalle.html"
    context_object_name = "oficinas"
    
class OficinaCreateView(LoginRequiredMixin, CreateView):
    model = Oficina
    template_name = "oficina/crear.html"
    fields = ['nombre', 'nombre_corto']
    success_url = reverse_lazy('oficina:lista')
    
class OficinaUpdateView(LoginRequiredMixin, UpdateView):
    model = Oficina
    template_name = "oficina/editar.html"
    fields = ['nombre', 'nombre_corto']
    success_url = reverse_lazy('oficina:lista')
    
class OficinaDeleteView(LoginRequiredMixin, DeleteView):
    model = Oficina
    template_name = "oficina/eliminar.html"
    context_object_name = "oficinas"
    success_url = reverse_lazy('oficina:lista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Eliminar Oficina'
        return context

class OficinaSearchView(ListView):
    model = Oficina
    template_name = "oficina/buscar.html"
    context_object_name = "oficinas"
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Oficina.objects.filter(nombre__icontains=query)
        else:
            return Oficina.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context