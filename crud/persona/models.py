from django.db import models

class Persona(models.Model):

    nombre = models.CharField(verbose_name="Nombre y apellido", max_length=50)
    edad = models.IntegerField(verbose_name="Edad")
    email = models.EmailField(verbose_name="correo Electronico", max_length=254, unique=True)
    class Meta:
        verbose_name = ("Persona")
        verbose_name_plural = ("Personas")
    def __str__(self):
        return f'{self.nombre} - {self.email}'

    def get_absolute_url(self):
        return reverse("Persona_detail", kwargs={"pk": self.pk})

