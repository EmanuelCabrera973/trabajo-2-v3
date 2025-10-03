import csv 
import sys
from django.db import transaction
from django.core.exceptions import ValidationError
from oficina.models import Oficina

def run(*args):
    if not args:
        print("Error: proporcionar ruta del archivo")
        print("uso:./manage.py runscript importar_oficinas --script-args <ruta del archivo>")
        sys.exit(1)
        
    csv_file = args[0]
    
    try:
        with open(csv_file,'r', encoding = 'utf8') as f:
            reader = csv.DictReader(f)
            oficinas_a_crear =[]
            
            for row in reader:
                nombre = row.get('nombre')
                nombre_corto=row.get('nombre_corto')
                
                if not nombre or not nombre_corto:
                    print(f"error en la fila{row}. falta un campo")
                    continue
                
                try:
                    oficina = Oficina(nombre=nombre, nombre_corto=nombre_corto)
                    oficina.full_clean()
                    oficinas_a_crear.append(oficina)
                except ValidationError as e:
                    print(f"Error de validación en la fila {row}. Detalle: {e}")
                except Exception as e:
                    print(f"Error inesperado en la fila {row}. Detalle: {e}")
                
            with transaction.atomic():
                Oficina.objects.bulk_create(oficinas_a_crear)
                print(f"importacion de {len(oficinas_a_crear)} oficinas completada exitosamente")
    
    except FileNotFoundError:
        print(f"Error no se encontro el el archivo {csv_file}")
    except:
        print(f"Ocurrio un erro inesperado en la importacion")
    
