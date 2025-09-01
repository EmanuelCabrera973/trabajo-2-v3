from django.db import models
from oficina.models import Oficina


class Persona(models.Model):
    
    edad = models.IntegerField(verbose_name="Edad")
    email = models.EmailField(verbose_name="correo Electronico", max_length=254, unique=True)
    nombre = models.CharField(verbose_name="Nombre y apellido", max_length=50)
    oficina = models.ForeignKey(
        Oficina,
        verbose_name="oficina asignada",
        on_delete=models.SET_NULL,
        related_name="personas",
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = ("persona")
        verbose_name_plural = ("personas")
    def __str__(self):
        return f'{self.nombre} - {self.email}'

    def get_absolute_url(self):
        return reverse("persona_detail", kwargs={"pk": self.pk})

