from django.db import models
from django.core.exceptions import ValidationError

def validate_nombre_corto(value):
    if not value.isupper():
        raise ValidationError("el nombre corto debe estar en mayusculas")
# Create your models here.
class Oficina(models.Model):
    """model definicion de oficina"""
    nombre=models.CharField(verbose_name="nombre de la oficina",
    max_length= 50, unique=True)
    nombre_corto = models.CharField(verbose_name = "id corto", max_length=10, unique=True,
                                    help_text="Codigo corto unico. (ej: PER,ADM,etc)",
    validators= [validate_nombre_corto],
    )
    
    class Meta:
        """meta definicion for oficina"""
        verbose_name = "Oficina"
        verbose_name_plural = "oficinas"
    def __str__(self):
        return  f'{self.nombre} - ({self.nombre_corto})'
    