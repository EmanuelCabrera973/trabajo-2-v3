from django.shortcuts import render

#CBV for singup view
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sing up'
        return context

class LogoutMessageView(TemplateView):
    template_name = 'accounts/logout_message.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'cerrar sesion'
        return context
# Create your views here.
